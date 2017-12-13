import argparse
import logging
import sys

from config import JsonFileConfig
from evaluator import Evaluator
from dumper import DeclarationsDumper, ReputationDumper
from fetcher import MeetupFetcher
from reputation import Reputation


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meetup", help="meetup name", default="AgileWarsaw")
    parser.add_argument("--config", help="config file name", default="config.json")
    parser.add_argument("--last", help="number of last events to check", default="10", type=int)
    parser.add_argument("--eventid", help="for downloading declarations before this event", type=int)
    return parser.parse_args(sys.argv[1:])


def evaluate_reputations(args):
    logging.warning("Running in general repuptatons counting mode")
    reputation = Evaluator(configuration, fetch, args.last).evaluate_by_events(Reputation)
    result_file_name = "result.csv"
    ReputationDumper(result_file_name, reputation).dump_to_csv()


def fetch_single_event(args):
    logging.warning("Running in declarations fetching mode, event={}".format(args.eventid))
    attendances = fetch.attendance_list(args.eventid)
    result_file_name = "{0}-{1}.csv".format(args.meetup, args.eventid)
    DeclarationsDumper(result_file_name, attendances).dump_to_csv()


if __name__ == "__main__":
    args = read_args()
    fetch = MeetupFetcher(args.meetup)
    configuration = JsonFileConfig(args.config)
    configuration.load()

    if hasattr(args, 'eventid') and args.eventid:
        fetch_single_event(args)
    else:
        evaluate_reputations(args)
