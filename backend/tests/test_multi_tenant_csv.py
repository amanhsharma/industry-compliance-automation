import io
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base
from app.models.tenant import Tenant
from app.services.ingestion import process_csv_upload

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_multi_tenant_csv_ingestion_no_unique_constraint_error():
    db = TestingSessionLocal()

    # Create two tenants
    t1 = Tenant(name="Tenant 1", slug="t1")
    t2 = Tenant(name="Tenant 2", slug="t2")
    db.add_all([t1, t2])
    db.commit()

    sample_csv = b"""transaction_id,account_id,amount,currency,counterparty_country,kyc_status
TXN-101,ACC-1,15000.00,USD,USA,VERIFIED
TXN-102,ACC-2,500.00,USD,PRK,VERIFIED"""

    # Ingest for Tenant 1
    ds1, rows1, vios1 = process_csv_upload(db, sample_csv, "t1.csv", t1.id)
    assert rows1 == 2
    assert vios1 == 2

    # Ingest for Tenant 2 (This used to fail with UNIQUE constraint failed: compliance_rules.code)
    ds2, rows2, vios2 = process_csv_upload(db, sample_csv, "t2.csv", t2.id)
    assert rows2 == 2
    assert vios2 == 2
