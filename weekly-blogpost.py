#!/usr/bin/env python
# encoding: utf-8

import render
import os
import sys
import xmlrpclib
import subprocess
import datetime
import yaml
import settings

config = settings.load_settings()

dry_run = False

args = sys.argv[1:]
if args[0] == '-n':
    dry_run = True
    args = args[1:]

date = args[0]

debts = render.get_debts()

text = render.render_template('templates/week.tmpl', date)
if dry_run:
    print >>sys.stderr, "Dry run only, not posting:"
    print text
else:
    lines = text.split("\n")
    title = lines[0]
    body  = "\n".join(lines[1:])

    page = dict(title = title, description = body)

    passwd = config['password']

    x = xmlrpclib.ServerProxy(config['xmlrpc_endpoint'])
    x.metaWeblog.newPost(config['blog_id'], config['username'], passwd, page, config['publish'])
    if config['publish']:
        print >>sys.stderr, "Posted new entry for %s" % date
    else:
        print >>sys.stderr, "Created new draft for %s" % date
