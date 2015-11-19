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
"""ad_group"""

import logging

from pudl.ad_object import ADObject

class ADGroup(ADObject):
    """A class to represent AD group objects.  Includes a number of
    helper methods, particularly object-factory related.

    ADGroup objects have minimal depth, with attributes set to
    strings or lists.  Available attributes are dependent
    on the results returned by the LDAP query.

    In its current implementation, the memberOf attribute
    is not expanded.  The member attribute is however flattened out.

    """


    def group(self, base_dn, samaccountname, attributes=(), explicit_membership_only=False):
        """Produces a single, populated ADGroup object through the object factory.
        Does not populate attributes for the caller instance.

        sAMAccountName may not be present in group objects in modern AD schemas.
        Searching by common name and object class (group) may be an alternative
        approach if required in the future.

        :param str base_dn: The base DN to search within
        :param str samaccountname: The group's sAMAccountName
        :param list attributes: Object attributes to populate, defaults to all

        :return: A populated ADGroup object
        :rtype: ADGroup
        """

        groups = self.groups(base_dn, samaccountnames=[samaccountname], attributes=attributes,
                             explicit_membership_only=explicit_membership_only)

        try:
            # Usually we will find a match, but perhaps not always
            return groups[0]
        except IndexError:
            logging.info("%s - unable to retrieve object from AD by sAMAccountName", samaccountname)


    def groups(self, base_dn, samaccountnames=(), attributes=(), explicit_membership_only=False):
        """Gathers a list of ADGroup objects

        sAMAccountName may not be present in group objects in modern AD schemas.
        Searching by common name and object class (group) may be an alternative
        approach if required in the future.

        :param str base_dn: The base DN to search within
        :param list samaccountnames: A list of group names for which objects will be
            created, defaults to all groups if unspecified
        :param list attributes: Object attributes to populate, defaults to all

        :return: A list of populated ADGroup objects
        :rtype: list
        """
        ad_groups = []

        search_filter = '(&(objectClass=group)(!(objectClass=user))(!(objectClass=computer)){0})'
        # If no samaccountnames specified, filter will pull all group objects under
        # base_dn
        if not samaccountnames:
            search_filter = search_filter.format('(sAMAccountName=*)')
        else:
            if len(samaccountnames) == 1:
                group_names = '(sAMAccountName={0})'.format(samaccountnames[0])
            else:
                group_names = '(|{0})'.format(''.join(['(sAMAccountName={0})'.\
                                                       format(group) for group
                                                       in samaccountnames]))

            search_filter = search_filter.format(group_names)


        logging.debug('%s Search filter: %s', self.__class__.__name__, search_filter)

        results = self.adq.search(base_dn, search_filter, attributes)

        for search_result in results:
            adg = self._object_factory(search_result)
            if not explicit_membership_only and 'member' in dir(adg):
                member = [u[0] for u in
                          self.adq.search(base_dn, '(memberOf:1.2.840.113556.1.4.1941:={0})'.\
                          format(search_result[0]), attributes=['member'])]
                adg.member = member
            ad_groups.append(adg)

        return ad_groups

