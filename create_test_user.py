from database import SessionLocal, User
from auth import get_password_hash

db = SessionLocal()

# Create a Free tier user
free_user = User(
    email="free@test.com",
    hashed_password=get_password_hash("test123"),
    is_active=1,
    is_superuser=0,
    subscription_tier="Free"
)

db.add(free_user)
db.commit()
db.close()

print("Free tier user created: free@test.com / test123")
