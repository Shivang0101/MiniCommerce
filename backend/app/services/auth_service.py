import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
        existing_user = await UserRepository.get_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_pwd = hash_password(user_in.password)
        is_admin = getattr(user_in, "is_admin", False)
        role = getattr(user_in, "role", "CUSTOMER")
        if is_admin and role == "CUSTOMER":
            role = "SRE_ADMIN"
        return await UserRepository.create(db, user_in.email, hashed_pwd, is_admin=is_admin, role=role)


    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
        user = await UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
        return await UserRepository.get_by_id(db, user_id)
