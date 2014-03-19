#!/usr/bin/env python

"""
A tool that runs a master tmux session to control slave tmux sessions on the
specified hosts.
"""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import itertools
import os
import re

import psh

ssh = psh.Program("ssh", _defer=False)
tmux = psh.Program("tmux", _defer=False)

MASTER_CONFIG = (
    # Use C-a as a prefix key in master session
    "set prefix C-a",
    "unbind-key C-b",
    "bind-key C-a send-prefix",

    # Windows should be named after their host names
    "set-option -g allow-rename off",

    # To see errors when we fail to open a session on a host
    "set-option -g set-remain-on-exit on",
)


def get_user_config():
    config_path = os.path.expanduser("~/.tmux.conf")

    if not os.path.exists(config_path):
        return ""

    with open(config_path) as config:
        return config.read()


def create_slave_session(session, host, user_config):
    if user_config:
        temp_file = ssh(host,
            'temp_file="$(mktemp)" && echo "$temp_file" && cat > "$temp_file"',
            _stdin=user_config).stdout().strip()
        slave_commands = r'\; source-file "{}"'.format(temp_file)
        cleanup_commands = 'rm -f "{}";'.format(temp_file)
    else:
        slave_commands = ""
        cleanup_commands = ""

    tmux("new-window", "-t", session, "-n", host, "ssh -t {host} '"
        'tmux has-session -t {session} || tmux new-session -d -s "{session}" {slave_commands}; '
        '{cleanup_commands} exec tmux attach-session -t "{session}"\''.format(
            host=host, session=session, slave_commands=slave_commands, cleanup_commands=cleanup_commands))


def create_master_session(session, hosts):
    master_config = list(MASTER_CONFIG)
    master_config_path = os.path.expanduser("~/.tmux-master.conf")
    if os.path.exists(master_config_path):
        master_config.append("source-file {}".format(master_config_path))

    commands = itertools.chain.from_iterable(
        ("; " + command).split(" ") for command in master_config)

    if tmux("has-session", _ok_statuses=(0,1)).status():
        tmux("new-session", "-d", "-s", session, "-n", "master", *commands)
        existing_windows = set()
    else:
        existing_windows = set(
            window.strip() for window in tmux(
                "list-windows", "-t", session, "-F", "#{window_name}", _defer=True))

    user_config = get_user_config()

    for host in hosts:
        if host not in existing_windows:
            create_slave_session(session, host, user_config)

    tmux("select-window", "-t", session + ":0")
    os.execlp("tmux", "tmux", "attach-session", "-t", session)


def kill_session(session, hosts):
    for host in hosts:
        ssh(host, "! tmux has-session -t {session} 2>/dev/null || tmux kill-session -t {session}".format(session=session))

    if not tmux("has-session", _ok_statuses=(0,1)).status():
        tmux("kill-session", "-t", session)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.strip().replace("\n", " "))

    parser.add_argument("-s", "--session", metavar="name", required=True, help="session name")
    parser.add_argument("-k", "--kill", action="store_true", help="kill the session")
    parser.add_argument("hosts", nargs="+", help="host names")

    args = parser.parse_args()

    if re.search("^[-_.a-zA-Z0-9]+$", args.session) is None:
        parser.error("Invalid session name.")

    return args


def main():
    args = parse_args()

    if args.kill:
        kill_session(args.session, args.hosts)
    else:
        create_master_session(args.session, args.hosts)


if __name__ == "__main__":
    main()
