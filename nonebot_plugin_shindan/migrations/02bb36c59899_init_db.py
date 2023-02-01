"""init_db

Revision ID: 02bb36c59899
Revises: 
Create Date: 2023-02-01 16:13:45.941344

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlmodel import Session, SQLModel, Field
from typing import Optional

# revision identifiers, used by Alembic.
revision = "02bb36c59899"
down_revision = None
branch_labels = None
depends_on = None


class ShindanRecord(SQLModel, table=True):
    __tablename__: str = "nonebot_plugin_shindan_shindanrecord"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    shindan_id: str
    command: str
    title: str = ""
    mode: str = "image"


default_shindan_records = [
    ShindanRecord(shindan_id="162207", command="今天是什么少女", title="你的二次元少女化形象"),
    ShindanRecord(shindan_id="917962", command="人设生成", title="人设生成器"),
    ShindanRecord(shindan_id="790697", command="中二称号", title="奇妙的中二称号生成器"),
    ShindanRecord(shindan_id="587874", command="异世界转生", title="異世界轉生—∩開始的種族∩——"),
    ShindanRecord(shindan_id="940824", command="魔法人生", title="魔法人生：我在霍格沃兹读书时发生的两三事"),
    ShindanRecord(
        shindan_id="1075116", command="抽老婆", title="あなたの二次元での嫁ヒロイン", mode="text"
    ),
    ShindanRecord(shindan_id="400813", command="抽舰娘", title="【艦これ】あ なたの嫁になる艦娘は？"),
    ShindanRecord(shindan_id="361845", command="抽高达", title="マイ・ガンダム診断"),
    ShindanRecord(shindan_id="595068", command="英灵召唤", title="Fate 英霊召喚"),
    ShindanRecord(
        shindan_id="360578", command="卖萌", title="顔文字作るよ(  ﾟдﾟ )", mode="text"
    ),
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "nonebot_plugin_shindan_shindanrecord",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shindan_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("command", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("mode", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with Session(op.get_bind()) as session:
        for record in default_shindan_records:
            session.add(record)
        session.commit()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("nonebot_plugin_shindan_shindanrecord")
    # ### end Alembic commands ###
