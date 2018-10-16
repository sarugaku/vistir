# -*- coding=utf-8 -*-
import os
import signal
import sys

from .termcolors import colored

import cursor
import functools
try:
    import yaspin
except ImportError:
    yaspin = None
    Spinners = None
else:
    from yaspin.spinners import Spinners

handler = None
if yaspin and os.name == "nt":
    handler = yaspin.signal_handlers.default_handler
elif yaspin and os.name != "nt":
    handler = yaspin.signal_handlers.fancy_handler


class DummySpinner(object):
    def __init__(self, text="", **kwargs):
        self.text = text

    def __enter__(self):
        print(self.text)
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if not exc_type:
            self.ok("Suceeded!")
        print(traceback)
        return False

    def fail(self, exitcode=1, text=None):
        if text:
            print(text)
        raise SystemExit(exitcode, text)

    def ok(self, text=None):
        print(text)
        return 0

    def write(self, text=None):
        print(text)


base_obj = yaspin.core.Yaspin if yaspin is not None else DummySpinner


class VistirSpinner(base_obj):
    def __init__(self, *args, **kwargs):
        """Get a spinner object or a dummy spinner to wrap a context.

        Keyword Arguments:
        :param str spinner_name: A spinner type e.g. "dots" or "bouncingBar" (default: {"bouncingBar"})
        :param str start_text: Text to start off the spinner with (default: {None})
        :param dict handler_map: Handler map for signals to be handled gracefully (default: {None})
        :param bool nospin: If true, use the dummy spinner (default: {False})
        """

        self.handler = handler
        sigmap = {}
        if handler:
            sigmap.update({
                signal.SIGINT: handler,
                signal.SIGTERM: handler
            })
        handler_map = kwargs.pop("handler_map", {})
        if os.name == "nt":
            sigmap[signal.SIGBREAK] = handler
        else:
            sigmap[signal.SIGALRM] = handler
        if handler_map:
            sigmap.update(handler_map)
        spinner_name = kwargs.pop("spinner_name", "bouncingBar")
        text = kwargs.pop("start_text", "") + " " + kwargs.pop("text", "")
        if not text:
            text = "Running..."
        kwargs["sigmap"] = sigmap
        kwargs["spinner"] = getattr(Spinners, spinner_name, Spinners.bouncingBar)
        super(VistirSpinner, self).__init__(*args, **kwargs)
        self.is_dummy = bool(yaspin is None)

    def fail(self, exitcode=1, *args, **kwargs):
        super(VistirSpinner, self).fail(**kwargs)

    def ok(self, *args, **kwargs):
        super(VistirSpinner, self).ok(*args, **kwargs)

    def write(self, *args, **kwargs):
        super(VistirSpinner, self).write(*args, **kwargs)

    def _compose_color_func(self):
        fn = functools.partial(
            colored,
            color=self._color,
            on_color=self._on_color,
            attrs=list(self._attrs),
        )
        return fn

    @staticmethod
    def _hide_cursor():
        cursor.hide()

    @staticmethod
    def _show_cursor():
        cursor.show()

    @staticmethod
    def _clear_line():
        sys.stdout.write(chr(27) + "[K")


def create_spinner(*args, **kwargs):
    nospin = kwargs.pop("nospin", False)
    if nospin:
        return DummySpinner(*args, **kwargs)
    return VistirSpinner(*args, **kwargs)
