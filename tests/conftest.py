"""Pytest fixtures for tests."""

import asyncio
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

from bot.database.models.base import Base
from bot.database.models.enums import ProjectStatus, TaskStatus, UserRole
from bot.database.models.project import Project
from bot.database.models.task import Task
from bot.database.models.user import User

# Test constants
TEST_TELEGRAM_ID = 123456789
TEST_PHONE = "+79991234567"
TEST_EMAIL = "test@example.com"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine() -> object:
    """Create test database engine."""
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )


@pytest_asyncio.fixture
async def test_session(
    test_engine: object,
) -> AsyncGenerator[AsyncSession]:
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create test user."""
    user = User(
        telegram_id=TEST_TELEGRAM_ID,
        username="testuser",
        first_name="Test",
        last_name="User",
        role=UserRole.CLIENT,
        phone=TEST_PHONE,
        email=TEST_EMAIL,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_project(
    test_session: AsyncSession,
    test_user: User,
) -> Project:
    """Create test project."""
    project = Project(
        title="Test Project",
        description="Test Description",
        status=ProjectStatus.DRAFT,
        client_id=test_user.id,
    )
    test_session.add(project)
    await test_session.commit()
    await test_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_task(
    test_session: AsyncSession,
    test_project: Project,
) -> Task:
    """Create test task."""
    task = Task(
        project_id=test_project.id,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=3,
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task
