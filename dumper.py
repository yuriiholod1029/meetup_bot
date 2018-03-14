
class ReputationDumper(object):
    def __init__(self, reputation_object):
        self._reputation_obj = reputation_object

    def dump_to_csv(self, output_stream):
        with open(self._result_file_path, 'w', encoding='utf-8') as f:  # TypeError -> you are using python2.x
            self._reputation_obj.dump_to_csv(f)
