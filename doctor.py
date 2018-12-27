# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/pydoctor/blob/master/NOTICE.txt

"""Show useful things about a Python installation.

Can be used without installation:

    wget -qO - http://bit.ly/pydoctor | python -

"""

from __future__ import print_function, unicode_literals

import contextlib
import locale
import os
import os.path
import re
import platform
import sys


SECTIONS = []
SECTION_MAP = {}


def section(name):
    """Declare a function for handling a section of the diagnosis."""
    SECTIONS.append(name)

    def decorator(func):
        SECTION_MAP[name] = func
        return func
    return decorator


print_ = print
INDENT = 0


def print(*stuff):
    """Our own indent-aware print function."""
    if INDENT:
        print_(" "*INDENT, end="")
    print_(*stuff)


@contextlib.contextmanager
def indent():
    """Indent nested prints by a certain amount."""
    global INDENT
    old_indent = INDENT
    INDENT += 4
    try:
        yield None
    finally:
        INDENT = old_indent


def more_about_file(filename, seen=None):
    """Print more information about a file.

    `seen` is a set of filename already seen, for dealing with symlink loops.

    """
    seen = seen or set()
    with indent():
        if not os.path.exists(filename):
            print("which doesn't exist")
        if os.path.islink(filename):
            link = os.readlink(filename)
            print("which is a symlink to: {0!r}".format(link))
            if link in seen:
                print("which we have seen already")
            seen.add(link)
            alink = os.path.abspath(os.path.join(os.path.dirname(filename), link))
            if alink != link:
                with indent():
                    print("which resolves to: {0!r}".format(alink))
                if alink in seen:
                    print("which we have seen already")
                    return
                seen.add(alink)
                link = alink
            more_about_file(link, seen)


def might_be_a_file(text):
    """This text might be a file, and if it seems like it is, show more info."""
    if "/" in text or "\\" in text:
        more_about_file(text)


@section("version")
def show_version():
    """The version of Python, and other details."""
    print("Python version:\n    {0}".format(sys.version.replace("\n", "\n    ")))
    print("Python implementation: {0!r}".format(platform.python_implementation()))
    print("Python executable: {0!r}".format(sys.executable))
    more_about_file(sys.executable)
    print("Python prefix: {0!r}".format(sys.prefix))
    more_about_file(sys.prefix)
    if hasattr(sys, "real_prefix"):
        print("This is a virtualenv.")
        with indent():
            print("The real prefix is: {0!r}".format(sys.real_prefix))
            more_about_file(sys.real_prefix)
    else:
        print("This is not a virtualenv.")


@section("os")
def show_os():
    """Details of the operating system."""
    print("Current directory: {0!r}".format(os.getcwd()))
    more_about_file(os.getcwd())
    print("Platform: {0!r}".format(platform.platform()))
    print("uname: {0!r}".format(platform.uname()))

    re_envs = r"^(COVER|NOSE|PEX|PIP|PY|VIRTUALENV|WORKON)"
    envs = [ename for ename in os.environ if re.match(re_envs, ename)]
    if envs:
        print("Environment variables:")
        with indent():
            for env in sorted(envs):
                val = os.environ[env]
                print("{0} = {1!r}".format(env, val))
                might_be_a_file(val)
    else:
        print("Environment variables: none")


@section("sizes")
def show_sizes():
    """Sizes of integers and pointers."""
    if sys.maxsize == 2**63-1:
        indicates = "indicating 64-bit"
    elif sys.maxsize == 2**31-1:
        indicates = "indicating 32-bit"
    else:
        indicates = "not sure what that means"
    print("sys.maxsize: {0!r}, {1}".format(sys.maxsize, indicates))
    if hasattr(sys, "maxint"):
        print("sys.maxint: {0!r}".format(sys.maxint))
    else:
        print("sys.maxint doesn't exist")


@section("encoding")
def show_encoding():
    """Information about encodings and Unicode."""
    if sys.version_info < (3, 0):
        if sys.maxunicode == 1114111:
            indicates = "indicating a wide Unicode build"
        elif sys.maxunicode == 65535:
            indicates = "indicating a narrow Unicode build"
    else:
        indicates = "as all Python 3 have"
    print("sys.maxunicode: {0!r}, {1}".format(sys.maxunicode, indicates))

    print("sys.getdefaultencoding(): {0!r}".format(sys.getdefaultencoding()))
    print("sys.getfilesystemencoding(): {0!r}".format(sys.getfilesystemencoding()))
    print("locale.getpreferredencoding(): {0!r}".format(locale.getpreferredencoding()))
    print("sys.stdin.encoding: {0!r}".format(sys.stdin.encoding))
    print("sys.stdout.encoding: {0!r}".format(sys.stdout.encoding))


@section("locale")
def show_locale():
    """Information about locale."""
    print("locale.getpreferredencoding(): {0!r}".format(locale.getpreferredencoding()))
    for name in dir(locale):
        if name.startswith("LC_") and name != "LC_ALL":
            val = locale.getlocale(getattr(locale, name))
            print("locale.getlocale({0}): {1!r}".format(name, val))


@section("path")
def show_path():
    """Details of the path used to find imports."""
    print("sys.path:")
    with indent():
        for p in sys.path:
            print(repr(p))
            more_about_file(p or ".")


def main(words):
    """Run the doctor!"""
    if "help" in words or "--help" in words:
        print("doctor.py [ SECTION ... ]")
        print("Sections are:")
        with indent():
            for section in SECTIONS:
                fn = SECTION_MAP.get(section)
                print("{0:10s}   {1}".format(section, fn.__doc__ or ""))
            print("{0:10s}   {1}".format("all", "All of the above"))
        return

    if not words or words == ["all"]:
        words = SECTIONS

    for word in words:
        fn = SECTION_MAP.get(word)
        if not fn:
            print("*** Don't understand {0!r}".format(word))
        else:
            print("\n--- {0} {1}".format(word, "-"*(40-len(word))))
            if fn.__doc__:
                print("# {0}".format(fn.__doc__))
            fn()


if __name__ == "__main__":
    main(sys.argv[1:])
