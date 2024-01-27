import os
import json
from tqdm import tqdm

from hera import Session
from hera.schema import *

from utils.json import read_json, write_json


def progress_decorator(func):
    def wrapper(progress_list: list, process_name: str, *args):
        if len(progress_list) > 0:
            serializzable_flag = is_serializable(progress_list)
            file_name = f"files/{process_name}.json"
            if os.path.exists(file_name):
                progress_status = read_json(file_name)
            else:
                progress_status = {
                    'index': 0,
                    'serializzable_flag': serializzable_flag,
                    'list': progress_list if serializzable_flag else serialize(progress_list)
                }
                if not serializzable_flag:
                    progress_status['entity'] = progress_list[0].__class__.__name__
                write_json(progress_status, file_name)

            for item in tqdm(progress_status['list'][progress_status['index']:]):
                print('\n')
                func(
                    item if serializzable_flag else deserialize(item, progress_status['entity']),
                    *args
                )
                progress_status['index'] += 1
                write_json(progress_status, file_name)

            os.remove(file_name)
        else:
            print('Lista vuota =(')
    return wrapper


def serialize(progress_list):
    return [item.id for item in progress_list]


def deserialize(item, entity):
    item_class = globals()[entity]
    with Session() as session:
        return session.query(item_class).filter(
            item_class.id == item
        ).first()


def is_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except TypeError:
        return False
