#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
import json
import sys
import cmd
import urllib
import hashlib
import os.path
import urllib2
import contextlib
from ConfigParser import ConfigParser


__author__ = 'Kang Li<i@likang.me>'
__version__ = '0.1'


class Terminal(cmd.Cmd):
    def __init__(self, completekey='tab', stdin=None, stdout=None):
        self.prompt = 'UCloud > '
        self.vocab = ['status', 'quit', 'help']
        self.fix_auto_completion()

        cmd.Cmd.__init__(self, completekey, stdin, stdout)

    @staticmethod
    def fix_auto_completion():
        """ fix auto completion on macintosh """
        import readline
        if 'libedit' in readline.__doc__:
            __import__('rlcompleter')
            readline.parse_and_bind("bind ^I rl_complete")


class UCloud(object):
    def __init__(self, action):
        self.action = action
        self.params = dict(PublicKey=options.public_key, Action=action)

    def __call__(self, **kwargs):
        self.params.update(kwargs)
        self.sign(self.params, options.private_key)
        return self.request()

    def request(self):
        url = options.base_url + '?' + urllib.urlencode(self.params)
        with contextlib.closing(urllib2.urlopen(url)) as r:
            resp = r.read()
            resp = json.loads(resp)
        print(resp)

    @staticmethod
    def sign(params, private_key):
        sign_str = ''.join(key+params[key] for key in sorted(params.keys()))
        sign_str += private_key
        params['Signature'] = hashlib.sha1(sign_str).hexdigest()


class Options(ConfigParser):
    """ parse and save options """

    def __getattr__(self, item):
        return self.get('ucloud', item)

    def parse(self, fn):
        if not os.path.exists(fn):
            print("Sorry but I can't find the config file. Please fill the "
                  "following template and save it to %s" % fn)
            print("""
; Sample UCloud config file

[ucloud]
public_key=
private_key=
base_url=https://api.ucloud.cn
""")
            sys.exit(2)
        with open(fn, 'r') as f:
            self.readfp(f)

    @staticmethod
    def check():
        u = UCloud('DescribeBucket')
        u()


options = Options()
conf_path = os.path.expanduser('~/.ucloudrc')


def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print ('usage: ucloud-cli')
        print ('usage: ucloud-cli command [option ...]')
        sys.exit()

    options.parse(conf_path)
    options.check()


if __name__ == '__main__':
    main()
