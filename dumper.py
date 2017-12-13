
class ReputationDumper(object):
    def __init__(self, result_file_path, reputation_object):
        self._result_file_path = result_file_path
        self._reputation_obj = reputation_object

    def dump_to_csv(self):
        with open(self._result_file_path, "w") as f:
            content = self._reputation_obj.dump_to_csv()
            f.write(content)


class DeclarationsDumper(object):
    def __init__(self, result_file_path, declarations_list):
        self._result_file_path = result_file_path
        self._declarations_list = declarations_list

    def dump_to_csv(self):
        with open(self._result_file_path, "w") as f:
            f.write("")

        with open(self._result_file_path, "a") as f:
            for attendance_record in self._declarations_list:
                if attendance_record["member"]["id"] == 0:
                    continue  # case when member is a former member

                line = "{0},{1}\n".format(attendance_record["member"]["id"], attendance_record["status"])
                f.write(line)
