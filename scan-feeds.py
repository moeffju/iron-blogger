#!/usr/bin/env python
import yaml
import feedparser
import datetime
import sys
import os
from dateutil.parser import parse
import dateutil.tz as tz
import settings

config=settings.load_settings()

with open('bloggers.yml') as f:
    users = yaml.safe_load(f.read())

if not os.path.exists('out'):
    os.makedirs('out')
try:
    with open('out/report.yml') as f:
        log = yaml.safe_load(f.read())
except IOError:
    log = {}

START = datetime.datetime.strptime(config['start_date'],'%Y/%m/%d')

def parse_published(pub):
    try:
        return parse(pub).astimezone(tz.tzlocal()).replace(tzinfo=None)
    except:
        return parse(pub).replace(tzinfo=None)
def get_date(post):
    for k in ('published', 'created', 'updated'):
        if k in post:
            return post[k]
    raise ValueError

def get_link(post):
    return post.link

def parse_feeds(weeks, uri):
    print >>sys.stderr, "Parsing: %s" % uri

    feed = feedparser.parse(uri)

    if feed['bozo']:
        print >>sys.stderr, "WARN: BOZO, check <http://feedvalidator.org/check.cgi?url=%s>: %s" % (uri, feed['bozo_exception'])

    if not feed.entries:
        print >>sys.stderr, "WARN: no entries for %s" % uri

    try:
        if weeks is None:
            weeks = []

        for post in feed.entries:
            date = parse_published(get_date(post))

            if date < START:
                continue
            wn = (date - START).days / 7

            while len(weeks) <= wn:
                weeks.append([])

            if post.has_key('title'):
                post = dict(date=date,
                            title=post.title,
                            url=get_link(post))
            if not post.has_key('title'):
                post = dict(date=date,
                            title="",
                            url=get_link(post))
            if post['url'] not in [p['url'] for p in weeks[wn]]:
                weeks[wn].append(post)

            #print >>sys.stderr, "  %s (week %d) <%s>" % (post['date'], wn, post['url'])
    except Exception as e:
        print >>sys.stderr, "ERROR: Couldn't parse feed. Check http://feedvalidator.org/check.cgi?url=%s" % uri
        print >>sys.stderr, str(e)

if len(sys.argv) > 1:
    for username in sys.argv[1:]:
        weeks = log.setdefault(username, [])
        for l in users[username]['links']:
            parse_feeds(weeks, l[2])
else:
    for (username, u) in users.items():
        weeks = log.setdefault(username, [])
        for l in u['links']:
            parse_feeds(weeks, l[2])

with open('out/report.yml', 'w') as f:
    yaml.safe_dump(log, f)
