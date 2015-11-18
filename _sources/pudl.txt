******
pudl
******

Overview
========

**pudl** is a bundled command-line interface which wraps much of the functionality
present in the pudl package modules.  Not only does it demonstrate usage of the functionality present
in pudl package modules, it also perhaps serves as a reasonable alternative to ldapsearch for the most
common types of queries.  With its simplified interface (and contrary to ldapsearch), there is no
need to create custom ldap filters.  Additionally, pudl has the added benefits of regular expression
object filtering and object serialization, in json or yaml format.  Note that all values returned are
strings.

Environment Variables
=====================
To keep the pudl syntax as simple and minimal as possible, setting a few environment variables and
adding them to an init file such as ~/.bashrc is advised:

* **PUDL_BASE_DN** - This is an important one to set, such as 'OU=Departments,DC=example,DC=com'.
* **PUDL_DOMAIN** - Also a key setting, the AD domain is prepended to the user name for authentication.
* **PUDL_PAGE_SIZE** - Adjusting the page size may result in faster queries, defaults to 300 results per page.
* **PUDL_TLS_NO_VERIFY** - Provides an encrypted communication channel with TLS, but does not verify the server's
  identity.  Use with caution.


Example Usage
=============

Pull Specific AD User Objects
-----------------------------
*Pulls two full user objects. Outputs json by default, with
yaml being another supported output format.*

.. code-block:: bash

    $ pudl user bhodges jdupont

Pull a Paired-Down User Object
------------------------------
*Pull a single user object with just three specific attributes,
output results as yaml.*

.. code-block:: bash

    $ pudl user -a samaccountname -a title -a memberof --output-format=yaml bhodges

AD Object grep!
---------------
*Pull all user objects with just two specific attributes, but filter
down to only those that that match a regular expression. Note that matching is case-insensitive.*

.. code-block:: bash

    $ pudl user -a samaccountname -a title --grep="[iI]nfrastruct.re"

Retrieve AD Group Objects
-------------------------
*Pull all attributes for three groups. Note that while member attribute items
are fully expanded by default, the memberOf attribute is not currently flattened.*

.. code-block:: bash

    $ pudl group HR Finance Technology


List AD Object Attributes
-------------------------
*Return a list of all attribute names for the first returned object in
the results set*

.. code-block:: bash

    $ pudl user --attributes-only bhodges


Command-line Reference
======================

.. argparse::
   :module: pudl.scripts.cli
   :func: parse_arguments
   :prog: pudl

