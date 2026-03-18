import asyncio
import uuid
import traceback
from app.core.config import settings
from app.db.session import engine, async_session_factory
from app.services.user_service import UserService
from app.schemas.user import UserCreate

async def run_test():
    random_email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    print(f"Testing direct user creation with: {random_email}")
    
    user_data = UserCreate(
        email=random_email,
        password="Password123!",
        name="Test User",
        role="student",
        university="Test Uni"
    )
    
    async with async_session_factory() as session:
        user_service = UserService(session)
        try:
            # Let's see what exactly throws an error
            hashed_pw = user_service._hash_password(user_data.password)
            print("Password hashed successfully!")
            
            user = await user_service.create_user(user_data)
            if user:
                print(f"SUCCESS: User created with ID: {user.id}")
            else:
                print("FAILED: create_user returned None. There should be an error logged above.")
        except Exception as e:
            print("EXCEPTION CAUGHT IN TEST SCRIPT:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test())
