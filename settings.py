#!/usr/bin/env python

import os
import ConfigParser

def load_settings():
    configfile = ConfigParser.ConfigParser()
    configfile.read('settings.cfg')
    config = dict()

    config['mail'] = configfile.get("general", "mail")
    config['start_date'] = configfile.get("general", "start_date")

    config['username'] = configfile.get("blogsettings", "username")
    config['password'] = configfile.get("blogsettings", "password")
    config['xmlrpc_endpoint'] = configfile.get("blogsettings", "xmlrpc_endpoint")
    config['blog_id'] = configfile.get("blogsettings", "blog_id")
    config['participants_page_id'] = configfile.get("blogsettings", "participants_page_id")
    config['publish'] = True if configfile.get('blogsettings', 'publish') == "true" else False

    config['consumer_key'] = configfile.get('twitter', 'consumer_key')
    config['consumer_secret'] = configfile.get('twitter', 'consumer_secret')
    config['access_token'] = configfile.get('twitter', 'access_token')
    config['access_token_secret'] = configfile.get('twitter', 'access_token_secret')

    return config
