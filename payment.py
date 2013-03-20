#!/usr/bin/env python

import sys
import argparse
import yaml
from datetime import datetime

parser = argparse.ArgumentParser(description='Handle iron blogger payments.')
parser.add_argument('name', type=str, help='name or handle')
parser.add_argument('amount', type=int, help='amount paid')
parser.add_argument('-t', metavar='TEXT', type=str, help='booking text', default='Payment', required=False)
args = parser.parse_args()

users = yaml.safe_load(file('bloggers.yml', 'r'))

matches = [key for key, v in users.iteritems() if args.name.lower() in key.lower() or args.name.lower() in v['name'].lower()]
if len(matches) != 1:
  print("Given name matches multiple bloggers: %s" % ', '.join(matches))
  print("Please be more specific!")
  sys.exit(-1)

s = '''%(date)s %(text)s
  Pool:Owed:%(name)s    $-%(amount)d
  Pool:Paid''' % { 'date': datetime.now().strftime('%Y-%m-%d'), 'text': args.t, 'name': matches[0], 'amount': args.amount }

print(s)
with open('ledger', 'a') as f:
    f.write("\n")
    f.write(s)
