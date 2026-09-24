import math
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db_schemes import Project,AlchemyProject


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_alchemy(project: Project) -> AlchemyProject:
        """
        Convert Pydantic Project -> SQLAlchemy AlchemyProject.
        """
        return AlchemyProject(
            id=project.id or uuid.uuid4(),
            project_id=project.project_id,
        )

    @staticmethod
    def _to_pydantic(project: AlchemyProject) -> Project:
        """
        Convert SQLAlchemy AlchemyProject -> Pydantic Project.
        """
        return Project.model_validate(project)

    async def insert_project(self, project: Project) -> Project:
        """
        Insert a project into PostgreSQL.
        """
        db_project = self._to_alchemy(project)

        self.session.add(db_project)

        await self.session.commit()

        return self._to_pydantic(db_project)

    async def does_project_exist(self, project_id: str) -> bool:
        """
        Check whether a project exists by project_id.
        """
        stmt = (
            select(AlchemyProject.id)
            .where(AlchemyProject.project_id == project_id)
            .limit(1)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def find_project(self, project_id: str) -> Project:
        """
        Retrieve a project by project_id.

        If the project does not exist, create it.
        """
        stmt = select(AlchemyProject).where(
            AlchemyProject.project_id == project_id
        )

        result = await self.session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if db_project is None:
            project = Project(project_id=project_id)
            return await self.insert_project(project)

        return self._to_pydantic(db_project)

    async def get_projects(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Project], int]:
        """
        Retrieve projects using pagination.

        Returns:
            (
                list[Project],
                total_pages
            )
        """
        # Count total projects
        count_stmt = select(func.count()).select_from(AlchemyProject)

        count_result = await self.session.execute(count_stmt)
        projects_count = count_result.scalar_one()

        total_pages = math.ceil(projects_count / page_size)

        # Retrieve current page
        stmt = (
            select(AlchemyProject)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.session.execute(stmt)

        db_projects = result.scalars().all()

        projects = [
            self._to_pydantic(db_project)
            for db_project in db_projects
        ]

        return projects, total_pages