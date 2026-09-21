import json
from datetime import datetime
from typing import List, Dict, Any
from app.models.record import TransactionRecord
from app.models.rule import ComplianceRule

DEFAULT_RULES = [
    {
        "code": "RULE-AML-001",
        "name": "AML High-Value CTR Threshold",
        "description": "Flags transactions exceeding the mandatory Bank Secrecy Act Currency Transaction Report (CTR) threshold of $10,000 USD.",
        "category": "AML",
        "severity": "HIGH",
        "regulatory_framework": "BSA 31 CFR § 1010.311",
        "parameters_json": json.dumps({"threshold_amount": 10000.0, "currency": "USD"}),
        "is_active": True
    },
    {
        "code": "RULE-SANCTIONS-001",
        "name": "OFAC Sanctioned Jurisdiction Embargo",
        "description": "Flags counterparties located in OFAC comprehensive embargoed or high-risk jurisdictions.",
        "category": "SANCTIONS",
        "severity": "CRITICAL",
        "regulatory_framework": "OFAC Sanctions Programs / Patriot Act § 311",
        "parameters_json": json.dumps({"embargoed_countries": ["PRK", "IRN", "SYR", "CUB", "RUS"]}),
        "is_active": True
    },
    {
        "code": "RULE-KYC-001",
        "name": "Unverified Customer Transaction Limit",
        "description": "Prohibits outbound transaction volume exceeding $1,000 USD for customer accounts lacking verified KYC documentation.",
        "category": "KYC",
        "severity": "HIGH",
        "regulatory_framework": "FinCEN Customer Due Diligence (CDD) Rule",
        "parameters_json": json.dumps({"unverified_threshold": 1000.0}),
        "is_active": True
    },
    {
        "code": "RULE-STRUCTURING-001",
        "name": "Anti-Structuring / Smurfing Threshold Detection",
        "description": "Detects transactions falling deliberately between $9,000 and $9,999 designed to circumvent the $10,000 reporting threshold.",
        "category": "VELOCITY",
        "severity": "CRITICAL",
        "regulatory_framework": "31 U.S. Code § 5324",
        "parameters_json": json.dumps({"min_bound": 9000.0, "max_bound": 9999.99}),
        "is_active": True
    },
    {
        "code": "RULE-TIMING-001",
        "name": "Off-Hours High-Risk Outbound Transfer",
        "description": "Flags high-value outbound wire transfers initiated between 01:00 and 05:00 UTC without prior multi-factor pre-clearance.",
        "category": "FRAUD",
        "severity": "MEDIUM",
        "regulatory_framework": "FFIEC IT Examination Guidelines",
        "parameters_json": json.dumps({"start_hour": 1, "end_hour": 5, "min_amount": 5000.0}),
        "is_active": True
    }
]

class RulesEngine:
    def __init__(self, active_rules: List[ComplianceRule]):
        # Map rule codes to rules for rapid lookup
        self.rules_by_code = {rule.code: rule for rule in active_rules if rule.is_active}

    def evaluate_batch(self, records: List[TransactionRecord], tenant_id: str, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Deterministic rule evaluation pipeline. Evaluates every record against
        active compliance rules, accumulating deterministic violation events.
        """
        violations = []

        for record in records:
            amount = float(record.amount)
            country = (record.counterparty_country or "").strip().upper()
            kyc = (record.kyc_status or "").strip().upper()
            record_time = record.timestamp

            # Rule evaluation: RULE-AML-001 (CTR threshold)
            rule_aml = self.rules_by_code.get("RULE-AML-001")
            if rule_aml:
                params = json.loads(rule_aml.parameters_json or "{}")
                threshold = params.get("threshold_amount", 10000.0)
                if amount >= threshold:
                    violations.append({
                        "tenant_id": tenant_id,
                        "dataset_id": dataset_id,
                        "record_id": record.id,
                        "rule_code": rule_aml.code,
                        "rule_name": rule_aml.name,
                        "severity": rule_aml.severity,
                        "message": f"Transaction of {amount:,.2f} {record.currency} exceeds the ${threshold:,.2f} AML reporting threshold.",
                        "details_json": json.dumps({
                            "threshold": threshold,
                            "actual_amount": amount,
                            "currency": record.currency,
                            "regulatory_framework": rule_aml.regulatory_framework
                        })
                    })

            # Rule evaluation: RULE-SANCTIONS-001 (Embargoed jurisdiction)
            rule_sanctions = self.rules_by_code.get("RULE-SANCTIONS-001")
            if rule_sanctions:
                params = json.loads(rule_sanctions.parameters_json or "{}")
                embargoed = params.get("embargoed_countries", ["PRK", "IRN", "SYR", "CUB", "RUS"])
                if country in embargoed:
                    violations.append({
                        "tenant_id": tenant_id,
                        "dataset_id": dataset_id,
                        "record_id": record.id,
                        "rule_code": rule_sanctions.code,
                        "rule_name": rule_sanctions.name,
                        "severity": rule_sanctions.severity,
                        "message": f"Counterparty country '{country}' matches high-risk/sanctioned jurisdiction list under OFAC sanctions.",
                        "details_json": json.dumps({
                            "matched_country": country,
                            "counterparty_name": record.counterparty_name,
                            "regulatory_framework": rule_sanctions.regulatory_framework
                        })
                    })

            # Rule evaluation: RULE-KYC-001 (Unverified customer limit)
            rule_kyc = self.rules_by_code.get("RULE-KYC-001")
            if rule_kyc:
                params = json.loads(rule_kyc.parameters_json or "{}")
                limit = params.get("unverified_threshold", 1000.0)
                if kyc in ("UNVERIFIED", "PENDING") and amount > limit:
                    violations.append({
                        "tenant_id": tenant_id,
                        "dataset_id": dataset_id,
                        "record_id": record.id,
                        "rule_code": rule_kyc.code,
                        "rule_name": rule_kyc.name,
                        "severity": rule_kyc.severity,
                        "message": f"Unverified account ({kyc}) performed a transaction of {amount:,.2f} {record.currency} exceeding the ${limit:,.2f} KYC ceiling.",
                        "details_json": json.dumps({
                            "kyc_status": kyc,
                            "amount": amount,
                            "limit": limit,
                            "account_id": record.account_id
                        })
                    })

            # Rule evaluation: RULE-STRUCTURING-001 (Deliberate threshold evasion)
            rule_structuring = self.rules_by_code.get("RULE-STRUCTURING-001")
            if rule_structuring:
                params = json.loads(rule_structuring.parameters_json or "{}")
                min_b = params.get("min_bound", 9000.0)
                max_b = params.get("max_bound", 9999.99)
                if min_b <= amount <= max_b:
                    violations.append({
                        "tenant_id": tenant_id,
                        "dataset_id": dataset_id,
                        "record_id": record.id,
                        "rule_code": rule_structuring.code,
                        "rule_name": rule_structuring.name,
                        "severity": rule_structuring.severity,
                        "message": f"Transaction of {amount:,.2f} {record.currency} falls within suspicious anti-structuring boundary ($9,000 - $9,999).",
                        "details_json": json.dumps({
                            "amount": amount,
                            "boundary": [min_b, max_b],
                            "account_id": record.account_id,
                            "regulatory_framework": rule_structuring.regulatory_framework
                        })
                    })

            # Rule evaluation: RULE-TIMING-001 (Off-hours high-risk wire)
            rule_timing = self.rules_by_code.get("RULE-TIMING-001")
            if rule_timing and record_time:
                params = json.loads(rule_timing.parameters_json or "{}")
                start_h = params.get("start_hour", 1)
                end_h = params.get("end_hour", 5)
                min_amt = params.get("min_amount", 5000.0)
                
                # Non-obvious rule evaluation: Off-hours flag checks if hour falls into restricted window
                if start_h <= record_time.hour <= end_h and amount >= min_amt:
                    violations.append({
                        "tenant_id": tenant_id,
                        "dataset_id": dataset_id,
                        "record_id": record.id,
                        "rule_code": rule_timing.code,
                        "rule_name": rule_timing.name,
                        "severity": rule_timing.severity,
                        "message": f"High-value outbound wire ({amount:,.2f} {record.currency}) initiated during off-hours ({record_time.strftime('%H:%M')} UTC).",
                        "details_json": json.dumps({
                            "hour": record_time.hour,
                            "timestamp": record_time.isoformat(),
                            "amount": amount
                        })
                    })

        return violations
