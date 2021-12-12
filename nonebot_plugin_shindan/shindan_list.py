import json
from pathlib import Path

data_path = Path() / 'data' / 'shindan' / 'shindan_list.json'


default_list = {
    '162207': {
        'command': '二次元少女',
        'title': '你的二次元少女化形象'
    },
    '917962': {
        'command': '人设生成',
        'title': '人设生成器'
    },
    '790697': {
        'command': '中二称号',
        'title': '奇妙的中二称号生成器'
    },
    '587874': {
        'command': '异世界转生',
        'title': '異世界轉生—∩開始的種族∩——'
    },
    '1098085': {
        'command': '特殊能力',
        'title': '测测你的特殊能力是什么？'
    },
    '940824': {
        'command': '魔法人生',
        'title': '魔法人生：我在霍格沃兹读书时发生的两三事'
    }
}


def load_shindan_list() -> dict:
    try:
        return json.load(data_path.open('r', encoding='utf-8'))
    except FileNotFoundError:
        return default_list


_shindan_list = load_shindan_list()


def dump_shindan_list():
    data_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        _shindan_list,
        data_path.open('w', encoding='utf-8'),
        indent=4,
        separators=(',', ': '),
        ensure_ascii=False
    )


def get_shindan_list() -> dict:
    return _shindan_list


def add_shindan(id: str, cmd: str, title: str) -> bool:
    if id in _shindan_list:
        return False
    _shindan_list[id] = {
        'command': cmd,
        'title': title
    }
    dump_shindan_list()
    return True


def del_shindan(id: str) -> bool:
    if id not in _shindan_list:
        return False
    _shindan_list.pop(id)
    dump_shindan_list()
    return True
