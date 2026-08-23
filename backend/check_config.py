from app.config import settings

print("DB URL:", settings.database_url)
print("Secret key loaded:", bool(settings.secret_key))