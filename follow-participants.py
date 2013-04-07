#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import yaml
import datetime
import dateutil
import dateutil.parser
import dateutil.relativedelta
import tweepy

import settings
from ironblogger import *


def evaluate_users(users, **kwargs):
    week = dateutil.parser.parse('monday') + dateutil.relativedelta.relativedelta(weeks=-1)
    week = (week - START).days / 7
    week_start = START + (week * datetime.timedelta(7))
    week_end = START + ((week + 1) * datetime.timedelta(7))

    follow = []
    unfollow = []

    for (user, data) in users.items():
        user = user.lower()
        if data.get('twitter', True) == False:  # user is not on twitter
            continue
        if should_skip(data.get('skip', []), week):  # user is skipping
            continue
        if data.get('stop'):  # user has stopped
            unfollow.append(user)
            continue
        if data.get('end') and dateutil.parser.parse(data.get('end'), default=START) <= week_end:  # user has ended
            unfollow.append(user)
            continue
        if data.get('punt') and data.get('end') and dateutil.parser.parse(data.get('end'), default=START) <= week_end:  # user has punted
            unfollow.append(user)
            continue
        if dateutil.parser.parse(data.get('start'), default=START) > week_start:  # user hasn’t started yet
            continue

        follow.append(user)

    return (follow, unfollow)


if __name__ == '__main__':
    config = settings.load_settings()

    START = datetime.datetime.strptime(config['start_date'], "%Y/%m/%d")

    parser = argparse.ArgumentParser(
        description='Follow participants on twitter.')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Dry run (do not send tweets).')
    args = parser.parse_args()

    users = yaml.safe_load(file('bloggers.yml', 'r'))

    (follow, unfollow) = evaluate_users(users)

    if args.dry_run:
        print('--- Dry run. ---')
        print('')

    print('Want to follow:')
    print('  ' + ', '.join(follow))
    print('Want to not follow:')
    print('  ' + ', '.join(unfollow))

    if not args.dry_run:
        auth = tweepy.OAuthHandler(
            config['consumer_key'], config['consumer_secret'])
        auth.set_access_token(
            config['access_token'], config['access_token_secret'])

        api = tweepy.API(auth)

        try:
            print("Fetching current followings…")
            already_following = set([u.screen_name.lower() for u in tweepy.Cursor(api.friends).items()])
            print("Currently following %d users." % len(already_following))
            will_follow = set(follow) - already_following
            will_unfollow = set(unfollow) & already_following

            print("Will follow %d users." % len(will_follow))
            for user in will_follow:
                try:
                    print('+ %s' % user)
                    api.create_friendship(user)
                except tweepy.error.TweepError as e:
                    print("Error calling Twitter: %s" % e)

            print("Will unfollow %d users." % len(will_unfollow))
            for user in will_unfollow:
                try:
                    print('- %s' % user)
                    api.destroy_friendship(user)
                except tweepy.error.TweepError as e:
                    print("Error calling Twitter: %s" % e)
        except tweepy.error.TweepError as e:
            print("Error calling Twitter: %s" % e)
