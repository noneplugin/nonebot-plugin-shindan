from nonebot_plugin_orm import Model
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ShindanRecord(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    shindan_id: Mapped[str] = mapped_column(String(32))
    command: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, default="")
    mode: Mapped[str] = mapped_column(String(32), default="image")
