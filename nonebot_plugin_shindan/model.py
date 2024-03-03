from nonebot_plugin_orm import Model
from pydantic import BaseModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ShindanConfig(BaseModel):
    id: int
    command: str
    title: str
    mode: str


class ShindanRecord(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    shindan_id: Mapped[int]
    command: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, default="")
    mode: Mapped[str] = mapped_column(String(32), default="image")

    @property
    def config(self) -> "ShindanConfig":
        return ShindanConfig(
            id=self.shindan_id,
            command=self.command,
            title=self.title,
            mode=self.mode,
        )
