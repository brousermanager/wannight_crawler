from utils.json import read_json, write_json


def guided_walk(data, path_obj: dict, finish_walk: bool):
    steps = path_obj['path'].split(' - ')
    try:
        for step in steps:
            if steps.index(step) == len(steps) - 1:
                finish_walk = True
            if step[0] == '{':
                data = data[step[1:-1]]
            elif step[0] == '[':
                for item in data:
                    try:
                        path_obj['path'] = ' - '.join(steps[steps.index(step) + 1:])
                        result, finish_walk = guided_walk(item, path_obj, finish_walk)
                        if result and finish_walk and type_control(result, path_obj):
                            return result, finish_walk
                        else:
                            finish_walk = False
                    except:
                        finish_walk = False
                        pass
    except:
        pass
    return data, finish_walk


def type_control(element, path_obj: dict):
    if (path_obj['type'] == "<class 'list'>"):
        try:
            return str(type(element)) == path_obj['type'] and \
                str(type(element[0])) == path_obj['item-type'] and \
                    (True if path_obj['item-type'] == "<class 'dict'>" else path_obj['dict-key'] in element[0])
        except:
            return False
    else:
        return str(type(element)) == path_obj['type']


def find_values(data, id):
    paths = read_json('files/dioniso_inputs/path.json')
    res = {'fb_id': id}
    for path in paths['using_path']:
        element, flag = guided_walk(data, path, False)
        if element and flag and type_control(element, path):
            res[path['name']] = element
        else:
            print(f"\033[91mNon trovato {path['name']} per evento {id}\033[0m")
            if path['require']:
                write_json(data, f"files/dioniso_outputs/{id}.json")
    return res
