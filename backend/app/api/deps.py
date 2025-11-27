from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User
from app.models.organization import OrgMember


def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from database.

    Creates user if it doesn't exist (first login from Clerk).

    Args:
        user_id: Clerk user ID from JWT token
        db: Database session

    Returns:
        User model instance

    Raises:
        HTTPException: If user cannot be retrieved/created
    """
    user = db.query(User).filter(User.clerk_id == user_id).first()

    if not user:
        # User doesn't exist - create from Clerk ID
        # In production, you would fetch user details from Clerk API
        user = User(clerk_id=user_id, email=f"{user_id}@temp.com")
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def get_user_org_access(
    org_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrgMember:
    """
    Verify user has access to organization.

    Args:
        org_id: Organization UUID
        user: Current authenticated user
        db: Database session

    Returns:
        OrgMember instance with role information

    Raises:
        HTTPException: If user is not a member of the organization
    """
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization"
        )

    return membership
