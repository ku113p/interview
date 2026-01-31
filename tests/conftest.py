import pytest

from src import db


@pytest.fixture(autouse=True)
def reset_db():
    db.BaseModel._storages = {}
    yield
    db.BaseModel._storages = {}
