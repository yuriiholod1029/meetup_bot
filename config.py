import json
import logging


class JsonFileConfig(object):
    def __init__(self, file_path):
        self._file_path = file_path
        self._config = {}

    def evaluate(self, attendance_response):
        rsvp = attendance_response.get("rsvp")
        if not rsvp:
            return 0  # case when user did not declared any attendance before event

        declaration = rsvp["response"]
        attendance = attendance_response["status"]

        config_key = "{0}, {1}".format(declaration, attendance)
        grade = self._config.get(config_key)

        if not grade:
            logging.warning("Unknown attendances composition: %s", config_key)
            return 0

        return grade

    def load(self):
        with open(self._file_path, "r") as f:
            self._config = json.loads(f.read())
