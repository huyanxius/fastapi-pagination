from __future__ import annotations

__all__ = [
    "LimitOffsetPage",
    "UseLimitOffsetHeaderLinks",
    "UseLimitOffsetLinks",
    "resolve_limit_offset_links",
]

from abc import ABC
from typing import Any, TypeAlias

from typing_extensions import TypeVar

from fastapi_pagination.customization import CustomizedPage
from fastapi_pagination.limit_offset import LimitOffsetPage as BasePage

from .bases import BaseLinksCustomizer, BaseUseHeaderLinks, BaseUseLinks, Links, create_links

TAny = TypeVar("TAny", default=Any)


def resolve_limit_offset_links(_page: BasePage, /) -> Links:
    offset, limit, total = _page.offset, _page.limit, _page.total

    if offset is None:
        offset = 0
    last = None
    if total is not None:
        last_offset = 0
        if limit is not None:
            # Preserve the current offset sequence for nonaligned offsets.
            start_offset = offset % limit
            last_offset = start_offset + (total - start_offset - 1) // limit * limit

        # Fall back to the first page when this offset sequence has no valid page.
        last = {"offset": max(0, last_offset)}

    return create_links(
        first={"offset": 0},
        last=last,
        next={"offset": offset + limit} if limit is not None and (total is None or offset + limit < total) else None,
        prev={"offset": offset - limit} if limit is not None and offset - limit >= 0 else None,
    )


class LimitOffsetLinksCustomizer(BaseLinksCustomizer, ABC):
    def resolve_links(self, _page: BasePage, /) -> Links:
        return resolve_limit_offset_links(_page)


class UseLimitOffsetLinks(LimitOffsetLinksCustomizer, BaseUseLinks):
    pass


class UseLimitOffsetHeaderLinks(LimitOffsetLinksCustomizer, BaseUseHeaderLinks):
    pass


LimitOffsetPage: TypeAlias = CustomizedPage[
    BasePage[TAny],
    UseLimitOffsetLinks(),
]
