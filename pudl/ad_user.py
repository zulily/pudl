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
"""ad_user"""

import logging

from pudl.ad_object import ADObject

class ADUser(ADObject):
    """A class to represent AD user objects.  Includes a number of
    helper methods, particularly object-factory related.

    ADUser objects have minimal depth, with attributes set to
    strings or lists.  Available attributes are dependent
    on the results returned by the LDAP query.
    """

    # Some refactoring may be considered in the future that would
    # involve passing the sAMAccountName to a contstructor override,
    # and possibly moving users() to become static.  Otherwise,
    # instead of user() creating and returning a single new object,
    # perhaps just populate the current ADUser instance, which
    # could make a little more sense



    def user(self, base_dn, samaccountname, attributes=(), explicit_membership_only=False):
        """Produces a single, populated ADUser object through the object factory.
        Does not populate attributes for the caller instance.

        :param str base_dn: The base DN to search within
        :param str samaccountname: The user's sAMAccountName
        :param list attributes: Object attributes to populate, defaults to all
        :param bool explicit_membership_only: If set True, memberof will only
            list groups for which the user is a directly referenced member

        :return: A populated ADUser object
        :rtype: ADUser
        """

        users = self.users(base_dn, samaccountnames=[samaccountname],
                           attributes=attributes, explicit_membership_only=explicit_membership_only)

        try:
            # Usually we will find a match, but perhaps not always
            return users[0]
        except IndexError:
            logging.info("%s - unable to retrieve object from AD by sAMAccountName", samaccountname)



    def users(self, base_dn, samaccountnames=(), attributes=(), explicit_membership_only=False):
        """Gathers a list of ADUser objects

        :param str base_dn: The base DN to search within
        :param list attributes: Object attributes to populate, defaults to all
        :param list samaccountnames: A list of usernames for which objects will be
            created, defaults to all users if unspecified
        :param bool explicit_membership_only: If set True, memberof will only
            list groups for which users are directly referenced members

        :return: A list of populated ADUser objects
        :rtype: list
        """
        ad_users = []

        search_filter = '(&(objectClass=user)(!(objectClass=group))(!(objectClass=computer)){0})'
        # If no samaccountnames specified, filter will pull all user objects under
        # base_dn
        if not samaccountnames:
            search_filter = search_filter.format('(sAMAccountName=*)')
        else:
            # Extensible filter: http://bit.ly/1Qh4eyV
            if len(samaccountnames) == 1:
                account_names = '(sAMAccountName={0})'.format(samaccountnames[0])
            else:
                account_names = '(|{0})'.format(''.join(['(sAMAccountName={0})'.format(username) \
                                                for username in samaccountnames]))

            search_filter = search_filter.format(account_names)


        logging.debug('%s Search filter: %s', self.__class__.__name__, search_filter)

        results = self.adq.search(base_dn, search_filter, attributes)

        for search_result in results:
            adu = self._object_factory(search_result)
            # Each results index 0 of the tuple is the DN
            if not explicit_membership_only and 'memberof' in dir(adu):
                memberof = [g[0] for g in self.adq.search(base_dn,
                                                          '(member:1.2.840.113556.1.4.1941:={0})'.\
                                                          format(search_result[0]),
                                                          attributes=['memberof'])]
                adu.memberof = memberof
            ad_users.append(adu)


        return ad_users


    def is_member(self, group_distinguishedname):
        """For the current ADUser instance, determine if
        the user is a member of a specific group (the group DN is used).
        The result may not be accurate if explicit_membership_only was set to
        True when the object factory method (user() or users()) was
        called.

        :param str group_distinguishedname: The group DistinguishedName

        :return: A boolean indicating whether or not the user is a member of the group
        :rtype: bool
        """
        #pylint: disable=no-member
        if group_distinguishedname.lower() in [dn.lower() for dn in self.memberof]:
        #pylint: enable=no-member
            return True
        else:
            return False


    def group_samaccountnames(self, base_dn):
        """For the current ADUser instance, determine which
        groups the user is a member of and convert the
        group DistinguishedNames to sAMAccountNames.
        The resulting list of groups may not be complete
        if explicit_membership_only was set to
        True when the object factory method (user() or users()) was
        called.

        :param str base_dn: The base DN to search within

        :return: A list of groups (sAMAccountNames) for which the
            current ADUser instance is a member, sAMAccountNames
        :rtype: list
        """
        #pylint: disable=no-member
        mappings = self.samaccountnames(base_dn, self.memberof)
        #pylint: enable=no-member
        groups = [samaccountname for samaccountname in mappings.values()]
        if not groups:
            logging.info("%s - unable to retrieve any groups for the current ADUser instance",
                         self.samaccountname)
        return groups

