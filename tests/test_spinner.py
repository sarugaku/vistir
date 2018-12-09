# -*- coding=utf-8 -*-

import pytest
from vistir.contextmanagers import replaced_stream
import time


@pytest.mark.parametrize("nospin, write_to_stdout", (
    (True, True), (True, False),
    (False, True), (False, False)
))
def test_spinner(capture_streams, monkeypatch, nospin, write_to_stdout):
    with replaced_stream("stdout") as stdout:
        with replaced_stream("stderr") as stderr:
            with monkeypatch.context() as m:
                # m.setenv("VISTIR_DISABLE_COLORS", "1")
                import vistir.spin
                with vistir.spin.create_spinner(
                    spinner_name="bouncingBar", text="Running...", nospin=nospin,
                    write_to_stdout=write_to_stdout
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
