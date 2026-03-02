"""
One-time script to add an admin user to the database.

Run from project root (task_manager_api):
    python scripts/create_admin.py

Default admin:
    Email:    admin@example.com
    Password: Admin@1234

Change ADMIN_EMAIL and ADMIN_PASSWORD below if you want different credentials.
"""
import asyncio
import sys
from pathlib import Path

# Ensure project root is on path when running as: python scripts/create_admin.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.routers.auth import hash_password


ADMIN_EMAIL = "admin@example.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@1234"


async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()
        if existing:
            if existing.role == UserRole.admin:
                print(f"Admin already exists: {ADMIN_EMAIL}")
                return
            existing.role = UserRole.admin
            await session.commit()
            print(f"Updated user to admin: {ADMIN_EMAIL}")
            return

        hashed = hash_password(ADMIN_PASSWORD)
        admin = User(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            hashed_password=hashed,
            role=UserRole.admin,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
