import json
import logging


class JsonFileConfig(object):
    def __init__(self, file_path):
        self._file_path = file_path
        self._config = {}

    def evaluate(self, attendance_response):
        rsvp = attendance_response.get("rsvp")
        if rsvp is None:
            return 0  # case when user did not declared any attendance before event

        declaration = rsvp["response"]
        attendance = attendance_response.get("status")
        if attendance_response is None:
            print(json.dumps(attendance_response, indent=4))
            return 0

        config_key = "{0}, {1}".format(declaration, attendance)
        grade = self._config.get(config_key)

        if grade is None:
            logging.warning("Unknown attendances composition: %r", config_key)
            return 0

        return grade

    def load(self):
        with open(self._file_path, "r") as f:
            self._config = json.loads(f.read())
