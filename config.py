import json


class JsonFileConfig(object):
    def __init__(self, file_path):
        self._file_path = file_path
        self._config = {}

    def evaluate(self, attendance_status):
        return self._config[attendance_status]

    def load(self):
        with open(self._file_path, "r") as f:
            self._config = json.loads(f.read())
