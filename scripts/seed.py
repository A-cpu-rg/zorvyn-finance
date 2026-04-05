import sys
from pathlib import Path
from datetime import date, timedelta
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionType
from app.core.security import hash_password

def seed_db():
    print("Seeding database...")
    db = SessionLocal()

    # Clear existing data for a fresh seed (Optional)
    # Caution: This will truncate your data!
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)

    # 1. Create Users
    if not db.query(User).filter_by(email="admin@zorvyn.com").first():
        admin = User(
            name="Admin User",
            email="admin@zorvyn.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin)
        print("Created admin user.")

    if not db.query(User).filter_by(email="analyst@zorvyn.com").first():
        analyst = User(
            name="Analyst User",
            email="analyst@zorvyn.com",
            hashed_password=hash_password("analyst123"),
            role=UserRole.ANALYST
        )
        db.add(analyst)
        print("Created analyst user.")

    if not db.query(User).filter_by(email="viewer@zorvyn.com").first():
        viewer = User(
            name="Viewer User",
            email="viewer@zorvyn.com",
            hashed_password=hash_password("viewer123"),
            role=UserRole.VIEWER
        )
        db.add(viewer)
        print("Created viewer user.")

    db.commit()

    admin_user = db.query(User).filter_by(email="admin@zorvyn.com").first()

    # 2. Create Transactions
    if db.query(Transaction).count() < 10:
        categories = {
            TransactionType.INCOME: ["Salary", "Freelance", "Investment", "Gift"],
            TransactionType.EXPENSE: ["Rent", "Groceries", "Utilities", "Entertainment", "Travel"]
        }
        
        today = date.today()
        for i in range(30):
            tx_type = random.choice([TransactionType.INCOME, TransactionType.EXPENSE])
            category = random.choice(categories[tx_type])
            amount = round(random.uniform(50, 5000), 2)
            # Random date within the last 60 days
            tx_date = today - timedelta(days=random.randint(0, 60))

            tx = Transaction(
                amount=amount,
                type=tx_type,
                category=category,
                date=tx_date,
                notes=f"Sample {tx_type.value} transaction for {category}",
                created_by=admin_user.id
            )
            db.add(tx)
        
        db.commit()
        print("Seeded 30 sample transactions.")
    else:
        print("Transactions already exist. Skipping transaction seeding.")

    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_db()
