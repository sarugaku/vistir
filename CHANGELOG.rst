0.5.2 (2020-05-20)
==================

Features
--------

- ``vistir.compat`` now includes a backport of ``os.path.samefile`` for use on Windows on python 2.7.  `#112 <https://github.com/sarugaku/vistir/issues/112>`_


0.5.1 (2020-05-14)
==================

Bug Fixes
---------

- Fixed an issue which caused failures when calling ``contextmanagers.atomic_open_for_write`` due to assumed permission to call ``chmod`` which may not always be possible.  `#110 <https://github.com/sarugaku/vistir/issues/110>`_
  
- Fixed several bugs with encoding of stream output on Windows and filesystem paths on OSX as well as Windows.  `#111 <https://github.com/sarugaku/vistir/issues/111>`_


0.5.0 (2020-01-13)
==================

Features
--------

- Reimplemented ``vistir.contextmanagers.open_file`` to fall back to ``urllib.urlopen`` in the absence of ``requests``, which is now an optional extra.  `#102 <https://github.com/sarugaku/vistir/issues/102>`_
  

Bug Fixes
---------

- Fixed a bug which caused ``path_to_url`` to sometimes fail to properly encode surrogates using utf-8 on windows using python 3.  `#100 <https://github.com/sarugaku/vistir/issues/100>`_


0.4.3 (2019-07-09)
==================

Bug Fixes
---------

- Added compatibility shim for ``TimeoutError`` exception handling.  `#92 <https://github.com/sarugaku/vistir/issues/92>`_
  
- Exceptions are no longer suppressed after being handled during ``vistir.misc.run``.  `#95 <https://github.com/sarugaku/vistir/issues/95>`_
  
- The signal handler for ``VistirSpinner`` will no longer cause deadlocks when ``CTRL_BREAK_EVENTS`` occur on windows.  `#96 <https://github.com/sarugaku/vistir/issues/96>`_


0.4.2 (2019-05-19)
==================

Features
--------

- Shortened windows paths will now be properly resolved to the full path by ``vistir.path.normalize_path``.  `#90 <https://github.com/sarugaku/vistir/issues/90>`_
  

Bug Fixes
---------

- Corrected argument order of ``icacls`` command for fixing permission issues when removing paths on windows.  `#86 <https://github.com/sarugaku/vistir/issues/86>`_
  
- Fixed an issue which caused color wrapping of standard streams on windows to fail to surface critical attributes.  `#88 <https://github.com/sarugaku/vistir/issues/88>`_


0.4.1 (2019-05-15)
==================

Features
--------

- Added expanded functionality to assist with the removal of read-only paths on Windows via ``icacls`` system calls if necessary.  `#81 <https://github.com/sarugaku/vistir/issues/81>`_
  
- Improved ``fs_encode`` compatibility shim in ``vistir.compat`` for handling of non-UTF8 data.  `#83 <https://github.com/sarugaku/vistir/issues/83>`_
  

Bug Fixes
---------

- Fixed a bug with ``vistir.misc.echo`` accidentally wrapping streams with ``colorama`` when it was not needed.
  Fixed a bug with rendering colors in text streams.  `#82 <https://github.com/sarugaku/vistir/issues/82>`_
  
- Fixed ``vistir.misc.to_bytes`` implementation to respect supplied encoding.  `#83 <https://github.com/sarugaku/vistir/issues/83>`_
  
- Blocking calls to ``vistir.misc.run`` will now properly handle ``KeyboardInterrupt`` events by terminating the subprocess and returning the result.  `#84 <https://github.com/sarugaku/vistir/issues/84>`_


0.4.0 (2019-04-10)
==================

Features
--------

- Added full native support for windows unicode consoles and the extended unicode character set when using ``vistir.misc.StreamWrapper`` instances via ``vistir.misc.get_wrapped_stream`` and ``vistir.misc.get_text_stream``.  `#79 <https://github.com/sarugaku/vistir/issues/79>`_
  

Bug Fixes
---------

- Fixed a bug which caused test failures due to generated paths on *nix based operating systems which were too long.  `#65 <https://github.com/sarugaku/vistir/issues/65>`_
  
- Fixed a bug which caused spinner output to sometimes attempt to double encode on python 2, resulting in failed output encoding.  `#69 <https://github.com/sarugaku/vistir/issues/69>`_
  
- Fixed a bug with the ``rmtree`` error handler implementation in ``compat.TemporaryDirectory`` which caused cleanup to fail intermittently on windows.  `#72 <https://github.com/sarugaku/vistir/issues/72>`_
  
- Fixed an issue where paths could sometimes fail to be fs-encoded properly when using backported ``NamedTemporaryFile`` instances.  `#74 <https://github.com/sarugaku/vistir/issues/74>`_
  
- Fixed a bug in ``vistir.misc.locale_encoding`` which caused invocation of a non-existent method called ``getlocaleencoding`` which forced all systems to use default encoding of ``ascii``.  `#78 <https://github.com/sarugaku/vistir/issues/78>`_


0.3.1 (2019-03-02)
==================

Features
--------

- Added a custom cursor hiding implementation to avoid depending on the cursor library, which was re-released under the GPL.  `#57 <https://github.com/sarugaku/vistir/issues/57>`_


0.3.0 (2019-01-01)
==================

Features
--------

- Added a new ``vistir.misc.StreamWrapper`` class with ``vistir.misc.get_wrapped_stream()`` to wrap existing streams
  and ``vistir.contextmanagers.replaced_stream()`` to temporarily replace a stream.  `#48 <https://github.com/sarugaku/vistir/issues/48>`_

- Added new entries in ``vistir.compat`` to support movements to ``collections.abc``: ``Mapping``, ``Sequence``, ``Set``, ``ItemsView``.  `#51 <https://github.com/sarugaku/vistir/issues/51>`_

- Improved ``decode_for_output`` to handle decoding failures gracefully by moving to an ``replace`` strategy.
  Now also allows a translation map to be provided to translate specific non-ascii characters when writing to outputs.  `#52 <https://github.com/sarugaku/vistir/issues/52>`_

- Added support for properly encoding and decoding filesystem paths at the boundaries across python versions and platforms.  `#53 <https://github.com/sarugaku/vistir/issues/53>`_


Bug Fixes
---------

- Fix bug where FileNotFoundError is not imported from compat for rmtree  `#46 <https://github.com/sarugaku/vistir/issues/46>`_

- Fixed a bug with exception handling during ``_create_process`` calls.  `#49 <https://github.com/sarugaku/vistir/issues/49>`_

- Environment variables will now be properly passed through to ``run``.  `#55 <https://github.com/sarugaku/vistir/issues/55>`_


0.2.5 (2018-11-21)
==================

Features
--------

- Added the ability to always write spinner output to stderr using ``write_to_stdout=False``.  `#40 <https://github.com/sarugaku/vistir/issues/40>`_

- Added extra path normalization and comparison utilities.  `#42 <https://github.com/sarugaku/vistir/issues/42>`_


0.2.4 (2018-11-12)
==================

Features
--------

- Remove additional text for ok and fail state  `#35 <https://github.com/sarugaku/vistir/issues/35>`_

- Backported compatibility shims from ``CPython`` for improved cleanup of readonly temporary directories on cleanup.  `#38 <https://github.com/sarugaku/vistir/issues/38>`_


0.2.3 (2018-10-29)
==================

Bug Fixes
---------

- Improved handling of readonly path write-bit-setting.  `#32 <https://github.com/sarugaku/vistir/issues/32>`_

- Fixed a bug with encoding of output streams for dummy spinner and formatting exceptions.  `#33 <https://github.com/sarugaku/vistir/issues/33>`_


0.2.2 (2018-10-26)
==================

Bug Fixes
---------

- Fixed a bug in the spinner implementation resulting in a failure to initialize colorama which could print control characters to the terminal on windows.  `#30 <https://github.com/sarugaku/vistir/issues/30>`_


0.2.1 (2018-10-26)
==================

Features
--------

- Implemented ``vistir.misc.create_tracked_tempdir``, which allows for automatically cleaning up resources using weakreferences at interpreter exit.  `#26 <https://github.com/sarugaku/vistir/issues/26>`_


Bug Fixes
---------

- Fixed a bug with string encodings for terminal colors when using spinners.  `#27 <https://github.com/sarugaku/vistir/issues/27>`_

- Modified spinners to prefer to write to ``sys.stderr`` by default and to avoid writing ``None``, fixed an issue with signal registration on Windows.  `#28 <https://github.com/sarugaku/vistir/issues/28>`_


0.2.0 (2018-10-24)
==================

Features
--------

- Add windows compatible term colors and cursor toggles via custom spinner wrapper.  `#19 <https://github.com/sarugaku/vistir/issues/19>`_

- Added new and improved functionality with fully integrated support for windows async non-unicode spinner.  `#20 <https://github.com/sarugaku/vistir/issues/20>`_

- ``vistir.contextmanager.spinner`` and ``vistir.spin.VistirSpinner`` now provide ``write_err`` to write to standard error from the spinner.  `#22 <https://github.com/sarugaku/vistir/issues/22>`_

- Added ``vistir.path.create_tracked_tempfile`` to the API for weakref-tracked temporary files.  `#26 <https://github.com/sarugaku/vistir/issues/26>`_


Bug Fixes
---------

- Add compatibility shim for ``WindowsError`` issues.  `#18 <https://github.com/sarugaku/vistir/issues/18>`_

- ``vistir.contextmanager.spinner`` and ``vistir.spin.VistirSpinner`` now provide ``write_err`` to write to standard error from the spinner.  `#23 <https://github.com/sarugaku/vistir/issues/23>`_

- Suppress ``ResourceWarning`` at runtime if warnings are suppressed in general.  `#24 <https://github.com/sarugaku/vistir/issues/24>`_


0.1.7 (2018-10-11)
==================

Features
--------

- Updated ``misc.run`` to accept new arguments for ``spinner``, ``combine_stderr``, and ``display_limit``.  `#16 <https://github.com/sarugaku/vistir/issues/16>`_


0.1.6 (2018-09-13)
==================

Features
--------

- Made ``yaspin`` an optional dependency which can be added as an extra by using ``pip install vistir[spinner]`` and can be toggled with ``vistir.misc.run(...nospin=True)``.  `#12 <https://github.com/sarugaku/vistir/issues/12>`_

- Added ``verbose`` flag to ``vistir.misc.run()`` to provide a way to prevent printing all subprocess output.  `#13 <https://github.com/sarugaku/vistir/issues/13>`_


0.1.5 (2018-09-07)
==================

Features
--------

- Users may now pass ``block=False`` to create nonblocking subprocess calls to ``vistir.misc.run()``.
  ``vistir.misc.run()`` will now provide a spinner when passed ``spinner=True``.  `#11 <https://github.com/sarugaku/vistir/issues/11>`_


Bug Fixes
---------

- ``vistir.misc.run()`` now provides the full subprocess object without communicating with it when passed ``return_object=True``.  `#11 <https://github.com/sarugaku/vistir/issues/11>`_


0.1.4 (2018-08-18)
==================

Features
--------

- Implemented ``vistir.path.ensure_mkdir_p`` decorator for wrapping the output of a function call to ensure it is created as a directory.

  Added ``vistir.path.create_tracked_tmpdir`` functionality for creating a temporary directory which is tracked using an ``atexit`` handler rather than a context manager.  `#7 <https://github.com/sarugaku/vistir/issues/7>`_


Bug Fixes
---------

- Use native implementation of ``os.makedirs`` to fix still-broken ``mkdir_p`` but provide additional error-handling logic.  `#6 <https://github.com/sarugaku/vistir/issues/6>`_


0.1.3 (2018-08-18)
==================

Bug Fixes
---------

- Fixed an issue which caused ``mkdir_p`` to use incorrect permissions and throw errors when creating intermediary paths.  `#6 <https://github.com/sarugaku/vistir/issues/6>`_


0.1.2 (2018-08-18)
==================

Features
--------

- Added ``mode`` parameter to ``vistir.path.mkdir_p``.  `#5 <https://github.com/sarugaku/vistir/issues/5>`_


0.1.1 (2018-08-14)
==================

Features
--------

- Added suport for coverage and tox builds.  `#2 <https://github.com/sarugaku/vistir/issues/2>`_

- Enhanced subprocess runner to reproduce the behavior of pipenv's subprocess runner.  `#4 <https://github.com/sarugaku/vistir/issues/4>`_


Bug Fixes
---------

- Fixed an issue where ``vistir.misc.run`` would fail to encode environment variables to the proper filesystem encoding on windows.  `#1 <https://github.com/sarugaku/vistir/issues/1>`_

- Fixed encoding issues when passing commands and environments to ``vistir.misc.run()``.  `#3 <https://github.com/sarugaku/vistir/issues/3>`_


0.1.0 (2018-08-12)
=======================

Features
--------

- Initial commit and release  `#0 <https://github.com/sarugaku/vistir/issues/0>`_
