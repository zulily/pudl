***************
Getting Started
***************

Installation
============

Prerequisites
-------------

*To get up and running, the following must be installed:*

* python 2.7.x
* python-dev
* libsasl2-dev
* libldap2-dev
* libyaml-dev

pip
---
From the top-level directory of the cloned repository:

.. code-block:: bash

    pip install .

.. note:: This is typically performed with an active python virtual environment.

And for *optional* document generation with sphinx, install the following python packages as well:

.. code-block:: bash

    pip install sphinx
    pip install pygments
    pip install sphinx_rtd_theme
    pip install sphinx-argparse

TLS
===
pudl only communicates with Active Directory over TLS and by default, the
remote server must meet strict criteria such as the commonname matching
the hostname in the LDAP URL, and the remote server must present a
certificate that is signed by a trusted authority.

Adding a trusted CA to a Linux system varies by distribution, but is rather
simple with ubuntu:

1) Copy the CA certificate (.CER format) to /usr/share/ca-certificates/extra/

2) chown the CA certificate to root.root and chmod it to 444

3) Run sudo dpkg-reconfigure ca-certificates

If the only requirement is an encrypted channel and not verifying
the identity of the remote server, the ADQuery constructor takes a tls_no_verify
parameter, and the pudl CLI has a --tls-no-verify argument.  Use
these options with caution.

Basic Usage
===========

**Pull a user object (bhodges) and a few attributes to print out**::


    #! /usr/bin/env python

    import sys
    from pudl import *
    from pudl.ad_query import ADQuery
    from pudl.ad_user import ADUser

    BASE_DN = 'OU=Departments,DC=example,DC=com'
    LDAP_USER = 'jdupont'
    PASSWORD = 'my_secret'

    def main():
        """
        """
        adq = ADQuery(user=LDAP_USER, password=PASSWORD)
        adu = ADUser(adq)
        users = adu.users(base_dn=BASE_DN, attributes=['samaccountname', 'cn',
                          'title',], samaccountnames=['bhodges',])

        for user in users:
            print '{0}: {1}, {2}'.format(user.samaccountname, user.cn, user.title)

    if __name__ == '__main__':
        sys.exit(main())

*For additional usage examples, reviewing the* :doc:`pudl` *cli* source is recommended
