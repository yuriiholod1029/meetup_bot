import json


class JsonFileConfig(object):
    def __init__(self, file_path):
        self._file_path = file_path
        # TODO check if file exists and, maybe, if is valid
        self._read()

    def evaluate(self, attendance_status):
        return self._config[attendance_status]

    def _read(self):
        with open(self._file_path, "r") as f:
            self._config = json.loads(f.read())
