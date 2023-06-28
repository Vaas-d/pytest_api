import json
from threading import Lock


def write_to_file(file, key, value) -> None:
    lock = Lock()
    lock.acquire()
    with open(file) as f:
        data = json.load(f)
    test_data = data
    test_data[key] = value
    with open(file, 'w') as f:
        json.dump(test_data, f, indent=1, sort_keys=True)
    lock.release()


def read_from_file(file, key) -> str:
    with open(file) as f:
        data = json.load(f)
        value = data.get(key)
    return value
