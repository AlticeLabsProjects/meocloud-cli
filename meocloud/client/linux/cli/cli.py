#! /usr/bin/env python
import sys
from six.moves import input
from six import print_
import os

# Horrible hack that increases all CLI to daemon timeouts by 1 second in
# order for them to be greater than daemon to core timeouts.
# This allows the CLI to detect and react to daemon timeouts.
from meocloud.client.linux.timeouts import increase_timeouts
increase_timeouts(1)

from meocloud.client.linux.logger import init_logging

from meocloud.client.linux.cli.handler import CLIHandler
from meocloud.client.linux.cli.daemon_client import DaemonClient
from meocloud.client.linux.cli import argparse3 as argparse

from meocloud.client.linux.settings import LOGGER_NAME, CLI_LOCK_PATH, DEFAULT_NOTIFS_TAIL_LINES
from meocloud.client.linux.locations import create_required_directories
from meocloud.client.linux.singleton import SingleInstance, InstanceAlreadyRunning
from meocloud.client.linux.decorators import retry, RetryFailed, TooManyRetries

# Logging
import logging

# TODO Translate all the things


@retry(max_tries=3, delay=1, backoff=2)
def start():
    instance = SingleInstance(CLI_LOCK_PATH)
    try:
        instance.start()
    except InstanceAlreadyRunning:
        raise RetryFailed()
    return instance


def main():
    if os.geteuid() == 0:
        if os.getenv('SUDO_USER') or os.getenv('SUDO_UID'):
            print_('Running meocloud under sudo might create problems since written files will be acessible to root only.')
            print_('Aborting.')
            sys.exit(1)
        else:
            print_('We do not recommend running meocloud as the root user.')
            print_('Are you sure you want to continue [N/y]? ', end='')
            answer = input().strip()
            if answer.lower() != 'y':
                sys.exit(1)
    success = False
    create_required_directories()
    init_logging()
    log = logging.getLogger(LOGGER_NAME)
    try:
        instance = start()
    except TooManyRetries:
        log.info('CLI: Could not acquire single instance lock. Aborting.')
        print_('Could not establish a exclusive connection to the daemon.')
        print_('Please make sure you are not running another meocloud command elsewhere and try again.')
    else:
        log.info('')
        log.info('')
        log.info('')
        log.info('')
        log.info('')
        daemon_client = DaemonClient()
        cli_handler = CLIHandler(daemon_client)
        try:
            parser = argparse.ArgumentParser(description='MEO Cloud command-line client', prog='meocloud')
            parser.add_argument('-v', '--version', action='store_true', help='Print MEO Cloud\'s version')

            subparsers = parser.add_subparsers()
            start_parser = subparsers.add_parser('start', help='Starts MEO Cloud daemon')
            start_parser.set_defaults(func=cli_handler.start)

            start_parser = subparsers.add_parser('stop', help='Stops MEO Cloud daemon')
            start_parser.set_defaults(func=cli_handler.stop)

            status_parser = subparsers.add_parser('status', help='Returns MEO Cloud\'s status')
            status_parser.set_defaults(func=cli_handler.status)

            notifs_parser = subparsers.add_parser('notifications', aliases=['not'], help='Outputs the last {0} notifications received'.format(DEFAULT_NOTIFS_TAIL_LINES))
            notifs_parser.add_argument('-n', '--lines', metavar='N', type=int, dest='n_lines', default=DEFAULT_NOTIFS_TAIL_LINES,
                                       help='Output the last N notifications, instead of the last {0}'.format(DEFAULT_NOTIFS_TAIL_LINES))
            notifs_parser.set_defaults(func=cli_handler.notifications)

            sync_list_parser = subparsers.add_parser('listsync', aliases=['ls'], help='List synchronized paths')
            sync_list_parser.set_defaults(func=cli_handler.list_sync)

            no_sync_parser = subparsers.add_parser('removesync', aliases=['rs'], help='Stops synchronization of the given path (inside your MEO Cloud\'s folder)')
            no_sync_parser.add_argument('path')
            no_sync_parser.add_argument('-f', '--force', dest='force', action='store_true', help='Prevent validation that the given path is a valid folder in your MEO Cloud. '
                                                                                                 'You can use it to stop the synchronization of files or expected future folders.')
            no_sync_parser.set_defaults(func=cli_handler.remove_sync)

            sync_parser = subparsers.add_parser('addsync', aliases=['as'], help='Reactivates synchronization of the given path (inside your MEO Cloud\'s folder)')
            sync_parser.add_argument('path')
            sync_parser.set_defaults(func=cli_handler.add_sync)

            proxy_parser = subparsers.add_parser('proxy', help='Get or set proxy')
            proxy_parser.add_argument('proxy_url', nargs='?', help='If present, use this value as the proxy; if not present, show the current proxy. '
                                                                   'If the value is \'default\', use the system proxy '
                                                                   '(found in the http_proxy or https_proxy environment variables).')
            proxy_parser.set_defaults(func=cli_handler.proxy)

            bwlimit_parser = subparsers.add_parser('ratelimit', help='Get or set bandwidth limits')
            bwlimit_parser.add_argument('direction', nargs='?', help='Use \'up\' or \'down\' to set the upload or download rate. If not present, show the current rate limits.')
            bwlimit_parser.add_argument('limit', nargs='?', type=int, default=0, help='Rate limit in kB/s. If not present, remove rate limit.')
            bwlimit_parser.set_defaults(func=cli_handler.bwlimit)

            pause_parser = subparsers.add_parser('pause', help='Pause MEO Cloud')
            pause_parser.set_defaults(func=cli_handler.pause)

            unpause_parser = subparsers.add_parser('resume', help='Resumes MEO Cloud')
            unpause_parser.set_defaults(func=cli_handler.resume)

            unlink_parser = subparsers.add_parser('unlink', help='Unlink you MEO Cloud account')
            unlink_parser.set_defaults(func=cli_handler.unlink)

            # TODO shell extension
            # TODO recent changed files

            # If no arguments received, print help and exit
            if len(sys.argv) == 1:
                parser.print_help()
                sys.exit(1)

            args = parser.parse_args()
            if args.version:
                success = cli_handler.version()
            else:
                handler = args.func
                delattr(args, 'func')
                delattr(args, 'version')
                success = handler(**vars(args))
        except Exception:
            log.exception('CLI: An uncatched error occurred!')
            cli_handler.out('Ups! An error has occurred!')
            cli_handler.out('Please try again, and if it happens again, please report this.')
        finally:
            daemon_client.close()
            instance.stop()
            if not success:
                sys.exit(1)


if __name__ == '__main__':
    main()
