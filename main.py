import argparse
import sys

from config import JsonFileConfig
from evaluator import Evaluator
from dumper import ReputationDumper
from fetcher import MeetupFetcher
from reputation import Reputation


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meetup", help="meetup name", default="AgileWarsaw")
    parser.add_argument("--config", help="config file name", default="config.json")
    parser.add_argument("--last", help="number of last events to check", default="10", type=int)
    return parser.parse_args(sys.argv[1:])


if __name__ == "__main__":
    args = read_args()
    fetch = MeetupFetcher(args.meetup, token=open('.token').read().strip())
    configuration = JsonFileConfig(args.config)
    configuration.load()

    reputation = Evaluator(configuration, fetch, args.last).evaluate_by_events(Reputation)

    with open('result.csv', 'w', encoding='utf-8') as f:  # TypeError -> you are using python2.x
        ReputationDumper(reputation).dump_to_csv(output_stream)
