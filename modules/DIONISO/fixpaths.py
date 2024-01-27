# we take this as a reference event
import json
from modules.HERA.HERA import executeQuery
import collections
from utils.convert_time import datetime_to_unixtimestamp

reference_event_id = '924894085405982'
reference_event_ids = ['1581083905669191',
                       '731449938602012',
                       '729890492192727',
                       '703086307969608',
                       '537953025067798',
                       '640277694519778',
                       '5610938859034325',
                       '953793272287692',
                       '713779383763548',
                       '695438225416726',
                       '650471590173298',
                       '1508102862989490',
                       '963474418178520'
                       '678933103950494'
                       '1327067084720414'
                       '1199316581023545']


def levenshtein(s1, s2):
    """Compute the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def bfs_search(json_obj, target):
    queue = collections.deque([(json_obj, [])])
    best_distance = float('inf')  # Initialize with infinity
    best_path = None

    while queue:
        node, path = queue.popleft()

        # If node is a string and target is also a string
        if isinstance(node, str) and isinstance(target, str):
            distance = levenshtein(node, target)
            if distance < best_distance:
                best_distance = distance
                best_path = path

        # If node is a number (int or float) and target is also a number
        elif (isinstance(node, (int, float)) and isinstance(target, (int, float))):
            distance = abs(node - target)
            if distance < best_distance:
                best_distance = distance
                best_path = path

        # If node is a dictionary
        if isinstance(node, dict):
            for key, value in node.items():
                new_path = list(path)
                new_path.append(key)
                queue.append((value, new_path))

        # If node is a list
        if isinstance(node, list):
            for i, value in enumerate(node):
                new_path = list(path)
                new_path.append(i)
                queue.append((value, new_path))

    return best_path


def get_value_from_path(json_obj, path):
    """Retrieve value from a nested JSON object using the provided path.


    Args:
        json_obj (_type_): _description_
        path (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    current_obj = json_obj
    for step in path:
        if isinstance(current_obj, dict):
            current_obj = current_obj[step]
        elif isinstance(current_obj, list) and isinstance(step, int):
            current_obj = current_obj[step]
        else:
            raise ValueError(f"Invalid step {step} for object type {type(current_obj)}")
    return current_obj


def getReferenceEvent(newlistjsons):
    for newjson in newlistjsons:
        values = executeQuery('SELECT * FROM wannight.evento WHERE id_fb = {}'.format(reference_event_id))[0]
        nome = values['nome']
        descrizione = values['descrizione']
        data_inizio = values['data_inizio']
        indirizzo = values['indirizzo']
        latitudine = float(values['latitudine'])
        longitudine = float(values['longitudine'])
        nome_comune = values['nome_comune']
        url_ticket = values['url_ticket']
        # Convert datetime to UNIX timestamp string
        data_inizio = int(datetime_to_unixtimestamp(data_inizio))
        variables = [nome, data_inizio, indirizzo, latitudine,
                     longitudine, nome_comune, url_ticket, descrizione]

        for variable in variables:
            getnewpaths(newjson, variable)


def getnewpaths(json_obj, target):
    # search for value
    path = bfs_search(json_obj, target)
    # to prove that the path is correct we can use the following code
    value = get_value_from_path(json_obj, path)
    print(f'path:{path} value: {value}')

    return path, value
