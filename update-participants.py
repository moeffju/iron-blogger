#!/usr/bin/env python

import render
import os
import sys
import xmlrpclib
import subprocess
import settings

config=settings.load_settings()

try:
  x = xmlrpclib.ServerProxy(config['xmlrpc_endpoint'])
  page = x.wp.getPage(config['blog_id'], config['participants_page_id'], config['username'], config['password'])

  text = render.render_template('templates/users.tmpl')
  page['description'] = text

  success = x.wp.editPage(config['blog_id'], config['participants_page_id'], config['username'], config['password'], page, True)
  if success:
    print >>sys.stderr, "Page %s updated." % config['participants_page_id']
  else:
    print >>sys.stderr, "Could not updated page %s. Check your settings." % config['participants_page_id']

except Exception as e:
  print >>sys.stderr, "Exception: %s" % e
