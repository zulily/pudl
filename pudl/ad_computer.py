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
"""ad_computer"""

import logging

from pudl.ad_object import ADObject

class ADComputer(ADObject):
    """A class to represent AD computer objects.  Includes a number of
    helper methods, particularly object-factory related.

    ADComputer objects have minimal depth, with attributes set to
    strings or lists.  Available attributes are dependent
    on the results returned by the LDAP query.
    """


    def computer(self, base_dn, samaccountname, attributes=()):
        """Produces a single, populated ADComputer object through the object factory.
        Does not populate attributes for the caller instance.

        :param str base_dn: The base DN to search within
        :param str samaccountname: The computer's sAMAccountName
        :param list attributes: Object attributes to populate, defaults to all

        :return: A populated ADComputer object
        :rtype: ADComputer
        """

        computers = self.computers(base_dn, samaccountnames=[samaccountname], attributes=attributes)

        try:
            # Usually we will find a match, but perhaps not always
            return computers[0]
        except IndexError:
            logging.info("%s - unable to retrieve object from AD by sAMAccountName", samaccountname)


    def computers(self, base_dn, samaccountnames=(), attributes=()):
        """Gathers a list of ADComputer objects

        :param str base_dn: The base DN to search within
        :param list samaccountnames: A list of computer names for which objects will be
            created, defaults to all computers if unspecified
        :param list attributes: Object attributes to populate, defaults to all

        :return: A list of populated ADComputer objects
        :rtype: list
        """
        ad_computers = []

        search_filter = '(&(objectClass=computer){0})'
        # If no samaccountnames specified, filter will pull all computer objects under
        # base_dn
        if not samaccountnames:
            search_filter = search_filter.format('(sAMAccountName=*)')
        else:
            if len(samaccountnames) == 1:
                computer_names = '(sAMAccountName={0})'.format(samaccountnames[0])
            else:
                computer_names = '(|{0})'.format(''.join(['(sAMAccountName={0})'.\
                                                          format(computer) for computer
                                                          in samaccountnames]))

            search_filter = search_filter.format(computer_names)


        logging.debug('%s Search filter: %s', self.__class__.__name__, search_filter)

        results = self.adq.search(base_dn, search_filter, attributes)

        for search_result in results:
            adc = self._object_factory(search_result)
            ad_computers.append(adc)

        return ad_computers

