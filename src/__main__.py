#!/usr/bin/env python3
"""
TIAS - Terra Invicta Advisory System

Main entry point for the modular command system.
"""

import argparse
import sys

# Python version check
if sys.version_info < (3, 11):
    print("ERROR: Python 3.11+ required")
    print(f"Current version: {sys.version}")
    print("Please upgrade Python and try again.")
    sys.exit(1)

# Import core utilities
from src.core.core import setup_logging

# Import command functions
from src.clean.command import cmd_clean
from src.install.command import cmd_install
from src.build.command import cmd_build
from src.validate.command import cmd_validate
from src.perf.command import cmd_perf
from src.parse.command import cmd_parse
from src.stage.command import cmd_stage
from src.inject.command import cmd_inject
from src.run.command import cmd_run


def main():
    parser = argparse.ArgumentParser(description='Terra Invicta Advisory System')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Increase verbosity (-v INFO, -vv DEBUG)')

    subparsers = parser.add_subparsers(dest='command', help='Command')

    subparsers.add_parser('install',  help='Interactive setup (auto-detect paths)')
    subparsers.add_parser('clean',    help='Remove build directory')
    subparsers.add_parser('build',    help='Build templates database')
    subparsers.add_parser('validate', help='Validate configuration and paths')
    subparsers.add_parser('perf',     help='Display performance statistics')
    subparsers.add_parser('stage',    help='Assemble actor context files at current tier')

    parse_parser = subparsers.add_parser('parse', help='Parse savegame')
    parse_parser.add_argument('--date', required=True, help='Date (YYYY-M-D or YYYY-MM-DD or DD/MM/YYYY)')

    inject_parser = subparsers.add_parser('inject', help='Generate LLM context from game state')
    inject_parser.add_argument('--date', required=True, help='Date (YYYY-M-D or YYYY-MM-DD or DD/MM/YYYY)')

    run_parser = subparsers.add_parser('run', help='Launch KoboldCpp')
    run_parser.add_argument('--date', required=True, help='Date (YYYY-M-D or YYYY-MM-DD or DD/MM/YYYY)')
    run_parser.add_argument('--quality', choices=['base', 'max', 'nuclear', 'ridiculous', 'ludicrous'],
                            help='Model quality tier (default: base or KOBOLDCPP_QUALITY from .env)')

    args = parser.parse_args()

    setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        'install':  cmd_install,
        'clean':    cmd_clean,
        'build':    cmd_build,
        'validate': cmd_validate,
        'perf':     cmd_perf,
        'parse':    cmd_parse,
        'stage':    cmd_stage,
        'inject':   cmd_inject,
        'run':      cmd_run,
    }

    commands[args.command](args)


if __name__ == '__main__':
    main()
