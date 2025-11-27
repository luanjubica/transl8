from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    org_id: UUID = Query(..., description="Organization ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all projects in an organization.

    API-first design: Returns paginated list with document counts.
    """
    # TODO: Add org membership check

    # Get total count
    total = db.query(func.count(Project.id)).filter(
        Project.org_id == org_id
    ).scalar()

    # Get projects with pagination
    projects = db.query(Project).filter(
        Project.org_id == org_id
    ).offset((page - 1) * page_size).limit(page_size).all()

    # Add document counts
    project_responses = []
    for project in projects:
        doc_count = db.query(func.count(Document.id)).filter(
            Document.project_id == project.id
        ).scalar()

        project_dict = ProjectResponse.model_validate(project).model_dump()
        project_dict['document_count'] = doc_count
        project_responses.append(ProjectResponse(**project_dict))

    return ProjectListResponse(
        items=project_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new project.

    API-first design: Accepts organization ID as query parameter.
    """
    # TODO: Add org membership check

    project = Project(
        org_id=org_id,
        name=project_data.name,
        source_language=project_data.source_language,
        target_languages=project_data.target_languages,
        created_by=current_user.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get project details by ID.

    API-first design: Returns full project information with document count.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # TODO: Add org membership check

    # Add document count
    doc_count = db.query(func.count(Document.id)).filter(
        Document.project_id == project.id
    ).scalar()

    project_dict = ProjectResponse.model_validate(project).model_dump()
    project_dict['document_count'] = doc_count

    return ProjectResponse(**project_dict)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update project details.

    API-first design: Partial updates supported via PATCH.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # TODO: Add org membership check

    # Update only provided fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project.

    API-first design: Cascade deletes all associated documents and segments.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # TODO: Add org membership check with role validation (owner/admin only)

    db.delete(project)
    db.commit()

    return None
