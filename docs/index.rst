.. pudl documentation master file, created by
   bhodges.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pudl's documentation!
================================

**pudl version:** |version|

``pudl`` is a python package that wraps python-ldap and provides a somewhat-oo interface to
Active Directory user, group and computer objects, retreived via LDAP with TLS.
While not necessarily a replacement for existing client libraries and the ldapsearch binary, the api
and bundled `cli <./pudl.html>`_ are perhaps simpler to work with than alternatives, for many
common queries.

Why the name "pudl"
===================
While pronounced like "puddle", the name is somewhat related to 'pudl'.replace('u', 'a')[::-1].

Contents:

.. toctree::
   :maxdepth: 2

   getting_started
   api_reference
   pudl
   license



Indices and tables
==================

* :ref:`genindex`

.. * :ref:`modindex`
.. * :ref:`search`

