"""Unit tests for client company CRUD operations."""

import pytest

from bot.database.crud_modules.client_company_crud import (
    create_company,
    delete_company,
    get_all_companies,
    get_company_by_id,
    update_company,
)

# Test constants
_TEST_COMPANY_NAME = "Test Company"
_TEST_INN = "1234567890"
_TEST_EMAIL = "test@company.com"
_EXPECTED_COMPANIES_COUNT = 2

# Field keys
_NAME_KEY = "name"
_INN_KEY = "inn"
_EMAIL_KEY = "email"


@pytest.mark.asyncio
class TestClientCompanyCRUD:
    """Tests for client company CRUD operations."""

    async def test_create_company(
        self,
        test_session: object,
    ) -> None:
        """Test creating company."""
        company = await create_company(
            test_session,
            {
                _NAME_KEY: _TEST_COMPANY_NAME,
                _INN_KEY: _TEST_INN,
                _EMAIL_KEY: _TEST_EMAIL,
            },
        )
        assert company.name == _TEST_COMPANY_NAME
        assert company.inn == _TEST_INN

    async def test_get_company_by_id(
        self,
        test_session: object,
    ) -> None:
        """Test getting company by ID."""
        company = await create_company(
            test_session,
            {
                _NAME_KEY: _TEST_COMPANY_NAME,
                _INN_KEY: _TEST_INN,
            },
        )
        retrieved = await get_company_by_id(test_session, company.id)
        assert retrieved is not None
        assert retrieved.name == _TEST_COMPANY_NAME

    async def test_get_all_companies(
        self,
        test_session: object,
    ) -> None:
        """Test getting all companies."""
        await create_company(
            test_session,
            {_NAME_KEY: "Company 1"},
        )
        await create_company(
            test_session,
            {_NAME_KEY: "Company 2"},
        )
        companies = await get_all_companies(test_session)
        assert len(companies) == _EXPECTED_COMPANIES_COUNT

    async def test_update_company(
        self,
        test_session: object,
    ) -> None:
        """Test updating company."""
        company = await create_company(
            test_session,
            {
                _NAME_KEY: _TEST_COMPANY_NAME,
                _INN_KEY: _TEST_INN,
            },
        )
        updated = await update_company(
            test_session,
            company.id,
            {_EMAIL_KEY: "new@company.com"},
        )
        assert updated is not None
        assert updated.email == "new@company.com"

    async def test_delete_company(
        self,
        test_session: object,
    ) -> None:
        """Test deleting company."""
        company = await create_company(
            test_session,
            {
                _NAME_KEY: _TEST_COMPANY_NAME,
                _INN_KEY: _TEST_INN,
            },
        )
        deleted = await delete_company(test_session, company.id)
        assert deleted is True
        retrieved = await get_company_by_id(test_session, company.id)
        assert retrieved is None
