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

email = render.render_template('templates/email.txt', date, mail=config['mail'])
if dry_run:
    print email
if not dry_run:
    p = subprocess.Popen(['mutt', '-H', '-'], stdin=subprocess.PIPE)
    p.communicate(email)
