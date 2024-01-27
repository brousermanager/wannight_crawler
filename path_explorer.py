import datetime

from utils.json import read_json, write_json

def save_path(name_key, target_path):
    print(f"Scrittura path {target_path}")
    file_path = 'files/dioniso_inputs/path.json'
    paths = read_json(file_path)
    if name_key in paths['find_path']:
        if target_path not in paths['find_path'][name_key]:
            paths['find_path'][name_key].append(target_path)
        else:
            print('Path già presente')
    else:
        paths['find_path'][name_key] = [target_path]
    write_json(paths, file_path)

def recursion_walk(name, element, target, path):
    if element == target:
        save_path(name_key, path)
    elif type(element) == list:
        for item in element:
            branch_path = f"{path if len(path) == 0 else f'{path} - '}[{element.index(item)}]"
            recursion_walk(name, item, target, branch_path)
    elif type(element) == dict:
        for key in element.keys():
            branch_path = f"{path if len(path) == 0 else f'{path} - '}{{{key}}}"
            recursion_walk(name, element[key], target, branch_path)

def prepare_target(target, key):
    if key in ['date_start', 'date_end']:
        dt_obj = datetime.datetime.strptime(target, "%Y-%m-%d %H:%M")
        return int(dt_obj.timestamp())
    else:
        return target

target = "Bevande"
name_key = 'categoria'
json_data = read_json('json/6687306977991569.json')
target_path = ''

target = prepare_target(target, name_key)
recursion_walk(name_key, json_data, target, target_path)
# res = find_values(json_data, 6687306977991569)
# print(res)