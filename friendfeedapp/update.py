#!/usr/bin/env python

import friendfeed
import os
from optparse import OptionParser

os.environ['DJANGO_SETTINGS_MODULE'] = 'friendfeedstats.settings'
from friendfeedapp.utils import get_or_create_from_entry

parser = OptionParser()
parser.add_option('-c', '--continuous', action = 'store_true', dest = 'continuous', default = False)
parser.add_option('-n', '--num', action = 'store', type = 'int', dest='num', default = 30)
parser.add_option('-s', '--start', action = 'store', type = 'int', dest='start', default = 0)
parser.add_option('-t', '--times', action = 'store', type = 'int', dest='times', default = 1)
parser.add_option('-u', '--update', action = 'store_true', dest = 'update_new_ffusers', default = False)
parser.add_option('-v', '--verbose', action = 'store_true', dest = 'verbose', default = False)
options, args = parser.parse_args()

service = friendfeed.FriendFeed()

start = options.start

if options.continuous:
    done = False
    while True:
        for entry in service.fetch_public_feed(start = start, num = options.num)['entries']:
            results = get_or_create_from_entry(entry)
            if options.verbose:
                print results
            ffuser = results[0]
            ffuser_created = results[1]
            if ffuser_created and options.update_new_ffusers:
                ffuser.update(options.verbose)
            entry_created = results[5]
            if not entry_created and not entry['likes'] and not entry['comments']:
                done = True
                break
        if done:
            break
        start += options.num
else:
    for time in range(options.times):
        for entry in service.fetch_public_feed(start = start, num = options.num)['entries']:
            results = get_or_create_from_entry(entry)
            if options.verbose:
                print results
            ffuser = results[0]
            ffuser_created = results[1]
            if ffuser_created and options.update_new_ffusers:
                ffuser.update(options.verbose)
        start += options.num
