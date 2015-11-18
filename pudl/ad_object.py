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
"""ad_object"""

import copy
import importlib
import logging


class ADObject(object):
    """A base class for AD objects."""

    def __init__(self, adq):
        """ADObject constructor"""
        # Setup logging, assumes a root logger already exists with handlers
        self.logger = logging.getLogger(__name__)

        self.adq = adq


    def to_dict(self):
        """Prepare a minimal dictionary with keys mapping to attributes for
        the current instance.

        """
        o_copy = copy.copy(self)
        # Remove some stuff that is not likely related to AD attributes
        for attribute in dir(self):
            if attribute == 'logger' or attribute == 'adq':
                try:
                    delattr(o_copy, attribute)
                except AttributeError:
                    pass

        return o_copy.__dict__


    def samaccountname(self, base_dn, distinguished_name):
        """Retrieve the sAMAccountName for a specific DistinguishedName

        :param str base_dn: The base DN to search within
        :param list distinguished_name: The base DN to search within
        :param list attributes: Object attributes to populate, defaults to all

        :return: A populated ADUser object
        :rtype: ADUser
        """
        mappings = self.samaccountnames(base_dn, [distinguished_name])

        try:
            # Usually we will find a match, but perhaps not always
            return mappings[distinguished_name]
        except KeyError:
            logging.info("%s - unable to retrieve object from AD by DistinguishedName",
                         distinguished_name)


    def samaccountnames(self, base_dn, distinguished_names):
        """Retrieve the sAMAccountNames for the specified DNs

        :param str base_dn: The base DN to search within
        :param list distinguished_name: A list of distinguished names for which to
            retrieve sAMAccountNames

        :return: Key/value pairs mapping DistinguishedName to sAMAccountName
        :rtype: dict
        """
        attributes = ['sAMAccountName']
        search_filter = '(|{0})'.format(''.join(['(DistinguishedName={0})'.format(dn)
                                                 for dn in distinguished_names]))
        logging.debug('%s Search filter: %s', self.__class__.__name__, search_filter)

        results = self.adq.search(base_dn, search_filter, attributes)

        mappings = {result[0]: result[1]['sAMAccountName'][0] for result in results}

        return mappings


    def _object_factory(self, search_result):
        """Given a single search result, create and return an object

        :param tuple search_result: a single search result returned by an LDAP query,
            position 0 is the DN and position 1 is a dictionary of key/value pairs

        :return: A single AD object instance
        :rtype: Object (ADUser, ADGroup, etc.)

        """
        class_name = self.__class__.__name__
        module = self.__module__
        logging.debug('Creating object of type %s for DN: %s', class_name, search_result[0])
        module = importlib.import_module('{0}'.format(module))
        class_ = getattr(module, class_name)
        ado = class_(self.adq)

        # A unique set of all attribute names found
        attribute_names = set()
        # A unique set
        multiples = set()
        for k in search_result[1].keys():
            if k not in attribute_names:
                attribute_names.add(k)
            else:
                multiples.add(k)
        for k, val in search_result[1].iteritems():
            if k in multiples and not hasattr(ado, k):
                setattr(ado, k.lower(), list())
            if hasattr(ado, k):
                value = getattr(ado, k)
                if len(val) == 1:
                    value.append(val[0])
                else:
                    value.append(val)
            else:
                if len(val) == 1:
                    setattr(ado, k.lower(), val[0])
                else:
                    setattr(ado, k.lower(), val)


        logging.debug('Attributes and values for %s object (DN: %s): %s', class_name,
                      search_result[0], ado.__dict__)

        return ado
