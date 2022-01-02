Alternatives
============

The original ``grc``
--------------------

Available at https://github.com/garabik/grc

While the original ``grc`` is a bit smarter with subprocesses, this rewrite
focuses on ease of use (including Installation, `Configuration`_ and
`source-code access`_).

Installation should also honour the `Linux FHS`_

``sed`` or ``awk``
------------------

``sed`` and ``awk`` are extremely powerful tools, and can certainly do what
``strec`` does. They will certainly perform better on large streams. It's their
intended use afterall. *However*, they both use an archaic and arcane syntax
for their scripts. Additionally, if you would like to colorize your output with
these, you need to work with ANSI escape sequences. ``strec`` aims to simplify
this by having a more readable `Configuration`_ syntax, and by hiding the ANSI
escape sequences.

See the installation document for more information.

Usage
=====

Configuration
=============

``strec`` searches three locations for configuration files in order:

* ``~/.strec/conf.d/<confname>.yml``
* ``/etc/strec/conf.d/<confname>.yml``
* ``/usr/share/strec/conf.d/<confname>.yml``

The first matching config file wins. This means, you can override any
system-wide configs with your own concoctions.

Syntax
------

``strec`` uses YAML_ as config syntax. Comparing to ``.ini`` and ``json`` files
(both included in the Python stdlib), this syntax lends itself much better to
the requirements of this application.

Basic structure
---------------

* The config file is separated into sections (contexts). It has to have at least
  the ``root`` context.
* Each context has a list of rules. These rules fire if a line contains a
  given regular expresssion. The first matching rule wins.
* The line will then be replaced with the string contained in the ``replace``
  value. You can use back-refs if you used capture groups in your regular
  expressions. Colours can be insterted using ``${t.color_name}``. You should
  always insert a ``${t.normal}`` after using a color, to reset to the terminal
  default. The colors are provided by the package blessings_. The ``t``
  variable is a reference to a ``blessings`` terminal instance so you should be
  able to use it as it is documented on the ``blessings`` homepage.
* Rules may define, that processing should *not* stop using the ``continue:
  yes`` flag. In that case, the same line will be matched with the following
  rule as well.
* Additionally, rules may "push" another context onto the stack. If that's the
  case, the rule will be processed, and all following lines will be matched
  against rules contained in the context named by the ``push`` value.
* If in a non-root context, a rule may "pop" the current context from the
  stack using the ``pop: yes`` action.

.. _blessings: https://github.com/erikrose/blessings

See `Config Reference`_ for more details.

Annotated Example
-----------------

::

    # the primary context. This section must exist!
    root:
        - match: '^(running)(.*)'
          # demonstrating replacements /and/ colorizing
          replace: '*** ${t.green}\1${t.normal}\2'

        - match: '^(writing)(.*)'
          replace: '>>> ${t.yellow}\1${t.normal}\2'

        - match: '^(reading)(.*)'
          replace: '<<< ${t.blue}\1${t.normal}\2'

        - match: '^(Processing dependencies for)(.*)'
          replace: '${t.green}\1${t.normal}\2'
          # switch to the "dependencies" context
          push: dependencies

        - match: '^(Installing.*)'
          replace: '>>> ${t.green}\1${t.normal}'

    # the "dependencies" context
    dependencies:
        - match: '^(Finished processing dependencies for)(.*)'
          replace: '${t.green}\1${t.normal}\2'
          # Revert back to the "root" context
          pop: yes

        - match: '^(Searching for )(.*)$'
          replace: '\1${t.blue}\2${t.normal}'
          # switch to the "dependency" context
          push: dependency

    # the "dependency" context
    dependency:
        # Let's prepend all lines with a small indent and pipe.
        # To do this, we specify a "match-all" regex, replace the line, and
        # specify that we will continue with the next matching rule using
        # "continue"
        - match: '(.*)'
          replace: ' | \1'
          continue: yes

        # Note that after the above rule, all lines are prepended with
        # additional text. We need to include this in the regex!
        - match: '^ \| (Installing.*)'
          replace: ' | >>> ${t.green}\1${t.normal}'

        - match: '^ \| (Running.*)'
          replace: ' | ${t.green}\1${t.normal}'

        - match: '^ \| (Best match.*)'
          replace: ' | ${t.green}\1${t.normal}'

        - match: '^ \| (WARNING|warning)'
          replace: ' | ${t.yellow}\1${t.normal}'

        - match: '^ \| Installed(.*)'
          replace: ' | Installed\1\n'
          pop: yes

Config Reference
================

Main Level
----------

**root**
    Specifies the primary context

All other keys represent a context you ``pushed`` somewhere.


Contexts
--------

A context is simply a list of rules

Rules
-----

**match**
    *Type*: ``string``

    A `python regular expression`_. If this matches somewhere in the input
    line, all occurrences will be replaced with the string specified in
    ``replace``.

    .. note:: While YAML does not enforce you to enclose strings in quotes, I
              is strongly recommend you use **single** quotes for regexps to
              avoid trouble with string escapes (backslashes).

**replace**
    *Type*: ``string``

    If ``continue`` is false (the default), this string will be emitted to
    ``stdout``. Otherwise, this string will be passed to the next matching
    rule. Not that the following rule sees the *modified* string!

    .. note:: While YAML does not enforce you to enclose strings in quotes, I
              is recommend using **single** quotes if using backreferences
              (backslashes).

**continue**
    *Type*: ``boolean``

    If true, don't write the string yet to ``stdout``. Instead, pass it on to
    the next matching rule.

**push**
    *Type*: ``string``

    Pushes a new context onto the stack. All following lines from ``stdin``
    will be matched agains rules in the new context.

    .. note:: This may change in a future release to give you yet more control

**pop**
    *Type*: ``boolean``

    If this is set to true, then return to the previous context after this
    rule has been processed. If in the ``root`` context, this is a no-op.

    .. note:: This may change in a future release to give you yet more control

Footnotes
=========


.. _Linux FHS: http://www.pathname.com/fhs/
.. _source-code access: https://github.com/exhuma/grc
.. _YAML: http://www.yaml.org
.. _python regular expression: http://docs.python.org/library/re.html#regular-expression-syntax
