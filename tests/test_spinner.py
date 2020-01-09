# -*- coding=utf-8 -*-
import importlib
import time

import pytest
import six

from vistir.contextmanagers import replaced_stream, replaced_streams

if six.PY2:
    from mock import patch
else:
    from unittest.mock import patch


@pytest.mark.parametrize(
    "nospin, write_to_stdout",
    ((True, True), (True, False), (False, True), (False, False)),
)
def test_spinner_without_yaspin(nospin, write_to_stdout):
    module_prefix = "__builtins__" if six.PY2 else "builtins"
    if six.PY3:
        bi = importlib.import_module(module_prefix)
        import_func = bi.__import__
        del bi
    else:
        import_func = __builtins__["__import__"]

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("yaspin"):
            raise ImportError(name)
        return import_func(name, globals, locals, fromlist, level)

    module_name = "{0}.__import__".format(module_prefix)
    with replaced_streams() as streams:
        stdout, stderr = streams
        if six.PY3:
            with patch(module_name, _import):
                import vistir.spin

                with vistir.spin.create_spinner(
                    spinner_name="bouncingBar",
                    text="Running...",
                    nospin=nospin,
                    write_to_stdout=write_to_stdout,
                ) as spinner:
                    time.sleep(3)
                    spinner.ok("Ok!")
                out = stdout.getvalue().strip(vistir.spin.CLEAR_LINE).strip()
                err = stderr.getvalue().strip(vistir.spin.CLEAR_LINE).strip()
                if write_to_stdout:
                    assert "Ok!" in out.strip().splitlines()[-1], out
                    assert err.strip() == "", err
                else:
                    assert "Ok!" in err.strip().splitlines()[-1], err
        else:
            with patch.dict("vistir.contextmanagers.__builtins__", __import__=_import):
                import vistir.spin

                with vistir.spin.create_spinner(
                    spinner_name="bouncingBar",
                    text="Running...",
                    nospin=nospin,
                    write_to_stdout=write_to_stdout,
                ) as spinner:
                    time.sleep(3)
                    spinner.ok("Ok!")
                out = stdout.getvalue().strip(vistir.spin.CLEAR_LINE).strip()
                err = stderr.getvalue().strip(vistir.spin.CLEAR_LINE).strip()
                if write_to_stdout:
                    assert "Ok!" in out.strip().splitlines()[-1], out
                    assert err.strip() == "", err
                else:
                    assert "Ok!" in err.strip().splitlines()[-1], err


@pytest.mark.parametrize(
    "nospin, write_to_stdout",
    ((True, True), (True, False), (False, True), (False, False)),
)
def test_spinner(monkeypatch, nospin, write_to_stdout):
    with replaced_stream("stdout") as stdout:
        with replaced_stream("stderr") as stderr:
            with monkeypatch.context() as m:
                # m.setenv("VISTIR_DISABLE_COLORS", "1")
                import vistir.spin

                with vistir.spin.create_spinner(
                    spinner_name="bouncingBar",
                    text="Running...",
                    nospin=nospin,
                    write_to_stdout=write_to_stdout,
                ) as spinner:
                    time.sleep(3)
                    spinner.ok("Ok!")
                out = stdout.getvalue().strip(vistir.spin.CLEAR_LINE).strip()
                err = stderr.getvalue().strip(vistir.spin.CLEAR_LINE).strip()
                if write_to_stdout:
                    assert "Ok!" in out.strip().splitlines()[-1], out
                    assert err.strip() == "", err
                else:
                    assert "Ok!" in err.strip().splitlines()[-1], err
