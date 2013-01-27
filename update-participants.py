#!/usr/bin/env python

import render
import os
import sys
import xmlrpclib
import subprocess
import settings

config=settings.load_settings()

try:
    subprocess.call(['stty', '-echo'])
    passwd = raw_input("Password for %s: " % (config['username'],))
    print
finally:
    subprocess.call(['stty', 'echo'])

x = xmlrpclib.ServerProxy(config['xmlrpc_endpoint'])
page = x.wp.getPage(config['blog_id'], config['participants_page_id'], config['username'], passwd)

text = render.render_template('templates/users.tmpl')
page['description'] = text

x.wp.editPage(config['blog_id'], config['participants_page_id'], config['username'], passwd,page,True)