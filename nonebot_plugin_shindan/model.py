from sqlmodel import Field
from typing import Optional

from nonebot_plugin_datastore import get_plugin_data

Model = get_plugin_data().Model


class ShindanRecord(Model, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    shindan_id: str
    command: str
    title: str = ""
    mode: str = "image"
