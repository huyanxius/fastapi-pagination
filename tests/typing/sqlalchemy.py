from typing import Any

from sqlalchemy import func, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, FromStatement, Mapped, Session, mapped_column
from typing_extensions import assert_type

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import (
    Selectable,
    apaginate,
    create_count_query,
    create_paginate_query,
    paginate,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


async def check_queries(session: Session, async_session: AsyncSession, statement: FromStatement) -> None:
    entity = select(User)
    columns = select(User.id, User.name)
    mixed = select(User, User.name)
    compound = columns.union_all(columns)
    raw = text("SELECT id, name FROM users")
    count = select(func.count()).select_from(User)
    params = Params()

    assert_type(paginate(session, entity, params, count_query=count), Any)
    assert_type(await apaginate(async_session, entity, params, count_query=count), Any)
    paginate(session, columns, params)
    await apaginate(async_session, columns, params)
    paginate(session, mixed, params)
    await apaginate(async_session, mixed, params)
    paginate(session, compound, params)
    await apaginate(async_session, compound, params)
    paginate(session, raw, params)
    await apaginate(async_session, raw, params)
    paginate(session, statement, params)
    await apaginate(async_session, statement, params)

    assert_type(create_count_query(entity), Selectable)
    assert_type(create_paginate_query(columns, params), Selectable)

    # These ignores must stay necessary: accepting Any would stop rejecting invalid queries.
    await apaginate(async_session, "SELECT 1", params)  # ty: ignore[invalid-argument-type]
    await apaginate(async_session, 1, params)  # ty: ignore[invalid-argument-type]
    await apaginate(async_session, User, params)  # ty: ignore[invalid-argument-type]
    await apaginate(async_session, insert(User), params)  # ty: ignore[invalid-argument-type]
    await apaginate(async_session, entity, params, count_query="SELECT 1")  # ty: ignore[invalid-argument-type]
