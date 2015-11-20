#! /usr/bin/env python
#
# Copyright (C) 2015 zulily, llc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""pudl cli"""

from __future__ import print_function

import argparse
import getpass
import logging
import os
import sys

from pudl import __version__ as pudl_version
from pudl.ad_computer import ADComputer
from pudl.ad_group import ADGroup
from pudl.ad_query import ADQuery
from pudl.ad_user import ADUser
from pudl.helper import object_filter, serialize


def main():
    """Do some stuff"""
    # Parse all command line argument
    args = parse_arguments().parse_args()

    # Setup logging
    configure_logging(args)
    logging.debug(args)

    # Prompt for a password if necessary
    if not args.password:
        password = getpass.getpass(prompt='Password ({0}): '.format(args.user))
    else:
        password = args.password

    # Create an instance of ADQuery which sets up a single
    # connection used for querying, for all AD object types
    ldap_url = 'ldap://{0}:{1}'.format(args.host, args.port)
    adq = ADQuery(user=args.user, password=password, page_size=args.page_size,
                  ldap_url=ldap_url, tls_no_verify=args.tls_no_verify)
    if args.subcommand == 'user':
        adu = ADUser(adq)
        users = adu.users(base_dn=args.base_dn, attributes=args.attributes,
                          samaccountnames=args.samaccountnames,
                          explicit_membership_only=args.explicit_membership_only)
        users = object_filter(users, args.grep)
        print(serialize([u.to_dict() for u in users],
                        output_format=args.output_format, attributes_only=args.attributes_only))
    elif args.subcommand == 'group':
        adg = ADGroup(adq)
        groups = adg.groups(base_dn=args.base_dn, attributes=args.attributes,
                            samaccountnames=args.samaccountnames,
                            explicit_membership_only=args.explicit_membership_only)
        groups = object_filter(groups, args.grep)
        print(serialize([g.to_dict() for g in groups],
                        output_format=args.output_format, attributes_only=args.attributes_only))
    elif args.subcommand == 'computer':
        adg = ADComputer(adq)
        computers = adg.computers(base_dn=args.base_dn, attributes=args.attributes,
                                  samaccountnames=args.samaccountnames)
        computers = object_filter(computers, args.grep)
        print(serialize([c.to_dict() for c in computers],
                        output_format=args.output_format, attributes_only=args.attributes_only))


def configure_logging(args):
    """Logging to console"""
    log_format = logging.Formatter('%(levelname)s:%(name)s:line %(lineno)s:%(message)s')
    log_level = logging.INFO if args.verbose else logging.WARN
    log_level = logging.DEBUG if args.debug else log_level
    console = logging.StreamHandler()
    console.setFormatter(log_format)
    console.setLevel(log_level)
    root_logger = logging.getLogger()
    if len(root_logger.handlers) == 0:
        root_logger.addHandler(console)
    root_logger.setLevel(log_level)
    root_logger.handlers[0].setFormatter(log_format)
    logging.getLogger(__name__)


def parse_arguments():
    """Collect command-line arguments.  Let the caller run parse_args(), as
    sphinx-argparse requires a function that returns an instance of
    argparse.ArgumentParser
    """
    # Pull a few settings from the environment, should they exist
    base_dn = os.environ['PUDL_BASE_DN'] if 'PUDL_BASE_DN' in os.environ \
              else 'OU=Departments,DC=example,DC=com'
    domain = os.environ['PUDL_DOMAIN'].upper() if 'PUDL_DOMAIN' in os.environ else 'EXAMPLE'
    page_size = os.environ['PUDL_PAGE_SIZE'].upper() if 'PUDL_PAGE_SIZE' in os.environ else 300
    tls_no_verify = bool(os.environ['PUDL_TLS_NO_VERIFY'].lower().capitalize()) \
                    if 'PUDL_TLS_NO_VERIFY' in os.environ else False

    parser = argparse.ArgumentParser(prog='pudl',
                                     description='A script for interacting with Active ' + \
                                     'Directory, leveraging python-ldap')
    parser.add_argument('-V', '--version', action='version', version='pudl v' + pudl_version,
                        help="Print the version number and exit")
    subparsers = parser.add_subparsers(dest='subcommand', help='Sub-command help')
    parser_common = subparsers.add_parser('common', add_help=False)
    parser_common.add_argument('--user', '-u', action='store', dest='user',
                               help='The ldap user (bind dn) to connect as. ' + \
                               'The full DN will work, or often, just the CN may be ' + \
                               'sufficient, such as "John Smith", or more commonly, ' + \
                               'specify the domain and sAMAccountName. Defaults to ' + \
                               '{0}\\username.  The domain '.format(domain) + \
                               'portion may be overridden with PUDL_DOMAIN',
                               default='{0}\\{1}'.format(domain, getpass.getuser()))
    parser_common.add_argument('--password', '-p', action='store',
                               dest='password', help="The connecting user's password")
    parser_common.add_argument('--host', '-H', action='store',
                               dest='host', help='The AD/LDAP host, defaults to ldap',
                               default='ldap')
    parser_common.add_argument('--port', '-P', action='store', dest='port',
                               help='The ldap port, defaults to 389.  389 is ' + \
                               'is the standard port', type=int, default=389)
    parser_common.add_argument('--page-size', '-s', action='store', dest='page_size',
                               help='The ldap results are paged, specify the ' + \
                               'number of results per page, defaults to ' + \
                               '{0}. May be overridden with PUDL_PAGE_SIZE'.format(page_size),
                               type=int, default=page_size)
    parser_common.add_argument('--base-dn', '-b', action='store',
                               dest='base_dn', default=base_dn,
                               help="The Base DN to use, defaults to {0}. ".format(base_dn) + \
                               "May be overridden with PUDL_BASE_DN")
    parser_common.add_argument('--attribute', '-a', action='append',
                               dest='attributes', metavar='ATTRIBUTE',
                               help="Attributes to include in results objects.  Note that " + \
                               "any nested objects return all attributes.  Maybe be used " + \
                               "multiple times, and if not specified, all " + \
                               "attributes are included in top-level objects")
    parser_common.add_argument('--grep', '-g', action='append', dest='grep',
                               help='Filter results to only those matching the specified ' + \
                               'regular expression (compares against all attributes). ' + \
                               'May be used multiple times')
    parser_common.add_argument('--attributes-only', '-A', action='store_true',
                               dest='attributes_only', help="Only display a list of attributes " + \
                               "that are present for the object type returned by the LDAP query")
    parser_common.add_argument('--output-format', '-f', action='store', dest='output_format',
                               choices=['json', 'yaml'], default='json',
                               help="Output format, defaults to json.")
    parser_common.add_argument('--verbose', '-v', action='store_true', dest='verbose',
                               help='Turn on verbose output', default=False)
    parser_common.add_argument('--debug', '-d', action='store_true', dest='debug', default=False,
                               help="Print out debugging information, very chatty")
    parser_common.add_argument('--tls-no-verify', '-V', action='store_true',
                               dest='tls_no_verify',
                               default=tls_no_verify, help="Don't verify the authenticity " + \
                               "of the server's certificate, defaults to " + \
                               "{0} and may be overridden with ".format(tls_no_verify) + \
                               "PUDL_TLS_NO_VERIFY")
    parser_user = subparsers.add_parser('user', parents=[parser_common], conflict_handler='resolve',
                                        help='Pull user objects from AD')
    parser_user.add_argument(nargs="*", dest='samaccountnames',
                             help='sAMAccountNames for any user objects that are to be ' + \
                             'looked up. If unspecified, returns all users under the base ' + \
                             'DN provided')
    parser_user.add_argument('--explicit-membership-only', '-e', action='store_true',
                             dest='explicit_membership_only', default=False,
                             help="Only show membership for users that is explicit, " + \
                             "not taking into account group nesting.  Defaults to False")
    parser_group = subparsers.add_parser('group', parents=[parser_common],
                                         conflict_handler='resolve',
                                         help='Pull group objects from AD')
    parser_group.add_argument(nargs="*", dest='samaccountnames',
                              help="sAMAccountNames for any group objects that are to be " + \
                              'looked up. If unspecified, returns all groups under the base ' + \
                              'DN provided. sAMAccountName may not be present in group ' + \
                              'objects in modern AD schemas')
    parser_group.add_argument('--explicit-membership-only', '-e', action='store_true',
                              dest='explicit_membership_only', default=False,
                              help="Only show membership for users that is explicit, " + \
                              "not taking into account group nesting.  Defaults to False")
    parser_computer = subparsers.add_parser('computer', parents=[parser_common],
                                            conflict_handler='resolve',
                                            help='Pull computer objects from AD')
    parser_computer.add_argument(nargs="*", dest='samaccountnames',
                                 help="sAMAccountNames for any computer objects that are to be " + \
                                 'looked up. If unspecified, returns all computers under ' + \
                                 'the base DN provided.')

    # sphinx is not add_help=False aware...
    del subparsers.choices['common']

    return parser


if __name__ == '__main__':
    sys.exit(main())
