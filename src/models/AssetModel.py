from .DatabaseModel import DatabaseModel
from .db_schemes import Asset
from .enums.DatabaseEnums import DatabaseEnums
from bson import ObjectId

class AssetModel(DatabaseModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DatabaseEnums.ASSETS.value]

    @classmethod
    async def create_instance(cls,db_client):
        await cls.create_index(db_client)
        model = cls(db_client)
        return model

    @staticmethod
    async def create_index(db_client):
        collection = db_client[DatabaseEnums.ASSETS.value]
        for index in Asset.get_indexes():
            await collection.create_index(
                index["keys"],
                name=index["name"],
                **index["options"]
            )

    async def insert_asset(self, asset: Asset):

        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_none=True))
        asset.id = result.inserted_id

        return asset

    async def get_project_assets(self, asset_project_id: str, asset_type: str = None):
        # use the asset_project_id index to quickly find documents matching that field, then filter those results by asset_type.
        query = {
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id
        }
        if asset_type:
            query["asset_type"] = asset_type

        records = await self.collection.find(query).to_list(length=None)

        return [
            Asset(**record)
            for record in records
        ]

    async def get_asset(self, asset_project_id: str, asset_name: str):

        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name,
        })

        if record:
            return Asset(**record)
        
        return None


    