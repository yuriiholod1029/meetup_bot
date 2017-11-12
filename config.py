
class FileConfig(object):
    def __init__(self, file_path):
        self._file_path = file_path
        # TODO check if file exists and, maybe, if is valid
        self._config = self._read()

    def evaluate(self, attendance_status):
        return 1  # TODO need to use status -> points mapping

    def _read(self):
        with open(self._file_path, 'r') as config:
            config.readline()
        return {}
