import json
from pathlib import Path

data_path = Path() / 'data' / 'shindan'


def load_shindan_list() -> dict:
    try:
        return json.load(data_path.open('r', encoding='utf-8'))
    except FileNotFoundError:
        return {}


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


def get_shindan_list_all() -> dict:
    return _shindan_list


def get_shindan_list(user_id: str) -> dict:
    if user_id not in _shindan_list:
        return {}
    return _shindan_list[user_id]


def add_shindan(user_id: str, id: str, cmd: str, title: str) -> str:
    user_list = get_shindan_list(user_id)
    if id in user_list:
        return False
    user_list[id] = {
        'command': cmd,
        'title': title
    }
    _shindan_list[user_id] = user_list
    dump_shindan_list()
    return True


def del_shindan(user_id: str, id: str) -> str:
    user_list = get_shindan_list(user_id)
    if id not in user_list:
        return False
    user_list.pop(id)
    if user_list:
        _shindan_list[user_id] = user_list
    else:
        _shindan_list.pop(user_id)
    dump_shindan_list()
    return True
