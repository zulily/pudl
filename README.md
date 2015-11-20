pudl
======
**pudl** is a python package (with an included CLI) that wraps python-ldap and provides a somewhat-oo interface to Active Directory user, group and computer objects, retreived via LDAP with TLS. While not necessarily a replacement for existing client libraries and the ldapsearch binary, the api and bundled cli are perhaps simpler to work with than alternatives, for many
common queries.

Documentation
--------------
For the full API reference and CLI usage with examples, please see the [full project documentation](http://pudl.readthedocs.org/en/latest/).

Prerequisites
--------------

*To get up and running, the following must be installed:*

+ python 2.7.x
+ python-dev
+ libsasl2-dev
+ libldap2-dev
+ libyaml-dev

Installation
------------

### The Easy Way
```bash
pip install pudl
```

### Manual Installation
+ Create a virtual environment and activate
+ Clone this git repository
+ pip install .

*Optionally for sphinx document generation, pip install the following*

+ sphinx
+ pygments
+ sphinx_rtd_theme
+ sphinx-argparse
+ mock

*Optionally, it may be desirable to set a few envrionment variables, e.g.:*

+ **PUDL_BASE_DN** - This is an important one to set, such as 'OU=Departments,DC=example,DC=com'.
+ **PUDL_DOMAIN** - Also a key setting, the AD domain is prepended to the user name for authentication.
+ **PUDL_PAGE_SIZE** - Adjusting the page size may result in faster queries, defaults to 300 results per page.
+ **PUDL_TLS_NO_VERIFY** - Provides an encrypted communication channel with TLS, but does not verify the server's identity.  Use with caution.

Example CLI Usage
-----------------
**Retrieve JSON representations of two users**

```bash
pudl user bhodges jdupont
```
**Retrieve three groups, serialized to yaml**

```bash
pudl group HR Finance Technology --output-format=yaml
```

License
-------
Apache License, version 2.0.  Please see LICENSE
