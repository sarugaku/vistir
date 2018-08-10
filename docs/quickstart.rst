===============================================================================
vistir: Setup / utilities which most projects eventually need
===============================================================================

.. image:: https://img.shields.io/pypi/v/vistir.svg
    :target: https://pypi.python.org/pypi/vistir

.. image:: https://img.shields.io/pypi/l/vistir.svg
    :target: https://pypi.python.org/pypi/vistir

.. image:: https://travis-ci.com/sarugaku/vistir.svg?branch=master
    :target: https://travis-ci.com/sarugaku/vistir

.. image:: https://img.shields.io/pypi/pyversions/vistir.svg
    :target: https://pypi.python.org/pypi/vistir

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
    :target: https://saythanks.io/to/techalchemy

.. image:: https://readthedocs.org/projects/vistir/badge/?version=latest
    :target: https://vistir.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


Installation
*************

Install from `PyPI`_:

  ::

    $ pipenv install --pre vistir

Install from `Github`_:

  ::

    $ pipenv install -e git+https://github.com/sarugaku/vistir.git#egg=vistir


.. _PyPI: https://www.pypi.org/project/vistir
.. _Github: https://github.com/sarugaku/vistir


.. _`Summary`:

Summary
********

**vistir** is a library full of utility functions designed to make life easier. Here are
some of the places where these functions are used:

  * `pipenv`_
  * `requirementslib`_
  * `pip-tools`_
  * `passa`_
  * `pythonfinder`_

.. _modutil: https://github.com/sarugaku/pythonfinder
.. _passa: https://github.com/sarugaku/passa
.. _pipenv: https://github.com/pypa/pipenv
.. _pip-tools: https://github.com/jazzband/pip-tools
.. _requirementslib: https://github.com/sarugaku/requirementslib


.. _`Usage`:

Usage
******

Importing a utility
////////////////////

You can import utilities directly from **vistir**:

  ::

    from vistir import cd
    cd('/path/to/somedir'):
        do_stuff_in('somedir')


Functionality
**************

Of particular note, **vistir** provides the following set of functions as top level
api offerings due to their utility:

    * ``shell_escape``
    * ``load_path``
    * ``run``
    * ``partialclass``
    * ``temp_environ``
    * ``temp_path``
    * ``cd``
    * ``atomic_open_for_write``
    * ``open_file``
    * ``rmtree``
    * ``mkdir_p``
    * ``TemporaryDirectory``
    * ``NamedTemporaryFile``
    * ``partialmethod``
