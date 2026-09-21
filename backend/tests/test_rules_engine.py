import pytest
from datetime import datetime, timezone
from app.models.record import TransactionRecord
from app.models.rule import ComplianceRule
from app.services.rules_engine import RulesEngine, DEFAULT_RULES

@pytest.fixture
def mock_rules():
    return [
        ComplianceRule(
            id=f"rule-{i}",
            code=r["code"],
            name=r["name"],
            description=r["description"],
            category=r["category"],
            severity=r["severity"],
            regulatory_framework=r["regulatory_framework"],
            parameters_json=r["parameters_json"],
            is_active=True
        )
        for i, r in enumerate(DEFAULT_RULES)
    ]

def test_aml_high_value_rule(mock_rules):
    engine = RulesEngine(mock_rules)
    rec_high = TransactionRecord(
        id="rec-1",
        tenant_id="tenant-1",
        dataset_id="ds-1",
        transaction_id="TXN-HIGH",
        account_id="ACC-01",
        amount=15000.0,
        currency="USD",
        kyc_status="VERIFIED",
        counterparty_country="USA",
        timestamp=datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    )
    violations = engine.evaluate_batch([rec_high], "tenant-1", "ds-1")
    rule_codes = [v["rule_code"] for v in violations]
    assert "RULE-AML-001" in rule_codes

def test_sanctions_rule(mock_rules):
    engine = RulesEngine(mock_rules)
    rec_sanctioned = TransactionRecord(
        id="rec-2",
        tenant_id="tenant-1",
        dataset_id="ds-1",
        transaction_id="TXN-SANCTION",
        account_id="ACC-02",
        amount=500.0,
        currency="USD",
        kyc_status="VERIFIED",
        counterparty_country="PRK", # North Korea
        timestamp=datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    )
    violations = engine.evaluate_batch([rec_sanctioned], "tenant-1", "ds-1")
    rule_codes = [v["rule_code"] for v in violations]
    assert "RULE-SANCTIONS-001" in rule_codes
    assert any(v["severity"] == "CRITICAL" for v in violations)

def test_kyc_unverified_rule(mock_rules):
    engine = RulesEngine(mock_rules)
    rec_kyc = TransactionRecord(
        id="rec-3",
        tenant_id="tenant-1",
        dataset_id="ds-1",
        transaction_id="TXN-KYC",
        account_id="ACC-03",
        amount=2500.0,
        currency="USD",
        kyc_status="UNVERIFIED",
        counterparty_country="USA",
        timestamp=datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    )
    violations = engine.evaluate_batch([rec_kyc], "tenant-1", "ds-1")
    rule_codes = [v["rule_code"] for v in violations]
    assert "RULE-KYC-001" in rule_codes

def test_structuring_rule(mock_rules):
    engine = RulesEngine(mock_rules)
    rec_struct = TransactionRecord(
        id="rec-4",
        tenant_id="tenant-1",
        dataset_id="ds-1",
        transaction_id="TXN-STRUCT",
        account_id="ACC-04",
        amount=9850.0,
        currency="USD",
        kyc_status="VERIFIED",
        counterparty_country="USA",
        timestamp=datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    )
    violations = engine.evaluate_batch([rec_struct], "tenant-1", "ds-1")
    rule_codes = [v["rule_code"] for v in violations]
    assert "RULE-STRUCTURING-001" in rule_codes

def test_compliant_record_no_violations(mock_rules):
    engine = RulesEngine(mock_rules)
    rec_clean = TransactionRecord(
        id="rec-5",
        tenant_id="tenant-1",
        dataset_id="ds-1",
        transaction_id="TXN-CLEAN",
        account_id="ACC-05",
        amount=450.0,
        currency="USD",
        kyc_status="VERIFIED",
        counterparty_country="USA",
        timestamp=datetime(2026, 9, 20, 14, 0, tzinfo=timezone.utc)
    )
    violations = engine.evaluate_batch([rec_clean], "tenant-1", "ds-1")
    assert len(violations) == 0
