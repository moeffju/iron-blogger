#!/usr/bin/python
import render
import os
import sys
import xmlrpclib
import subprocess

XMLRPC_ENDPOINT = 'http://iron-blogger.mit.edu/xmlrpc.php'
USER            = 'nelhage'
BLOG_ID         = 1

try:
    subprocess.call(['stty', '-echo'])
    passwd = raw_input("Password for %s: " % (USER,))
    print
finally:
    subprocess.call(['stty', 'echo'])

x = xmlrpclib.ServerProxy(XMLRPC_ENDPOINT)

text = render.render_template('templates/week.tmpl', sys.argv[1])

lines = text.split("\n")
title = lines[0]
body  = "\n".join(lines[1:])

page = dict(title = title,
            description = body)

x.metaWeblog.newPost(BLOG_ID, USER, passwd, page, True)