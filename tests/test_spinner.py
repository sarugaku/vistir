# -*- coding=utf-8 -*-

import vistir.spin
import time


def test_spinner(capsys):
    with vistir.spin.create_spinner(spinner_name="bouncingBar", text="Running...", nospin=False) as spinner:
        time.sleep(3)
        spinner.ok("Ok!")
    out, err = capsys.readouterr()
    assert out.strip().endswith("Ok!")
    assert err.strip() == ""
    with vistir.spin.create_spinner(spinner_name="bouncingBar", text="Running...", nospin=False, write_to_stdout=False) as spinner:
        time.sleep(3)
        spinner.ok("Ok!")
    out, err = capsys.readouterr()
    assert err.strip().endswith("Ok!")
    assert out.strip() == ""
