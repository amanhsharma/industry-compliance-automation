import os
import sys
import json
from pathlib import Path

# Add parent directory to sys.path so app can be imported
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal, Base, engine
from app.models.tenant import Tenant
from app.models.user import User
from app.models.rule import ComplianceRule
from app.core.security import hash_password
from app.services.rules_engine import DEFAULT_RULES
from app.services.ingestion import process_csv_upload

def seed_database():
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if demo tenant exists
        tenant = db.query(Tenant).filter(Tenant.slug == "meridian-financial").first()
        if not tenant:
            print("Creating default demo tenant: Meridian Financial Services...")
            tenant = Tenant(
                name="Meridian Financial Services",
                slug="meridian-financial"
            )
            db.add(tenant)
            db.flush()
        else:
            print(f"Demo tenant '{tenant.name}' already exists.")

        # Seed Admin User
        admin_user = db.query(User).filter(User.email == "admin@meridian.com").first()
        if not admin_user:
            print("Creating demo admin user (admin@meridian.com / admin123)...")
            admin_user = User(
                tenant_id=tenant.id,
                email="admin@meridian.com",
                hashed_password=hash_password("admin123"),
                full_name="Sarah Jenkins (Lead Compliance)",
                role="admin"
            )
            db.add(admin_user)
            db.flush()

        # Seed Officer User
        officer_user = db.query(User).filter(User.email == "compliance@meridian.com").first()
        if not officer_user:
            print("Creating demo officer user (compliance@meridian.com / officer123)...")
            officer_user = User(
                tenant_id=tenant.id,
                email="compliance@meridian.com",
                hashed_password=hash_password("officer123"),
                full_name="David Vance (Senior Analyst)",
                role="compliance_officer"
            )
            db.add(officer_user)
            db.flush()

        # Seed Compliance Rules
        for r_data in DEFAULT_RULES:
            existing_rule = db.query(ComplianceRule).filter(
                ComplianceRule.code == r_data["code"],
                (ComplianceRule.tenant_id == tenant.id) | (ComplianceRule.tenant_id == None)
            ).first()
            if not existing_rule:
                print(f"Creating default rule: {r_data['code']} - {r_data['name']}...")
                rule = ComplianceRule(
                    tenant_id=tenant.id,
                    code=r_data["code"],
                    name=r_data["name"],
                    description=r_data["description"],
                    category=r_data["category"],
                    severity=r_data["severity"],
                    regulatory_framework=r_data["regulatory_framework"],
                    parameters_json=r_data["parameters_json"],
                    is_active=r_data["is_active"]
                )
                db.add(rule)

        db.commit()

        # Ingest sample dataset if transactions_sample.csv exists
        sample_path = Path(__file__).parent.parent / "sample_data" / "transactions_sample.csv"
        if sample_path.exists():
            print(f"Ingesting initial sample dataset from {sample_path.name}...")
            with open(sample_path, "rb") as f:
                content = f.read()
            dataset, rows, violations = process_csv_upload(
                db=db,
                file_content=content,
                filename="transactions_sample.csv",
                tenant_id=tenant.id,
                uploaded_by_id=admin_user.id
            )
            print(f"Successfully ingested sample: {rows} transactions, {violations} violations detected.")

        print("\nSeed completed successfully!")
        print("Demo Credentials:")
        print("  Admin:     admin@meridian.com / admin123")
        print("  Officer:   compliance@meridian.com / officer123")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
