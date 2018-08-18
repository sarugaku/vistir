Implemented ``vistir.path.ensure_mkdir_p`` decorator for wrapping the output of a function call to ensure it is created as a directory.
Added ``vistir.path.create_tracked_tmpdir`` functionality for creating a temporary directory which is tracked using an ``atexit`` handler rather than a context manager.
