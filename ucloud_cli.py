#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
import sys
import cmd
import json
import shlex
import urllib
import hashlib
import os.path
import urllib2
import contextlib
from functools import partial
from prettytable import PrettyTable
from ConfigParser import ConfigParser


__author__ = 'Kang Li<i@likang.me>'
__version__ = '0.1'


class Terminal(cmd.Cmd):
    """ UCloud line-oriented command interpreter """

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        self.region = options.region
        self.regions = ['cn-north-01', 'cn-north-02', 'cn-north-03', 'cn-east-01',
                        'cn-south-01', 'hk-01', 'us-west-01']
        self.doc = dict()
        self.load_doc()

        self.postcmd(0, 0)
        self.fix_auto_completion()
        cmd.Cmd.__init__(self, completekey, stdin, stdout)

    def load_doc(self):
        """ Load doc from doc.json and generate do_*() and complete_*()  """

        conf_file = os.path.join(os.path.dirname(__file__), 'doc.json')

        with open(conf_file) as d:
            self.doc = json.loads(d.read())

        for action in self.doc:
            # generate complete_*()
            complete_func = partial(self._complete_action, action)
            setattr(Terminal, 'complete_' + action, complete_func)

            # generate do_*()
            do_func = partial(self._do_action, action)
            do_func.__doc__ = self._pretty_doc(action)
            setattr(Terminal, 'do_' + action, do_func)

    def _pretty_doc(self, action):
        """ Generate __doc__ for do_*()  """
        doc_action = self.doc[action]
        sort_func = lambda x, y: doc_action[x]['Order'] < doc_action[y]['Order']

        doc_table = PrettyTable(['Parameter', 'Type', 'Required', 'Description'])
        for field_name in doc_table.field_names:
            doc_table.align[field_name] = 'l'
        for param in sorted(doc_action.keys(), cmp=sort_func):
            params_info = doc_action[param]
            doc_table.add_row([param,
                               params_info['Type'],
                               ('No', 'Yes')[int(params_info['Required'])],
                               params_info['Desc']])
        return doc_table.get_string().encode('utf-8')

    def do_region(self, region):
        """  Set default region """

        if region not in self.regions:
            self.output('Invalid region: %s' % region)
            return

        self.region = region
        options.save(region=region)

    def complete_region(self, *args):
        return [r for r in self.regions if r.startswith(args[0])]

    def _complete_action(self, action, *args):
        pass

    def _do_action(self, action, line):
        args = dict(self.split_args(line))
        if self.region and 'Region' in self.doc[action]:
            args['Region'] = self.region

        try:
            resp = UCloud(action)(**args)
            self.output(json.dumps(resp, indent=4, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.output(str(e))

    def postcmd(self, stop, line):
        self.prompt = 'UCloud %s> ' % ((self.region + ' ') if self.region else '')

    def output(self, stuff):
        self.stdout.write(stuff + '\n')

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

    def save(self, **kwargs):
        for key, value in kwargs.items():
            self.set('ucloud', key, value)

        with open(self.conf_path, 'wb') as f:
            self.write(f)

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
