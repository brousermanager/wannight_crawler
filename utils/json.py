import json
import regex


def read_json(path: str):
    """Reads a JSON file.

    Args:
        path (str): _description_

    Returns:
        any: _description_ 
    """
    with open(path, "r") as file:
        return json.load(file)


def write_json(data, path: str):
    """Writes a JSON file.

    Args:
        data (_type_): _description_
        path (str): _description_
    """
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def extract_object(json_obj, object_name):
    """Parse a JSON object into dictionary.

    Args:
        json_obj (_type_): _description_
        object_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Parse the JSON string into a Python dictionary
    data = json_obj

    # Extract the object with the given nam
    # if the key is the same of the object name

    if object_name in data:
        return data[object_name]
    else:
        for value in data.values():
            if isinstance(value, dict):
                result = extract_object(json.dumps(value), object_name)
                if result is not None:
                    return result
            if isinstance(value, list):
                for item in value:
                    result = extract_object(json.dumps(item), object_name)
                    if result is not None:
                        return result
    return None


def extractEventsFromJson(stringa: str, oldOrNew: bool) -> list:
    """Extracts events from a JSON file.

    Args:
        stringa (str): _description_
        oldOrNew (bool): _description_

    Returns:
        list: _description_
    """
    parameter = 'upcoming_events' if oldOrNew else 'past_events'
    eventIDList = []
    json_object = json.loads(stringa)
    if 'data' in json_object:
        if 'page' in json_object['data']:
            if parameter in json_object['data']['page']:
                for event in json_object['data']['page'][parameter]['edges']:
                    eventIDList.append(event['node']['id'])
    return eventIDList


def extractJsonFromHtml(soup: str, eventID: str = None) -> list:
    """Extract JSON from HTML document.
    To extract all json objects pass eventID = None

    Args:
        soup (str): _description_
        eventID (str, optional): _description_. Defaults to None.

    Returns:
        list: _description_
    """
    pattern = regex.compile(r'(?<j>\{(?:[^{}]|(?&j))*\})')
    json_objects = []
    for each in pattern.findall(soup):
        if eventID == None or eventID in each:
            try:
                correctJson = json.loads(each)
                json_objects.append(correctJson)

            except:
                each = each[1: -1]
                each = each[each.find('{'):]
                each = each[:each.rfind('}') + 1]
                json_objects.extend(extractJsonFromHtml(each))

    return json_objects

# data una key search_value_key e una sua subkey search_key, restituisce il valore della subkey


def find_json_value(json_obj, search_key, search_value_key='value'):

    results = []

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == search_key and search_value_key in value:
                results.append(value[search_value_key])
            elif isinstance(value, (dict, list)):
                results.extend(find_json_value(
                    value, search_key, search_value_key))
    elif isinstance(json_obj, list):
        for item in json_obj:
            results.extend(find_json_value(item, search_key, search_value_key))

    return results


# search for a specific path in a json object with a specific value
# you need to convert to returned value to a list if you want to visualize it
def find_paths(json_object, target_value, current_path=[]):
    """Recursively finds all paths to a target value in a JSON object."""
    if isinstance(json_object, dict):
        for key, value in json_object.items():
            if value == target_value:
                yield current_path + [key]
            else:
                yield from find_paths(value, target_value, current_path + [key])
    elif isinstance(json_object, list):
        for i, value in enumerate(json_object):
            if value == target_value:
                yield current_path + [i]
            else:
                yield from find_paths(value, target_value, current_path + [i])


# function to find a list present somewhere in a complex json
def find_list(json_obj, list_name):
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == list_name and isinstance(value, list):
                return value
            elif isinstance(value, (dict, list)):
                result = find_list(value, list_name)
                if result is not None:
                    return result
    elif isinstance(json_obj, list):
        for item in json_obj:
            result = find_list(item, list_name)
            if result is not None:
                return result
    return None
