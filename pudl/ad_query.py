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
"""ad_query"""

import logging
import ldap

# Set a default LDAP URL, port 389 as we are using LDAP+TLS and not LDAPS
LDAP_URL = 'ldap://ldap:389'

# LDAP options related to trusting the identity of the remote server
#pylint: disable=no-member
LDAP_OPTIONS = ((ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3),
                (ldap.OPT_REFERRALS, 0))

LDAP_OPTIONS_TLS_NO_VERIFY = ((ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW),
                              (ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3),
                              (ldap.OPT_REFERRALS, 0))
#pylint: enable=no-member

# Limit the number of results per page, with a default that should generally
# be below the size of the limit imposed by most AD servers
PAGE_SIZE = 300

# Require identity trust is established with the server by default
TLS_NO_VERIFY = False

class ADQuery(object):  #pylint: disable=too-few-public-methods
    """Query Active directory with python-ldap.  May be used directly, but is most
    commonly used indirectly via ADObject-based classes.  All connections
    require TLS.
    """

    def __init__(self, user, password,
                 ldap_url=LDAP_URL,
                 tls_no_verify=TLS_NO_VERIFY,
                 page_size=PAGE_SIZE):
        """The ADQuery constructor

        :param str user: The LDAP user to connect as
        :param str password: The LDAP user's password
        :param str ldap_url: The url, defaults to *{0}*
        :param bool tls_no_verify: If True, connect to servers with certificates not signed
            by an authority we trust, defaults to False
        :param int page_size: The max result set size, per page, defaults to *{1}*
        """.format(LDAP_URL, PAGE_SIZE)
        if tls_no_verify:
            ldap_options = LDAP_OPTIONS_TLS_NO_VERIFY
        else:
            ldap_options = LDAP_OPTIONS

        # Setup logging, assumes a root logger already exists with handlers
        self.logger = logging.getLogger(__name__)

        # Set LDAP options for the connection
        for setting in ldap_options:
            ldap.set_option(setting[0], setting[1])

        self.ldap = ldap.initialize(ldap_url)
        self.sprc = ldap.controls.SimplePagedResultsControl(True, page_size, '')
        self.user = user
        self.password = password
        self.page_size = page_size

        # Open the connection
        self._open()


    def search(self, base_dn, search_filter, attributes=()):
        """Perform an AD search

        :param str base_dn: The base DN to search within
        :param str search_filter: The search filter to apply, such as:
          *objectClass=person*
        :param list attributes: Object attributes to populate, defaults to all
        """
        results = []
        page = 0
        while page == 0 or self.sprc.cookie:
            page += 1
            #pylint: disable=no-member
            message_id = self.ldap.search_ext(base_dn, ldap.SCOPE_SUBTREE,
                                              search_filter, attributes,
                                              serverctrls=[self.sprc])
            #pylint: enable=no-member
            data, server_controls = self.ldap.result3(message_id)[1::2]
            self.sprc.cookie = server_controls[0].cookie
            logging.debug('%s - Page %s results: %s',  \
                          self.__class__.__name__, page, ', '.join(k[0] for k in data))
            results += [u for u in data]

        return results


    def _open(self):
        """Bind, use tls"""
        try:
            self.ldap.start_tls_s()
        #pylint: disable=no-member
        except ldap.CONNECT_ERROR:
        #pylint: enable=no-member
            logging.error('Unable to establish a connection to the LDAP server, ' + \
                          'please check the connection string ' + \
                          'and ensure the remote certificate is signed by a trusted authority.')
            raise

        self.ldap.simple_bind_s(self.user, self.password)

