import argparse
import logging
import os
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
    parser.add_argument("--eventid", help="for downloading declarations for this event", type=int)
    parser.add_argument("-d", help="fetch declarations to temporal files if not fetched yet", action='store_true')
    return parser.parse_args(sys.argv[1:])


def evaluate_reputations(args):
    # TODO do it using temporal files with declarations
    logging.warning("Running in general repuptatons counting mode")
    reputation = Evaluator(configuration, fetch, args.last).evaluate_by_events(Reputation)
    result_file_name = "result.csv"
    ReputationDumper(result_file_name, reputation).dump_to_csv()


def fetch_single_event(event_id, result_file_name):
    logging.warning("Running in declarations fetching mode, event={}".format(event_id))
    attendances = fetch.attendance_list(event_id)
    DeclarationsDumper(result_file_name, attendances).dump_to_csv()


def meetup_event_file_name(meetup_name, event_id):
    return "{0}-{1}.csv".format(meetup_name, event_id)


if __name__ == "__main__":
    args = read_args()
    fetch = MeetupFetcher(args.meetup)
    configuration = JsonFileConfig(args.config)
    configuration.load()

    if hasattr(args, 'eventid') and args.eventid:
        fetch_single_event(args.eventid, meetup_event_file_name(args.meetup, args.eventid))
    elif hasattr(args, "d"):
        for event_id in fetch.upcoming_ids_in_time_deltas_range():
            logging.warning(event_id)
            result_file_name = meetup_event_file_name(args.meetup, event_id)
            logging.warning(result_file_name)
            if not os.path.exists(result_file_name):
                fetch_single_event(event_id, result_file_name)
            else:
                logging.warning("Declarations data for event %a already dumped to file", event_id)
    else:
        evaluate_reputations(args)
