from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from google.cloud.datastore import Client, Entity, Key

from pdf_bot.account import AccountRepository


@pytest.fixture(name="user_entity")
def fixture_user_entity(user_id: int) -> Key:
    key = Key("User", user_id, project="test")
    return Entity(key)


@pytest.fixture(name="db")
def fixture_db() -> Client:
    return cast(Client, MagicMock())


@pytest.fixture(name="account_repository")
def fixture_account_repository(db) -> AccountRepository:
    return AccountRepository(db)


def test_get_user(
    account_repository: AccountRepository,
    db: Client,
    user_id: int,
    user_entity: Entity,
):
    db.get.return_value = user_entity
    actual = account_repository.get_user(user_id)
    assert actual == user_entity


def test_get_user_null(
    account_repository: AccountRepository,
    db: Client,
    user_id: int,
):
    db.get.return_value = None
    actual = account_repository.get_user(user_id)
    assert actual is None


def test_upsert_user(
    account_repository: AccountRepository,
    db: Client,
    user_id: int,
    language_code: str,
    user_entity: Entity,
):
    db.get.return_value = user_entity

    account_repository.upsert_user(user_id, language_code)

    assert user_entity["language"] == language_code
    db.put.assert_called_with(user_entity)


def test_upsert_user_new_user(
    account_repository: AccountRepository,
    db: Client,
    user_id: int,
    language_code: str,
    user_entity: Entity,
):
    with patch("pdf_bot.account.account_repository.datastore") as datastore:
        datastore.Entity.return_value = user_entity
        db.get.return_value = None

        account_repository.upsert_user(user_id, language_code)

        db.put.assert_called_with(user_entity)
