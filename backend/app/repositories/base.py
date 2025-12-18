from typing import Any, Mapping, Optional, TypeVar, Union

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase


T = TypeVar("T", bound=Mapping[str, Any])


def to_object_id(id_str: str) -> ObjectId:
    return ObjectId(id_str)


def oid_str(oid: Union[ObjectId, Any]) -> str:
    return str(oid)


class BaseRepository:
    """
    Lightweight repository wrapper around a Mongo collection.
    """

    collection_name: str

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    @property
    def col(self) -> AsyncIOMotorCollection:
        return self.db[self.collection_name]

    async def insert_one(self, doc: dict[str, Any]) -> str:
        res = await self.col.insert_one(doc)
        return oid_str(res.inserted_id)

    async def find_one(self, query: dict[str, Any]) -> Optional[dict[str, Any]]:
        return await self.col.find_one(query)

    async def find_by_id(self, id_str: str) -> Optional[dict[str, Any]]:
        return await self.col.find_one({"_id": to_object_id(id_str)})

    async def find_many(
        self,
        query: Optional[dict[str, Any]] = None,
        *,
        limit: int = 100,
        skip: int = 0,
        sort: Optional[list[tuple[str, int]]] = None,
    ) -> list[dict[str, Any]]:
        q = query or {}
        cursor = self.col.find(q).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        return await cursor.to_list(length=limit)

    async def update_one(
        self, query: dict[str, Any], update: dict[str, Any], *, upsert: bool = False
    ) -> int:
        res = await self.col.update_one(query, update, upsert=upsert)
        return res.modified_count

    async def delete_one(self, query: dict[str, Any]) -> int:
        res = await self.col.delete_one(query)
        return res.deleted_count


