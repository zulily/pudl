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
"""helper - a module containing a collection useful object manipulations"""

import json
import re
import yaml

def object_filter(objects, grep):
    """Filter out any objects that do not have attributes with values matching
    *all* regular expressions present in grep (AND, essentially)

    :param objects ADObject: A list of ADObjects
    :param grep list: A list of regular expressions that must match for filtering

    :return: A list of filtered ADObjects
    :rtype: list
    """
    filtered = []
    if grep:
        for ad_object in objects:
            o_string = ' '.join([value for value in ad_object.to_dict().values()
                                 if isinstance(value, str)])
            skip = False
            for regex in grep:
                if not re.search(regex, o_string, re.M|re.S|re.I):
                    skip = True
                    break
            if not skip:
                filtered.append(ad_object)

        return filtered
    else:
        return objects


def serialize(ad_objects, output_format='json', indent=2, attributes_only=False):
    """Serialize the object to the specified format

    :param ad_objects list: A list of ADObjects to serialize
    :param output_format str: The output format, json or yaml.  Defaults to json
    :param indent int: The number of spaces to indent, defaults to 2
    :param attributes only: Only serialize the attributes found in the first record of the list
        of ADObjects

    :return: A serialized, formatted representation of the list of ADObjects
    :rtype: str
    """

    # If the request is to only show attributes for objects returned
    # in the query, overwrite ad_objects with only those attributes present in
    # the first object in the list
    if attributes_only:
        ad_objects = [key for key in sorted(ad_objects[0].keys())]

    if output_format == 'json':
        return json.dumps(ad_objects, indent=indent, ensure_ascii=False, sort_keys=True)
    elif output_format == 'yaml':
        return yaml.dump(sorted(ad_objects), indent=indent)



