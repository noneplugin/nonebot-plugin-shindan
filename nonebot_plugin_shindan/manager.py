from typing import Optional

from nonebot_plugin_orm import get_session
from sqlalchemy import select

from .model import ShindanConfig, ShindanRecord


class ShindanManager:
    def __init__(self):
        self.shindan_list: list[ShindanConfig] = []

    async def load_shindan(self):
        async with get_session() as session:
            statement = select(ShindanRecord)
            shindan_records = (await session.scalars(statement)).all()
            self.shindan_list = [record.config for record in shindan_records]

    async def add_shindan(self, id: int, command: str, title: str, mode: str = "image"):
        async with get_session() as session:
            record = ShindanRecord(
                shindan_id=id, command=command, title=title, mode=mode
            )
            session.add(record)
            await session.commit()
        await self.load_shindan()

    async def remove_shindan(self, id: int):
        async with get_session() as session:
            statement = select(ShindanRecord).where(ShindanRecord.shindan_id == id)
            if record := await session.scalar(statement):
                await session.delete(record)
                await session.commit()
        await self.load_shindan()

    async def set_shindan(
        self,
        id: int,
        *,
        command: Optional[str] = None,
        title: Optional[str] = None,
        mode: Optional[str] = None,
    ):
        async with get_session() as session:
            statement = select(ShindanRecord).where(ShindanRecord.shindan_id == id)
            if record := await session.scalar(statement):
                if command:
                    record.command = command
                if title:
                    record.title = title
                if mode:
                    record.mode = mode
                session.add(record)
                await session.commit()
        await self.load_shindan()


shindan_manager = ShindanManager()
