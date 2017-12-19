
class ReputationDumper(object):
    def __init__(self, result_file_path, reputation_object):
        self._result_file_path = result_file_path
        self._reputation_obj = reputation_object

    def dump_to_csv(self):
        with open(self._result_file_path, "w") as f:
            content = self._reputation_obj.dump_to_csv()
            f.write(content)
