from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db_schemes import Asset,AlchemyAsset


class AssetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_alchemy(asset: Asset) -> AlchemyAsset:
        """
        Convert Pydantic Asset -> SQLAlchemy AlchemyAsset.
        """
        return AlchemyAsset(
            id=asset.id,
            asset_project_id=asset.asset_project_id,
            asset_type=asset.asset_type,
            asset_name=asset.asset_name,
            asset_size=asset.asset_size,
            asset_config=asset.asset_config,
            asset_pushed_at=asset.asset_pushed_at,
        )

    @staticmethod
    def _to_pydantic(asset: AlchemyAsset) -> Asset:
        """
        Convert SQLAlchemy AlchemyAsset -> Pydantic Asset.
        """
        return Asset.model_validate(asset)

    async def dose_asset_exist(self, asset_name: str) -> bool:
        """
        Check whether an asset with the given name exists.
        """
        stmt = (
            select(AlchemyAsset.id)
            .where(AlchemyAsset.asset_name == asset_name)
            .limit(1)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def insert_asset(self, asset: Asset) -> Asset:
        """
        Insert an asset into PostgreSQL.
        """
        db_asset = self._to_alchemy(asset)

        self.session.add(db_asset)

        await self.session.commit()

        return self._to_pydantic(db_asset)

    async def get_project_assets(
        self,
        asset_project_id,
        asset_type: str | None = None,
    ) -> list[Asset]:
        """
        Get all assets belonging to a project.

        Optionally filter by asset_type.
        """
        stmt = select(AlchemyAsset).where(
            AlchemyAsset.asset_project_id == asset_project_id
        )

        if asset_type is not None:
            stmt = stmt.where(
                AlchemyAsset.asset_type == asset_type
            )

        result = await self.session.execute(stmt)

        db_assets = result.scalars().all()

        return [
            self._to_pydantic(db_asset)
            for db_asset in db_assets
        ]

    async def get_asset(
        self,
        asset_project_id,
        asset_name: str,
    ) -> Asset | None:
        """
        Get an asset by project ID and asset name.
        """
        stmt = select(AlchemyAsset).where(
            AlchemyAsset.asset_project_id == asset_project_id,
            AlchemyAsset.asset_name == asset_name,
        )

        result = await self.session.execute(stmt)

        db_asset = result.scalar_one_or_none()

        if db_asset is None:
            return None

        return self._to_pydantic(db_asset)