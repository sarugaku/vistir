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
