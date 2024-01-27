from datetime import datetime
import warnings


def convert_unix_timestamp_to_mysql(datetime_list):
    """Convert a timestamp to a MySQL datetime format.

    Args:
        datetime_list (list): _description_

    Returns:
        str: _description_
    """
    if datetime_list == 'NULL':
        return datetime_list
    else:
        datetime_obj = datetime.fromtimestamp(int(datetime_list[0]))
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')


def datetime_to_unixtimestamp(dt_obj):
    """Convert datetime to unix format timestamp.

    Args:
        dt_obj (_type_): _description_

    Returns:
        str: _description_
    """
    timestamp = int(dt_obj.timestamp())
    return str(timestamp)


def now() -> str:
    """Return a string of the current time.

    Returns:
        str: _description_
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def today() -> str:
    warnings.warn('This function is deprecated', DeprecationWarning)
    return datetime.now().strftime('%Y-%m-%d')


def saveLog(msg: str, process: str) -> None:
    warnings.warn('This function is deprecated', DeprecationWarning)
    with open('log/' + today() + '.txt', "a") as file:
        file.write(msg + '\n')
