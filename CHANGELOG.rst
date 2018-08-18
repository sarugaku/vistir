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
