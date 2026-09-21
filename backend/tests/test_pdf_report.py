from app.services.pdf_generator import generate_compliance_pdf_report

def test_pdf_report_generation():
    summary_data = {
        "compliance_score": 92.5,
        "total_records": 250,
        "total_violations": 18,
        "open_violations": 5
    }
    violations_data = [
        {
            "transaction_id": "TXN-901",
            "rule_code": "RULE-AML-001",
            "rule_name": "AML High-Value CTR Threshold",
            "severity": "HIGH",
            "status": "OPEN",
            "message": "Transaction of $25,000 exceeds CTR threshold"
        },
        {
            "transaction_id": "TXN-902",
            "rule_code": "RULE-SANCTIONS-001",
            "rule_name": "OFAC Sanctions Check",
            "severity": "CRITICAL",
            "status": "OPEN",
            "message": "Counterparty country matches sanctioned list"
        }
    ]

    pdf_bytes = generate_compliance_pdf_report(
        tenant_name="Meridian Test Tenant",
        summary_data=summary_data,
        violations_data=violations_data
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
