#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
import sys
import cmd
import os.path

# fix auto completion on macintosh
import readline
if 'libedit' in readline.__doc__:
    import rlcompleter
    readline.parse_and_bind("bind ^I rl_complete")

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

__author__ = 'Kang Li<i@likang.me>'
__version__ = '0.1'


conf_path = os.path.expanduser('~/.ucloudrc')


class Terminal(cmd.Cmd):
    def __init__(self, options, completekey='tab', stdin=None, stdout=None):
        self.options = options
        self.prompt = 'upyun > '
        self.vocab = ['status', 'create_u_host_instance'
                      'quit', 'help']

        cmd.Cmd.__init__(self, completekey, stdin, stdout)


def load_options():
    if not os.path.exists(conf_path):
        print("Sorry but I can't find the config file. Please fill the "
              "following template and save it to %s" % conf_path)
        print("""
; Sample UCloud config file

[ucloud]
public_key=
private_key=
default_region=cn-north-01
""")
        sys.exit(2)
    options = ConfigParser()
    with open(conf_path, 'r') as f:
        options.readfp(f)
    return options


def check_keys(options):
    pass


def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print ('usage: ucloud-cli')
        print ('usage: ucloud-cli command [option ...]')
        sys.exit()

    _options = load_options()
    check_keys(_options)

if __name__ == '__main__':
    main()
