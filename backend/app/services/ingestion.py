import csv
import io
import json
from datetime import datetime
from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.dataset import DatasetUpload
from app.models.record import TransactionRecord
from app.models.violation import Violation
from app.models.rule import ComplianceRule
from app.services.rules_engine import RulesEngine, DEFAULT_RULES

REQUIRED_HEADERS = {
    "transaction_id",
    "account_id",
    "amount",
}

def parse_iso_datetime(dt_str: str) -> datetime | None:
    if not dt_str or not dt_str.strip():
        return None
    cleaned = dt_str.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except Exception:
        try:
            return datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

def process_csv_upload(
    db: Session,
    file_content: bytes,
    filename: str,
    tenant_id: str,
    uploaded_by_id: str | None = None
) -> Tuple[DatasetUpload, int, int]:
    """
    Parses and ingests a CSV dataset, validates schema and data types,
    evaluates active deterministic compliance rules, and persists records
    and violations scoped to the tenant.
    """
    text_stream = io.StringIO(file_content.decode("utf-8-sig"))
    reader = csv.DictReader(text_stream)

    if not reader.fieldnames:
        raise ValueError("Uploaded CSV file is empty or has invalid formatting.")

    normalized_headers = {h.strip().lower() for h in reader.fieldnames if h}
    missing = REQUIRED_HEADERS - normalized_headers
    if missing:
        raise ValueError(f"CSV missing mandatory columns: {', '.join(missing)}")

    # Create dataset record
    dataset = DatasetUpload(
        tenant_id=tenant_id,
        filename=filename,
        file_size_bytes=len(file_content),
        row_count=0,
        violation_count=0,
        status="PROCESSING",
        uploaded_by_id=uploaded_by_id
    )
    db.add(dataset)
    db.flush()

    records_to_insert: List[TransactionRecord] = []
    
    for row_idx, row in enumerate(reader, start=1):
        cleaned_row = {k.strip().lower(): v.strip() if v else "" for k, v in row.items() if k}
        
        txn_id = cleaned_row.get("transaction_id") or f"TXN-{row_idx}"
        acct_id = cleaned_row.get("account_id") or "UNKNOWN"
        raw_amt = cleaned_row.get("amount", "0")
        try:
            amount = float(raw_amt.replace(",", "").replace("$", ""))
        except ValueError:
            amount = 0.0

        currency = cleaned_row.get("currency", "USD").upper() or "USD"
        cp_name = cleaned_row.get("counterparty_name") or None
        cp_country = (cleaned_row.get("counterparty_country") or "").upper() or None
        kyc = (cleaned_row.get("kyc_status") or "VERIFIED").upper()
        txn_type = (cleaned_row.get("transaction_type") or "TRANSFER").upper()
        timestamp = parse_iso_datetime(cleaned_row.get("timestamp", ""))

        record = TransactionRecord(
            tenant_id=tenant_id,
            dataset_id=dataset.id,
            transaction_id=txn_id,
            account_id=acct_id,
            counterparty_name=cp_name,
            counterparty_country=cp_country,
            amount=amount,
            currency=currency,
            timestamp=timestamp,
            kyc_status=kyc,
            transaction_type=txn_type,
            raw_data=json.dumps(cleaned_row)
        )
        records_to_insert.append(record)

    db.add_all(records_to_insert)
    db.flush()

    # Retrieve active rules for tenant (or system defaults)
    active_rules = db.query(ComplianceRule).filter(
        (ComplianceRule.tenant_id == tenant_id) | (ComplianceRule.tenant_id == None),
        ComplianceRule.is_active == True
    ).all()

    # If no rules exist for this tenant, check if tenant-specific rules should be cloned or default rules used
    if not active_rules:
        created_defaults = []
        for r_def in DEFAULT_RULES:
            existing = db.query(ComplianceRule).filter(
                ComplianceRule.tenant_id == tenant_id,
                ComplianceRule.code == r_def["code"]
            ).first()
            if not existing:
                rule_obj = ComplianceRule(
                    tenant_id=tenant_id,
                    code=r_def["code"],
                    name=r_def["name"],
                    description=r_def["description"],
                    category=r_def["category"],
                    severity=r_def["severity"],
                    regulatory_framework=r_def["regulatory_framework"],
                    parameters_json=r_def["parameters_json"],
                    is_active=r_def["is_active"]
                )
                db.add(rule_obj)
                created_defaults.append(rule_obj)
            else:
                created_defaults.append(existing)
        db.flush()
        active_rules = created_defaults

    # Run deterministic rules evaluation
    engine = RulesEngine(active_rules)
    flagged_violations_data = engine.evaluate_batch(records_to_insert, tenant_id, dataset.id)

    violations_to_insert = [
        Violation(
            tenant_id=v["tenant_id"],
            dataset_id=v["dataset_id"],
            record_id=v["record_id"],
            rule_code=v["rule_code"],
            rule_name=v["rule_name"],
            severity=v["severity"],
            message=v["message"],
            details_json=v["details_json"],
            status="OPEN"
        )
        for v in flagged_violations_data
    ]

    db.add_all(violations_to_insert)

    dataset.row_count = len(records_to_insert)
    dataset.violation_count = len(violations_to_insert)
    dataset.status = "COMPLETED"

    db.commit()
    db.refresh(dataset)

    return dataset, dataset.row_count, dataset.violation_count
