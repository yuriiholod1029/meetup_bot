from config import JsonFileConfig
from evaluator import Evaluator
from dumper import Dumper
from fetcher import MeetupFetcher
from reputation import Reputation

"""
Calling with:
    python3.6 evaluator.py [meetup_name=AgileWarsaw] [config_file=config.ini] [num_last_events=1]
"""

if __name__ == "__main__":
    # TODO parse input parameters

    fetch = MeetupFetcher("AgileWarsaw")
    configuration = JsonFileConfig("./config.json")
    configuration.load()

    reputation = Evaluator(configuration, fetch, 1).evaluate_by_events(Reputation)

    Dumper("result.csv", reputation).dump_to_csv()
