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

import psh

ssh = psh.Program("ssh", _defer=False)
tmux = psh.Program("tmux", _defer=False)

# TODO: include master config
# TODO: run slaves with user config
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


def create_session(session, hosts):
    commands = itertools.chain.from_iterable(
        ("; " + command).split(" ") for command in MASTER_CONFIG)

    if tmux("has-session", _ok_statuses=(0,1)).status():
        tmux("new-session", "-d", "-s", session, *commands)
        existing_windows = set()
    else:
        existing_windows = set(
            window.strip() for window in tmux(
                "list-windows", "-t", session, "-F", "#{window_name}", _defer=True))

    for host in hosts:
        if host in existing_windows:
            continue

        tmux("new-window", "-t", session, "-n", host,
            "ssh -t {host} 'tmux has-session -t {session} && exec tmux attach-session -t {session} || exec tmux new-session -s {session}'".format(
                host=host, session=session))

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

    return parser.parse_args()


def main():
    args = parse_args()

    if args.kill:
        kill_session(args.session, args.hosts)
    else:
        create_session(args.session, args.hosts)


if __name__ == "__main__":
    main()
