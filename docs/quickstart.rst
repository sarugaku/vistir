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


🐉 Installation
=================

Install from `PyPI`_:

  ::

    $ pipenv install --pre vistir

Install from `Github`_:

  ::

    $ pipenv install -e git+https://github.com/sarugaku/vistir.git#egg=vistir


.. _PyPI: https://www.pypi.org/project/vistir
.. _Github: https://github.com/sarugaku/vistir


.. _`Summary`:

🐉 Summary
===========

**vistir** is a library full of utility functions designed to make life easier. Here are
some of the places where these functions are used:

  * `pipenv`_
  * `requirementslib`_
  * `pip-tools`_
  * `passa`_
  * `pythonfinder`_

.. _passa: https://github.com/sarugaku/passa
.. _pipenv: https://github.com/pypa/pipenv
.. _pip-tools: https://github.com/jazzband/pip-tools
.. _requirementslib: https://github.com/sarugaku/requirementslib
.. _pythonfinder: https://github.com/sarugaku/pythonfinder


.. _`Usage`:

🐉 Usage
==========

Importing a utility
--------------------

You can import utilities directly from **vistir**:

.. code:: python

    from vistir import cd
    cd('/path/to/somedir'):
        do_stuff_in('somedir')


.. _`Functionality`:

🐉 Functionality
==================

**vistir** provides several categories of functionality, including:

    * Backports
    * Compatibility Shims
    * Context Managers
    * Miscellaneous Utilities
    * Path Utilities

.. note::

   The backports should be imported via :mod:`~vistir.compat` which will provide the
   native versions of the backported items if possible.


🐉 Compatibility Shims
-----------------------

Shims are provided for full API compatibility from python 2.7 through 3.7 for the following:

    * :func:`weakref.finalize`
    * :func:`functools.partialmethod` (via :func:`~vistir.backports.functools.partialmethod`)
    * :class:`tempfile.TemporaryDirectory` (via :class:`~vistir.backports.tempfile.TemporaryDirectory`)
    * :class:`tempfile.NamedTemporaryFile` (via :class:`~vistir.backports.tempfile.NamedTemporaryFile`)
    * :class:`~vistir.compat.Path`
    * :func:`~vistir.compat.get_terminal_size`
    * :class:`~vistir.compat.JSONDecodeError`
    * :exc:`~vistir.compat.ResourceWarning`
    * :exc:`~vistir.compat.FileNotFoundError`

The following additional function is provided for encoding strings to the filesystem
defualt encoding:

    * :func:`~vistir.compat.fs_str`


🐉 Context Managers
--------------------

**vistir** provides the following context managers as utility contexts:

    * :func:`~vistir.contextmanagers.atomic_open_for_write`
    * :func:`~vistir.contextmanagers.cd`
    * :func:`~vistir.contextmanagers.open_file`
    * :func:`~vistir.contextmanagers.spinner`
    * :func:`~vistir.contextmanagers.temp_environ`
    * :func:`~vistir.contextmanagers.temp_path`


.. _`atomic_open_for_write`:

**atomic_open_for_write**
///////////////////////////

This context manager ensures that a file only gets overwritten if the contents can be
successfully written in its place.  If you open a file for writing and then fail in the
middle under normal circumstances, your original file is already gone.

.. code:: python

    >>> fn = "test_file.txt"
    >>> with open(fn, "w") as fh:
            fh.write("this is some test text")
    >>> read_test_file()
    this is some test text
    >>> def raise_exception_while_writing(filename):
            with vistir.contextmanagers.atomic_open_for_write(filename) as fh:
                fh.write("Overwriting all the text from before with even newer text")
                raise RuntimeError("But did it get overwritten now?")
    >>> raise_exception_while_writing(fn)
        Traceback (most recent call last):
            ...
        RuntimeError: But did it get overwritten now?
    >>> read_test_file()
        writing some new text


.. _`cd`:

**cd**
///////

A context manager for temporarily changing the working directory.


.. code:: python

    >>> os.path.abspath(os.curdir)
    '/tmp/test'
    >>> with vistir.contextmanagers.cd('/tmp/vistir_test'):
            print(os.path.abspath(os.curdir))
    /tmp/vistir_test


.. _`open_file`:

**open_file**
///////////////

A context manager for streaming file contents, either local or remote. It is recommended
to pair this with an iterator which employs a sensible chunk size.


.. code:: python

    >>> filecontents = b""
        with vistir.contextmanagers.open_file("https://norvig.com/big.txt") as fp:
            for chunk in iter(lambda: fp.read(16384), b""):
                filecontents.append(chunk)
    >>> import io
    >>> import shutil
    >>> filecontents = io.BytesIO(b"")
    >>> with vistir.contextmanagers.open_file("https://norvig.com/big.txt") as fp:
            shutil.copyfileobj(fp, filecontents)


.. _`spinner`:

**spinner**
////////////

A context manager for wrapping some actions with a threaded, interrupt-safe spinner. The
spinner is fully compatible with all terminals (you can use ``bouncingBar`` on non-utf8
terminals) and will allow you to update the text of the spinner itself by simply setting
``spinner.text`` or write lines to the screen above the spinner by using
``spinner.write(line)``. Success text can be indicated using ``spinner.ok("Text")`` and
failure text can be indicated with ``spinner.fail("Fail text")``.

.. code:: python

    >>> lines = ["a", "b"]
    >>> with vistir.contextmanagers.spinner(spinner_name="dots", text="Running...", handler_map={}, nospin=False) as sp:
            for line in lines:
            sp.write(line + "\n")
            while some_variable = some_queue.pop():
                sp.text = "Consuming item: %s" % some_variable
            if success_condition:
                sp.ok("Succeeded!")
            else:
                sp.fail("Failed!")


.. _`temp_environ`:

**temp_environ**
/////////////////

Sets a temporary environment context to freely manipulate :data:`os.environ` which will
be reset upon exiting the context.


.. code:: python

    >>> os.environ['MY_KEY'] = "test"
    >>> os.environ['MY_KEY']
    'test'
    >>> with vistir.contextmanagers.temp_environ():
            os.environ['MY_KEY'] = "another thing"
            print("New key: %s" % os.environ['MY_KEY'])
    New key: another thing
    >>> os.environ['MY_KEY']
    'test'


.. _`temp_path`:

**temp_path**
//////////////

Sets a temporary environment context to freely manipulate :data:`sys.path` which will
be reset upon exiting the context.


.. code:: python

    >>> path_from_virtualenv = load_path("/path/to/venv/bin/python")
    >>> print(sys.path)
    ['/home/user/.pyenv/versions/3.7.0/bin', '/home/user/.pyenv/versions/3.7.0/lib/python37.zip', '/home/user/.pyenv/versions/3.7.0/lib/python3.7', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/lib-dynload', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/site-packages']
    >>> with temp_path():
            sys.path = path_from_virtualenv
            # Running in the context of the path above
            run(["pip", "install", "stuff"])
    >>> print(sys.path)
    ['/home/user/.pyenv/versions/3.7.0/bin', '/home/user/.pyenv/versions/3.7.0/lib/python37.zip', '/home/user/.pyenv/versions/3.7.0/lib/python3.7', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/lib-dynload', '/home/user/.pyenv/versions/3.7.0/lib/python3.7/site-packages']


🐉 Miscellaneous Utilities
--------------------------

The following Miscellaneous utilities are available as helper methods:

    * :func:`~vistir.misc.shell_escape`
    * :func:`~vistir.misc.unnest`
    * :func:`~vistir.misc.dedup`
    * :func:`~vistir.misc.run`
    * :func:`~vistir.misc.load_path`
    * :func:`~vistir.misc.partialclass`
    * :func:`~vistir.misc.to_text`
    * :func:`~vistir.misc.to_bytes`
    * :func:`~vistir.misc.decode_for_output`


.. _`shell_escape`:

**shell_escape**
/////////////////

Escapes a string for use as shell input when passing *shell=True* to :func:`os.Popen`.

.. code:: python

    >>> vistir.misc.shell_escape("/tmp/test/test script.py hello")
    '/tmp/test/test script.py hello'


.. _`unnest`:

**unnest**
///////////

Unnests nested iterables into a flattened one.

.. code:: python

    >>> nested_iterable = (1234, (3456, 4398345, (234234)), (2396, (23895750, 9283798, 29384, (289375983275, 293759, 2347, (2098, 7987, 27599)))))
    >>> list(vistir.misc.unnest(nested_iterable))
    [1234, 3456, 4398345, 234234, 2396, 23895750, 9283798, 29384, 289375983275, 293759, 2347, 2098, 7987, 27599]


.. _`dedup`:

**dedup**
//////////

Deduplicates an iterable (like a :class:`set`, but preserving order).

.. code:: python

    >>> iterable = ["repeatedval", "uniqueval", "repeatedval", "anotherval", "somethingelse"]
    >>> list(vistir.misc.dedup(iterable))
    ['repeatedval', 'uniqueval', 'anotherval', 'somethingelse']

.. _`run`:

**run**
////////

Runs the given command using :func:`subprocess.Popen` and passing sane defaults.

.. code:: python

    >>> out, err = vistir.run(["cat", "/proc/version"])
    >>> out
    'Linux version 4.15.0-27-generic (buildd@lgw01-amd64-044) (gcc version 7.3.0 (Ubuntu 7.3.0-16ubuntu3)) #29-Ubuntu SMP Wed Jul 11 08:21:57 UTC 2018'


.. _`load_path`:

**load_path**
//////////////

Load the :data:`sys.path` from the given python executable's environment as json.

.. code:: python

    >>> load_path("/home/user/.virtualenvs/requirementslib-5MhGuG3C/bin/python")
    ['', '/home/user/.virtualenvs/requirementslib-5MhGuG3C/lib/python37.zip', '/home/user/.virtualenvs/requirementslib-5MhGuG3C/lib/python3.7', '/home/user/.virtualenvs/requirementslib-5MhGuG3C/lib/python3.7/lib-dynload', '/home/user/.pyenv/versions/3.7.0/lib/python3.7', '/home/user/.virtualenvs/requirementslib-5MhGuG3C/lib/python3.7/site-packages', '/home/user/git/requirementslib/src']


.. _`partialclass`:

**partialclass**
/////////////////

Create a partially instantiated class.

.. code:: python

    >>> source = partialclass(Source, url="https://pypi.org/simple")
    >>> new_source = source(name="pypi")
    >>> new_source
    <__main__.Source object at 0x7f23af189b38>
    >>> new_source.__dict__
    {'url': 'https://pypi.org/simple', 'verify_ssl': True, 'name': 'pypi'}


.. _`to_text`:

**to_text**
////////////

Convert arbitrary text-formattable input to text while handling errors.

.. code:: python

    >>> vistir.misc.to_text(b"these are bytes")
    'these are bytes'


.. _`to_bytes`:

**to_bytes**
/////////////

Converts arbitrary byte-convertable input to bytes while handling errors.

.. code:: python

    >>> vistir.misc.to_bytes("this is some text")
    b'this is some text'
    >>> vistir.misc.to_bytes(u"this is some text")
    b'this is some text'


.. _`decode_for_output`:

**decode_for_output**
//////////////////////

Converts an arbitrary text input to output which is encoded for printing to terminal
outputs using the system preferred locale using ``locale.getpreferredencoding(False)``
with some additional hackery on linux systems.

.. code:: python

    >>> vistir.misc.decode_for_output(u"Some text")
    "some default locale encoded text"


🐉 Path Utilities
------------------

**vistir** provides utilities for interacting with filesystem paths:

    * :func:`vistir.path.get_converted_relative_path`
    * :func:`vistir.path.handle_remove_readonly`
    * :func:`vistir.path.is_file_url`
    * :func:`vistir.path.is_readonly_path`
    * :func:`vistir.path.is_valid_url`
    * :func:`vistir.path.mkdir_p`
    * :func:`vistir.path.ensure_mkdir_p`
    * :func:`vistir.path.create_tracked_tempdir`
    * :func:`vistir.path.create_tracked_tempfile`
    * :func:`vistir.path.path_to_url`
    * :func:`vistir.path.rmtree`
    * :func:`vistir.path.safe_expandvars`
    * :func:`vistir.path.set_write_bit`
    * :func:`vistir.path.url_to_path`
    * :func:`vistir.path.walk_up`


.. _`get_converted_relative_path`:

**get_converted_relative_path**
////////////////////////////////

Convert the supplied path to a relative path (relative to :data:`os.curdir`)


.. code:: python

    >>> os.chdir('/home/user/code/myrepo/myfolder')
    >>> vistir.path.get_converted_relative_path('/home/user/code/file.zip')
    './../../file.zip'
    >>> vistir.path.get_converted_relative_path('/home/user/code/myrepo/myfolder/mysubfolder')
    './mysubfolder'
    >>> vistir.path.get_converted_relative_path('/home/user/code/myrepo/myfolder')
    '.'


.. _`handle_remove_readonly`:

**handle_remove_readonly**
///////////////////////////

Error handler for shutil.rmtree.

Windows source repo folders are read-only by default, so this error handler attempts to
set them as writeable and then proceed with deletion.

This function will call check :func:`vistir.path.is_readonly_path` before attempting to
call :func:`vistir.path.set_write_bit` on the target path and try again.


.. _`is_file_url`:

**is_file_url**
////////////////

Checks whether the given url is a properly formatted ``file://`` uri.

.. code:: python

    >>> vistir.path.is_file_url('file:///home/user/somefile.zip')
    True
    >>> vistir.path.is_file_url('/home/user/somefile.zip')
    False


.. _`is_readonly_path`:

**is_readonly_path**
/////////////////////

Check if a provided path exists and is readonly by checking for ``bool(path.stat & stat.S_IREAD) and not os.access(path, os.W_OK)``

.. code:: python

    >>> vistir.path.is_readonly_path('/etc/passwd')
    True
    >>> vistir.path.is_readonly_path('/home/user/.bashrc')
    False


.. _`is_valid_url`:

**is_valid_url**
/////////////////

Checks whether a URL is valid and parseable by checking for the presence of a scheme and
a netloc.

.. code:: python

    >>> vistir.path.is_valid_url("https://google.com")
    True
    >>> vistir.path.is_valid_url("/home/user/somefile")
    False


.. _`mkdir_p`:

**mkdir_p**
/////////////

Recursively creates the target directory and all of its parents if they do not
already exist.  Fails silently if they do.

.. code:: python

    >>> os.mkdir('/tmp/test_dir')
    >>> os.listdir('/tmp/test_dir')
    []
    >>> vistir.path.mkdir_p('/tmp/test_dir/child/subchild/subsubchild')
    >>> os.listdir('/tmp/test_dir/child/subchild')
    ['subsubchild']


.. _`ensure_mkdir_p`:

**ensure_mkdir_p**
///////////////////

A decorator which ensures that the caller function's return value is created as a
directory on the filesystem.

.. code:: python

    >>> @ensure_mkdir_p
    def return_fake_value(path):
        return path
    >>> return_fake_value('/tmp/test_dir')
    >>> os.listdir('/tmp/test_dir')
    []
    >>> return_fake_value('/tmp/test_dir/child/subchild/subsubchild')
    >>> os.listdir('/tmp/test_dir/child/subchild')
    ['subsubchild']


.. _`create_tracked_tempdir`:

**create_tracked_tempdir**
////////////////////////////

Creates a tracked temporary directory using :class:`~vistir.path.TemporaryDirectory`, but does
not remove the directory when the return value goes out of scope, instead registers a
handler to cleanup on program exit.

.. code:: python

    >>> temp_dir = vistir.path.create_tracked_tempdir(prefix="test_dir")
    >>> assert temp_dir.startswith("test_dir")
    True
    >>> with vistir.path.create_tracked_tempdir(prefix="test_dir") as temp_dir:
        with io.open(os.path.join(temp_dir, "test_file.txt"), "w") as fh:
            fh.write("this is a test")
    >>> os.listdir(temp_dir)


.. _`create_tracked_tempfile`:

**create_tracked_tempfile**
////////////////////////////

Creates a tracked temporary file using ``vistir.compat.NamedTemporaryFile``, but creates
a ``weakref.finalize`` call which will detach on garbage collection to close and delete
the file.

.. code:: python

    >>> temp_file = vistir.path.create_tracked_tempfile(prefix="requirements", suffix="txt")
    >>> temp_file.write("some\nstuff")
    >>> exit()


.. _`path_to_url`:

**path_to_url**
////////////////

Convert the supplied local path to a file uri.

.. code:: python

    >>> path_to_url("/home/user/code/myrepo/myfile.zip")
    'file:///home/user/code/myrepo/myfile.zip'


.. _`rmtree`:

**rmtree**
///////////

Stand-in for :func:`~shutil.rmtree` with additional error-handling.

This version of `rmtree` handles read-only paths, especially in the case of index files
written by certain source control systems.

.. code:: python

    >>> vistir.path.rmtree('/tmp/test_dir')
    >>> [d for d in os.listdir('/tmp') if 'test_dir' in d]
    []

.. note::

    Setting `ignore_errors=True` may cause this to silently fail to delete the path


.. _`safe_expandvars`:

**safe_expandvars**
////////////////////

Call :func:`os.path.expandvars` if value is a string, otherwise do nothing.

.. code:: python

    >>> os.environ['TEST_VAR'] = "MY_TEST_VALUE"
    >>> vistir.path.safe_expandvars("https://myuser:${TEST_VAR}@myfakewebsite.com")
    'https://myuser:MY_TEST_VALUE@myfakewebsite.com'


.. _`set_write_bit`:

**set_write_bit**
//////////////////

Set read-write permissions for the current user on the target path.  Fail silently
if the path doesn't exist.

.. code:: python

    >>> vistir.path.set_write_bit('/path/to/some/file')
    >>> with open('/path/to/some/file', 'w') as fh:
            fh.write("test text!")


.. _`url_to_path`:

**url_to_path**
////////////////

Convert a valid file url to a local filesystem path. Follows logic taken from pip.

.. code:: python

    >>> vistir.path.url_to_path("file:///home/user/somefile.zip")
    '/home/user/somefile.zip'
