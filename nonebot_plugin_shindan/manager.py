from sqlmodel import select
from typing import List, Optional

from nonebot_plugin_datastore import create_session

from .model import ShindanRecord


class ShindanManager:
    def __init__(self):
        self.shindan_records: List[ShindanRecord] = []

    async def load_shindan_records(self):
        async with create_session() as session:
            statement = select(ShindanRecord)
            self.shindan_records = (await session.exec(statement)).all()  # type: ignore

    async def add_shindan(
        self, shindan_id: str, command: str, title: str, mode: str = "image"
    ) -> Optional[str]:
        for record in self.shindan_records:
            if shindan_id == record.shindan_id:
                return "该占卜已存在"
            if command == record.command:
                return "该指令已存在"
        async with create_session() as session:
            record = ShindanRecord(
                shindan_id=shindan_id, command=command, title=title, mode=mode
            )
            session.add(record)
            await session.commit()
        await self.load_shindan_records()

    async def remove_shindan(self, shindan_id: str) -> Optional[str]:
        if shindan_id not in [record.shindan_id for record in self.shindan_records]:
            return "不存在该占卜"
        async with create_session() as session:
            statement = select(ShindanRecord).where(
                ShindanRecord.shindan_id == shindan_id
            )
            record: Optional[ShindanRecord] = await session.scalar(statement)
            if record:
                await session.delete(record)
                await session.commit()
        await self.load_shindan_records()

    async def set_shindan_mode(self, shindan_id: str, mode: str) -> Optional[str]:
        if shindan_id not in [record.shindan_id for record in self.shindan_records]:
            return "不存在该占卜"
        async with create_session() as session:
            statement = select(ShindanRecord).where(
                ShindanRecord.shindan_id == shindan_id
            )
            record: Optional[ShindanRecord] = await session.scalar(statement)
            if record:
                record.mode = mode
                session.add(record)
                await session.commit()
        await self.load_shindan_records()


shindan_manager = ShindanManager()
