#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings

import sys
import os
import subprocess

import argparse

import yaml
import datetime
import dateutil
import dateutil.parser

import tweepy


def parse_skip(rec):
  spec = rec.get('skip', [])
  out = []
  for s in spec:
    if isinstance(s, list):
      out.append(map(to_week_num, s))
    else:
      out.append(to_week_num(s))
  return out


def should_skip(skips, week):
  for e in skips:
    if e == week:
      return True
    if isinstance(e, list) and e[0] <= week and e[1] > week:
      return True
  return False


def get_debts():
  p = subprocess.Popen(['ledger', '-f', os.path.join(HERE, 'ledger'), '-n', 'balance', 'Pool:Owed:'], stdout=subprocess.PIPE)
  (out, _) = p.communicate()
  debts = []
  for line in out.split("\n"):
    if not line: continue
    (val, acct) = line.split(None, 1)
    user = acct[len("Pool:Owed:"):]
    val  = int(val[len("$"):])
    debts.append((user, val))
  return debts


def evaluate_users(users, report, **kwargs):
  week = START
  week = (week - START).days / 7
  week_start = START + (week * datetime.timedelta(7))
  week_end   = START + ((week + 1) * datetime.timedelta(7))

  punted = []
  has_blogged = []
  has_not_blogged = []

  for (user, data) in users.items():
    if data.get('stop'):
      # user has stopped
      continue
    if data.get('end') and dateutil.parser.parse(data.get('end'), default=START) <= week_start:
      # user has ended
      continue
    if should_skip(data.get('skip', []), week):
      # user is skipping
      continue
    if data.get('punt') and data.get('end') and dateutil.parser.parse(data.get('end'), default=START) <= week_start:
      # user has punted
      punted.append(user)
      continue
    user_start = dateutil.parser.parse(data.get('start'), default=START)
    if user_start > week_start:
      # user hasn’t started yet
      continue

    weeks = report.get(user, [])
    if len(weeks) <= week or not weeks[week]:
      has_not_blogged.append(user)
    else:
      has_blogged.append(user)

  return {'has_not_blogged': has_not_blogged, 'has_blogged': has_blogged, 'punted': punted}


config = settings.load_settings()

START = datetime.datetime.strptime(config['start_date'], "%Y/%m/%d")
HERE  = os.path.dirname(__file__)


parser = argparse.ArgumentParser(description='Notify participants of things.')
parser.add_argument('--about', metavar='MODE', type=str, choices=['blog', 'payment'], default='blog', help='What to notify people about (blog or payment).')
parser.add_argument('-n', '--dry-run', action='store_true', help='Dry run (do not send tweets).')
parser.add_argument('--blog-message', metavar='MSG', type=str, default='%(users)s This is a friendly reminder that you haven’t blogged yet this week.', help='What to tell people who haven’t blogged yet.')
parser.add_argument('--payment-message', metavar='MSG', type=str, default='@%(user)s Your current iron blogging debt is €%(amount)d.', help='What to tell people who owe money.')
parser.add_argument('--punt-message', metavar='MSG', type=str, default='@%(user)s Strike 6, you’re out! Pay €%(amount)d to return.', help='What to tell people who punted.')
args = parser.parse_args()

if args.dry_run:
  print("(Dry run, not sending any tweets.)")

if not args.dry_run:
  auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
  auth.set_access_token(config['access_token'], config['access_token_secret'])

  api = tweepy.API(auth)

users = yaml.safe_load(file('bloggers.yml', 'r'))
report = yaml.safe_load(file('out/report.yml', 'r'))

debts = get_debts()
results = evaluate_users(users, report)

if args.about == 'blog':
  targets = ['@' + x for x in results['has_not_blogged']]
  while len(targets) > 0:
    batch = []
    while len(targets) > 0 and len(args.blog_message % {'users': ' '.join(batch + [targets[0]])}) <= 140:
      batch.append(targets.pop(0))
    tweet = args.blog_message % {'users': ' '.join(batch)}

    print tweet
    if not args.dry_run:
      api.update_status(status=tweet)

elif args.about == 'payment':
  for user, amount in debts:
    tweet = args.payment_message % {'user':user, 'amount':amount}

    print tweet
    if not args.dry_run:
      api.update_status(status=tweet)

  for user in results['punted']:
    tweet = args.punt_message % {'user':user, 'amount':30}

    print tweet
    if not args.dry_run:
      api.update_status(status=tweet)
