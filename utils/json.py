import json


def load_str(json_str):
    return json.loads(json_str)


def load_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)