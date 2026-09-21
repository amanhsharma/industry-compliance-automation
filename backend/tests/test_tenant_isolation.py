import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.tenant import Tenant
from app.models.user import User
from app.models.dataset import DatasetUpload
from app.models.record import TransactionRecord
from app.models.violation import Violation

# In-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_multi_tenant_isolation():
    client = TestClient(app)
    db = TestingSessionLocal()

    # Create Tenant A and Tenant B
    tenant_a = Tenant(name="Tenant Alpha", slug="tenant-alpha")
    tenant_b = Tenant(name="Tenant Beta", slug="tenant-beta")
    db.add_all([tenant_a, tenant_b])
    db.flush()

    user_a = User(
        tenant_id=tenant_a.id,
        email="alpha@test.com",
        hashed_password=hash_password("password123"),
        full_name="Alpha Officer",
        role="compliance_officer"
    )
    user_b = User(
        tenant_id=tenant_b.id,
        email="beta@test.com",
        hashed_password=hash_password("password123"),
        full_name="Beta Officer",
        role="compliance_officer"
    )
    db.add_all([user_a, user_b])
    db.flush()

    # Create dataset & violation for Tenant A
    ds_a = DatasetUpload(
        tenant_id=tenant_a.id,
        filename="alpha_records.csv",
        row_count=1,
        violation_count=1,
        status="COMPLETED"
    )
    db.add(ds_a)
    db.flush()

    rec_a = TransactionRecord(
        tenant_id=tenant_a.id,
        dataset_id=ds_a.id,
        transaction_id="TXN-A1",
        account_id="ACC-A1",
        amount=50000.0,
        currency="USD"
    )
    db.add(rec_a)
    db.flush()

    vio_a = Violation(
        tenant_id=tenant_a.id,
        dataset_id=ds_a.id,
        record_id=rec_a.id,
        rule_code="RULE-AML-001",
        rule_name="AML High-Value CTR Threshold",
        severity="HIGH",
        status="OPEN",
        message="Alpha violation message"
    )
    db.add(vio_a)
    db.commit()

    # Generate token for User B
    token_b = create_access_token(user_b.id)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B queries violations -> should receive empty list (cannot see Tenant A's violation)
    res_vio = client.get("/api/violations", headers=headers_b)
    assert res_vio.status_code == 200
    assert len(res_vio.json()) == 0

    # User B attempts to access Tenant A's specific violation -> 404 Not Found
    res_direct = client.get(f"/api/violations/{vio_a.id}", headers=headers_b)
    assert res_direct.status_code == 404

    # User B queries datasets -> should receive empty list
    res_ds = client.get("/api/datasets", headers=headers_b)
    assert res_ds.status_code == 200
    assert len(res_ds.json()) == 0

    # User A queries violations -> should see their violation
    token_a = create_access_token(user_a.id)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res_a_vio = client.get("/api/violations", headers=headers_a)
    assert res_a_vio.status_code == 200
    assert len(res_a_vio.json()) == 1
    assert res_a_vio.json()[0]["id"] == vio_a.id
