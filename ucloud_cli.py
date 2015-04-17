#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
import json
import sys
import cmd
import shlex
import urllib
import hashlib
import os.path
import urllib2
import contextlib
from ConfigParser import ConfigParser


__author__ = 'Kang Li<i@likang.me>'
__version__ = '0.1'


class Terminal(cmd.Cmd):
    """ UCloud line-oriented command interpreter """
    doc_path = os.path.join(os.path.dirname(__file__), 'doc.json')

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        self.prompt = 'UCloud > '
        self.region = None
        self.fix_auto_completion()

        with open(self.doc_path) as d:
            self.doc = json.loads(d.read())

        cmd.Cmd.__init__(self, completekey, stdin, stdout)

    def gen_action(self, action):
        """ Generate do_xx(command) dynamically  """
        def do_action(line):
            args = dict(self.split_args(line))
            if self.region and 'Region' in self.doc[action]:
                args['Region'] = self.region

            ucloud = UCloud(action)
            try:
                resp = ucloud(**args)
                self.output(json.dumps(resp, indent=4, ensure_ascii=False))
            except Exception as e:
                self.output(str(e))
        return do_action

    def do_help(self, arg):
        pass

    def output(self, stuff):
        self.stdout.write(stuff + '\n')

    def completenames(self, text, *ignored):
        """ All command names  """
        do_text = 'do_'+text
        names = [a[3:] for a in self.get_names() if a.startswith(do_text)]
        return names + [a for a in self.doc.keys() if a.startswith(text)]

    def emptyline(self):
        return None

    def welcome(self):
        """ Print logo generated with font Sub-Zero """
        self.output(r"""
 __  __     ______     __         ______     __  __     _____
/\ \/\ \   /\  ___\   /\ \       /\  __ \   /\ \/\ \   /\  __-.
\ \ \_\ \  \ \ \____  \ \ \____  \ \ \/\ \  \ \ \_\ \  \ \ \/\ \
 \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \____-
  \/_____/   \/_____/   \/_____/   \/_____/   \/_____/   \/____/
""")

    def do_quit(self, _):
        """ Quit when we got command quit/exit or Control-D """
        self.output('')
        sys.exit(0)

    do_EOF = do_exit = do_quit

    def __getattr__(self, item):
        """ Inject do_xxx action into Terminal """
        if item.startswith('do_'):
            action = item[3:]
            if action in self.doc:
                setattr(self, item, self.gen_action(action))
                return getattr(self, item)
        raise AttributeError("'Terminal' object has no attribute '%s'" % item)

    @staticmethod
    def split_args(line):
        raw_args = [arg.split('=', 1) for arg in shlex.split(line)]
        return [tuple(arg) for arg in raw_args if len(arg) == 2]


    @staticmethod
    def fix_auto_completion():
        """ fix auto completion on macintosh """
        import readline
        if 'libedit' in readline.__doc__:
            __import__('rlcompleter')
            readline.parse_and_bind("bind ^I rl_complete")


class UCloud(object):
    """ UCloud API Client """
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
        return resp

    @staticmethod
    def sign(params, private_key):
        sign_str = ''.join(key+params[key] for key in sorted(params.keys()))
        sign_str += private_key
        params['Signature'] = hashlib.sha1(sign_str).hexdigest()


class Options(ConfigParser):
    """ parse and save options """
    conf_path = os.path.expanduser('~/.ucloudrc')

    def __getattr__(self, item):
        return self.get('ucloud', item)

    def load(self):
        if not os.path.exists(self.conf_path):
            print("Sorry but I can't find the config file. Please fill the "
                  "following template and save it to %s" % self.conf_path)
            print("""
; Sample UCloud config file

[ucloud]
public_key=
private_key=
base_url=https://api.ucloud.cn
""")
            sys.exit(2)
        with open(self.conf_path, 'r') as f:
            self.readfp(f)


options = Options()


def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print ('usage: ucloud-cli')
        print ('usage: ucloud-cli command [option ...]')
        sys.exit()

    options.load()

    terminal = Terminal()
    try:
        terminal.welcome()
        terminal.cmdloop()
    except KeyboardInterrupt:
        print('')


if __name__ == '__main__':
    main()
