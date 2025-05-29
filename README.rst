########
PyDoctor
########


This is a program that investigates your machine, and prints information about
the Python installation.  It's useful for diagnosing problems on machines you
can't touch yourself.  I've used it for continuous integration machines, and
for helping people remotely.

It reads a lot of information, and prints it out.  That's it.  It does not
change anything on your machine.

If someone asks you to run this and show them the output, please examine the
output first to be sure it doesn't contain information you don't want to share.

You can see a `sample report`_ to get an idea of what to expect.


Running the doctor
==================

The simplest way to run this is directly from GitHub::

    $ wget -qO - https://bit.ly/pydoctor | python -

or::

    $ curl -sL https://bit.ly/pydoctor | python -

or::

    $ python -c "import urllib.request as r; exec(r.urlopen('https://bit.ly/pydoctor').read())"

You can of course also download `doctor.py`_ and read it first to be sure you
like what it will do.

The output consists of a number of sections.  With no arguments, doctor.py will
print everything.  You can specify section names to get just that information.
See ``doctor.py --help`` for details.


Problems
========

If this program fails, or gets something wrong, please open an issue to let
me know.  Pull requests also welcome.


.. _sample report: https://raw.githubusercontent.com/nedbat/pydoctor/master/sample_report.txt
.. _doctor.py: https://raw.githubusercontent.com/nedbat/pydoctor/master/doctor.py
