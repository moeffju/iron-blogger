#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import datetime
import os

import settings


config = settings.load_settings()
START = datetime.datetime.strptime(config['start_date'],"%Y/%m/%d")


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
    p = subprocess.Popen(['ledger', '-f', os.path.join(os.path.dirname(__file__), 'ledger'), '-n', 'balance', 'Pool:Owed:'], stdout=subprocess.PIPE)
    (out, _) = p.communicate()
    debts = []
    for line in out.split("\n"):
        if not line:
            continue
        (val, acct) = line.split(None, 1)
        user = acct[len("Pool:Owed:"):]
        val = int(val[len("$"):])
        debts.append((user, val))
    return debts


def get_balance(acct):
    p = subprocess.Popen(['ledger', '-f', os.path.join(os.path.dirname(__file__), 'ledger'), '-n', 'balance', acct], stdout=subprocess.PIPE)
    (out, _) = p.communicate()
    try:
        return int(out.split()[0][1:])
    except:
        return 0


def to_week_num(date):
    return (parse(date, default=START) - START).days / 7
