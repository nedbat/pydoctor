# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/pydoctor/blob/master/NOTICE.txt

"""Show useful things about a Python installation.

Can be used without installation:

    wget -qO - http://bit.ly/pydoctor | python -

"""

# This file should remain compatible with Python 2.7.

from __future__ import print_function, unicode_literals

import contextlib
import glob
import locale
import os
import os.path
import re
import platform
import sys


DOCTOR_VERSION = 9

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
        elif os.path.islink(filename):
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
                    more_about_file(alink, seen)
            else:
                more_about_file(link, seen)
        elif os.path.isdir(filename):
            contents = os.listdir(filename)
            num_entries = len(contents)
            if num_entries == 0:
                print("which is an empty directory")
            elif num_entries == 1:
                print("which is a directory with 1 entry: {0!r}".format(contents[0]))
            else:
                print("which is a directory with {0} entries:".format(num_entries))
                with indent():
                    to_show = 6
                    names = ", ".join(repr(n) for n in contents[:to_show])
                    if num_entries > to_show:
                        more = ", and {0} more".format(num_entries - to_show)
                    else:
                        more = ""
                    print(names + more)
        else:
            print("which is a file {0} bytes long".format(os.path.getsize(filename)))


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
    if hasattr(sys, "base_prefix"):
        print("Python base_prefix: {0!r}".format(sys.base_prefix))
        more_about_file(sys.base_prefix)
    else:
        print("There is no base_prefix")
    if hasattr(sys, "real_prefix"):
        print("This is a virtualenv.")
        with indent():
            print("The real_prefix is: {0!r}".format(sys.real_prefix))
            more_about_file(sys.real_prefix)
    elif hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix:
        print("This is a venv virtualenv.")
    else:
        print("This is not a virtualenv.")
    print("Python build:")
    with indent():
        print("branch: {0!r}".format(platform.python_branch()))
        print("revision: {0!r}".format(platform.python_revision()))


@section("os")
def show_os():
    """Details of the operating system."""
    print("Current directory: {0!r}".format(os.getcwd()))
    more_about_file(os.getcwd())
    print("Platform: {0!r}".format(platform.platform()))
    if sys.platform.startswith("linux"):
        os_release = platform.freedesktop_os_release()
        print("On Linux: {0!r}".format(os_release["PRETTY_NAME"]))
        if "VERSION" in os_release:
            print("Linux version: {0!r}".format(os_release["VERSION"]))
    elif sys.platform.startswith("win32"):
        print("On Windows: {0} {1} {2} {3}".format(*platform.win32_ver()))
    elif sys.platform.startswith("darwin"):
        release, version_info, machine = platform.mac_ver()
        version = "{0} {1} {2}".format(*version_info)
        print("On macOS: {0} {1} {2}".format(release, version, machine))
    else:
        info = platform.system(), platform.release(), platform.version()
        print("On {0!r}: {1} {2}".format(*platform.system_alias(*info)))
    print("uname: {0!r}".format(platform.uname()))


@section("env")
def show_env():
    """Details of the environment."""
    re_envs = r"^(COVER|NOSE|PEX|PIP|PY|TWINE|VIRTUALENV|WORKON)"
    re_cloak = r"API|TOKEN|KEY|SECRET|PASS|SIGNATURE"
    label = "Environment variables matching {0}".format(re_envs)
    envs = [ename for ename in os.environ if re.search(re_envs, ename)]
    if envs:
        print("{0}:".format(label))
        with indent():
            for env in sorted(envs):
                val = os.environ[env]
                cloaked = ""
                if re.search(re_cloak, env):
                    val = re.sub(r"\w", "*", val)
                    cloaked = " (cloaked)"
                print("{0}{1} = {2!r}".format(env, cloaked, val))
                might_be_a_file(val)
                if os.pathsep in val and "WARNINGS" not in env:
                    with indent():
                        print("looks like a path:")
                        with indent():
                            for pathval in val.split(os.pathsep):
                                print("{0!r}".format(pathval))
                                might_be_a_file(pathval)
    else:
        print("{0}: none".format(label))

    print("$PATH:")
    with indent():
        for p in os.environ['PATH'].split(os.pathsep):
            print(repr(p))
            more_about_file(p or ".")


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
    if sys.version_info < (3, 3):
        if sys.maxunicode == 1114111:
            indicates = "indicating a wide Unicode build"
        elif sys.maxunicode == 65535:
            indicates = "indicating a narrow Unicode build"
        else:
            indicates = "not sure what that means"
    else:
        indicates = "as all Python >=3.3 have"
    print("sys.maxunicode: {0!r}, {1}".format(sys.maxunicode, indicates))

    print("sys.getdefaultencoding(): {0!r}".format(sys.getdefaultencoding()))
    print("sys.getfilesystemencoding(): {0!r}".format(sys.getfilesystemencoding()))
    print("locale.getpreferredencoding(): {0!r}".format(locale.getpreferredencoding()))
    print("sys.stdin.encoding: {0!r}".format(sys.stdin.encoding))
    print("sys.stdout.encoding: {0!r}".format(sys.stdout.encoding))
    print("os.device_encoding(0) (stdin): {0!r}".format(os.device_encoding(0)))
    print("os.device_encoding(1) (stdout): {0!r}".format(os.device_encoding(1)))


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
            for pth in sorted(glob.glob(p + "/*.pth")):
                with indent():
                    print("pth file:", repr(pth))
                    with indent():
                        with open(pth) as fpth:
                            print(repr(fpth.read()))


def main(words):
    """Run the doctor!"""
    print("doctor.py version {0}".format(DOCTOR_VERSION))
    print("sys.argv: {0!r}".format(sys.argv))

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
