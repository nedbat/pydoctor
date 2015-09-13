"""Show useful things about a Python installation.

Can be used without installation:

    wget -qO - https://raw.githubusercontent.com/nedbat/pydoctor/master/doctor.py | python -

"""

from __future__ import print_function, unicode_literals

import os
import os.path
import re
import platform
import sys


SECTIONS = []
SECTION_MAP = {}

def section(name):
    SECTIONS.append(name)
    def decorator(func):
        SECTION_MAP[name] = func
        return func
    return decorator


def show_symlink_maybe(filename):
    if os.path.islink(filename):
        link = os.readlink(filename)
        print("  which is a symlink to: {0!r}".format(link))
        alink = os.path.abspath(os.path.join(os.path.dirname(filename), link))
        if alink != link:
            print("    which resolves to: {0!r}".format(alink))


@section("version")
def show_version():
    print("Python version:\n    {0}".format(sys.version.replace("\n", "\n    ")))
    print("Python implementation: {0!r}".format(platform.python_implementation()))
    print("Python executable: {0!r}".format(sys.executable))
    show_symlink_maybe(sys.executable)
    print("Python prefix: {0!r}".format(sys.prefix))
    show_symlink_maybe(sys.prefix)
    if hasattr(sys, "real_prefix"):
        print("This is a virtualenv.")
        print("  The real prefix is: {0!r}".format(sys.real_prefix))
        show_symlink_maybe(sys.real_prefix)
    else:
        print("This is not a virtualenv.")


@section("os")
def show_os():
    print("Current directory: {0!r}".format(os.getcwd()))
    show_symlink_maybe(os.getcwd())
    print("Platform: {0!r}".format(platform.platform()))
    print("uname: {0!r}".format(platform.uname()))

    re_envs = r"^(PY|COVER|NOSE)"
    envs = [ename for ename in os.environ if re.match(re_envs, ename)]
    if envs:
        print("Environment variables:")
        for env in envs:
            print("  {0} = {1!r}".format(env, os.environ[env]))
    else:
        print("Environment variables: none")


@section("sizes")
def show_sizes():
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


@section("path")
def show_path():
    print("sys.path:")
    print("\n".join("    {0!r}".format(p) for p in sys.path))


def main(words):
    if "help" in words or "--help" in words:
        print("Sections are: {0}, or all".format(" ".join(SECTIONS)))
        return

    if not words or words == ["all"]:
        words = SECTIONS

    for word in words:
        fn = SECTION_MAP.get(word)
        if not fn:
            print("*** Don't understand {0!r}".format(word))
        else:
            print("\n--- {0} ----------".format(word))
            fn()


if __name__ == "__main__":
    main(sys.argv[1:])
