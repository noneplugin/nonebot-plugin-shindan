from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    shindanmaker_cookie: str = ""


shindan_config = get_plugin_config(Config)
