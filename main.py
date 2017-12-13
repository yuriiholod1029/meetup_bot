import argparse
import logging
import sys

from config import JsonFileConfig
from evaluator import Evaluator
from dumper import Dumper
from fetcher import MeetupFetcher
from reputation import Reputation


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--meetup", help="meetup name", default="AgileWarsaw")
    parser.add_argument("--config", help="config file name", default="config.json")
    parser.add_argument("--last", help="number of last events to check", default="10", type=int)
    parser.add_argument("--eventid", help="for downloading declarations before this event", type=int)
    args = parser.parse_args(sys.argv[1:])

    fetch = MeetupFetcher(args.meetup)
    configuration = JsonFileConfig(args.config)
    configuration.load()

    if hasattr(args, 'eventid') and args.eventid:
        logging.warning("Running in declarations fetching mode, event={}".format(args.eventid))
        reputation = Evaluator(configuration, fetch).evaluate_single_event(Reputation, args.eventid)
        result_file_name = "{0}-{1}".format(args.meetup, args.eventid)
    else:
        logging.warning("Running in general repuptatons counting mode")
        reputation = Evaluator(configuration, fetch, args.last).evaluate_by_events(Reputation)
        result_file_name = "result.csv"

    Dumper(result_file_name, reputation).dump_to_csv()
