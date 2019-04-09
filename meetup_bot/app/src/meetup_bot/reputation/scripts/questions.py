from collections import defaultdict, Counter
import csv

from meetup_bot.app.src.meetup_bot.reputation.fetcher import MeetupFetcher
from meetup_bot.app.src.meetup_bot.reputation.main import read_args


if __name__ == "__main__":
    args = read_args()
    fetcher = MeetupFetcher(args.meetup, token=open('.token').read().strip())

    # >>> pprint(m[-1666][u'group_profile'][u'answers'])
    # [{u'answer': u'general',
    #   u'question': u"What are the agile subjects you'd like to hear about?",
    #   u'question_id': 3819832},
    #  {u'answer': u'przy okazji konferencji Turkusowe rEWOLUCJE',
    #   u'question': u'How did you find us?',
    #   u'question_id': 3819822},
    #  {u'answer': u'both',
    #   u'question': u'A language question: would you attend meetups in Polish, in English or both?',
    #   u'question_id': 8484196}]

    args = read_args()
    fetcher = MeetupFetcher(args.meetup, token=open('.token').read().strip())
    result = defaultdict(dict)
    members = fetcher.raw_members()
    for member in members:
        member[u'id']
        for q in member[u'group_profile'][u'answers']:
            result[member[u'id']][q[u'question']] = q.get(u'answer', '')


    LANGUAGE_QUESTION = u'A language question: would you attend meetups in Polish, in English or both?'
    language = Counter()
    with open('questions.csv', 'w', encoding='utf-8') as output_stream:  # TypeError -> you are using python2.x
        writer = csv.writer(
            output_stream,
            #lineterminator="\n",
        )
        header = [
            u'How did you find us?',
            u"What are the agile subjects you'd like to hear about?",
            u'A language question: would you attend meetups in Polish, in English or both?',
        ]
        writer.writerow(header)
        for member_id, answers in result.items():
            writer.writerow(
                [
                    member_id,
                    answers[u'How did you find us?'],
                    answers[u"What are the agile subjects you'd like to hear about?"],
                    answers[LANGUAGE_QUESTION],
                ]
            )
            language[answers[LANGUAGE_QUESTION].strip(' .,!?').lower().replace('polski', 'polish')] += 1

    for i, j in language.most_common():
        print(i, '\t', j)
