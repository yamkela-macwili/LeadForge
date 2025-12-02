from database import get_db, User
from auth import get_password_hash

def seed_free_user():
    db = next(get_db())
    try:
        email = "free@leadforge.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating user {email}...")
            user = User(
                email=email,
                hashed_password=get_password_hash("password"),
                is_active=1,
                is_superuser=0,
                subscription_tier="Free",
                credits=0
            )
            db.add(user)
            db.commit()
            print(f"User {email} created successfully.")
        else:
            print(f"User {email} already exists.")
    except Exception as e:
        print(f"Error seeding user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_free_user()
