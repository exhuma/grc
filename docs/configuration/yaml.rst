YAML
====

The YAML style configuration is the preferred way to configure colorisations. It
provides a strucured approach and supports different "contexts" (see below)
which make it easier to organise rules.

Syntax
------

As the name implies, this uses YAML_ as config syntax. Comparing to ``.ini`` and
``json`` files (both included in the Python stdlib), this syntax lends itself
much better to the requirements of this application.

Basic structure
---------------

* The config file is separated into sections (contexts). It has to have at least
  the ``root`` context.
* Each context has a list of rules. These rules fire if a line contains a
  given regular expresssion. The first matching rule wins.
* The line will then be replaced with the string contained in the ``replace``
  value. You can use back-refs if you used capture groups in your regular
  expressions. Colours can be insterted using ``{color_name}``. You should
  always insert a ``{reset}`` after using a color, to reset to the terminal
  default. Color names are provided by :py:class:`strec.themes.ansi.ANSI`.
* Rules may define that processing should *not* stop using the ``continue:
  yes`` flag. In that case, the same line will be matched with the following
  rule as well.
* Additionally, rules may "push" another context onto the stack. If that's the
  case, the rule will be processed, and all following lines will be matched
  against rules contained in the context named by the ``push`` value.
* A non-root context, a rule may "pop" the current context from the
  stack using the ``pop: true`` action.

See :ref:`Config Reference` for more details.

Annotated Example
-----------------

.. code-block:: yaml

    ---
    # the primary context. This section must exist!
    root:
        - match: '^(running)(.*)'
          # demonstrating replacements /and/ colorizing
          replace: '*** ${green}\1{reset}\2'

        - match: '^(writing)(.*)'
          replace: '>>> ${yellow}\1{reset}\2'

        - match: '^(reading)(.*)'
          replace: '<<< ${blue}\1{reset}\2'

        - match: '^(Processing dependencies for)(.*)'
          replace: '${green}\1{reset}\2'
          # switch to the "dependencies" context
          # Any subsequent input-lines will use the rules from the
          # "dependencies" context
          push: dependencies

        - match: '^(Installing.*)'
          replace: '>>> ${green}\1{reset}'

    # the "dependencies" context
    dependencies:
        - match: '^(Finished processing dependencies for)(.*)'
          replace: '${green}\1{reset}\2'
          # Revert back to the "root" context
          pop: true

        - match: '^(Searching for )(.*)$'
          replace: '\1${blue}\2{reset}'
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
          continue: true

        # Note that after the above rule, all lines are prepended with
        # additional text. We need to include this in the regex!
        - match: '^ \| (Installing.*)'
          replace: ' | >>> ${green}\1{reset}'

        - match: '^ \| (Running.*)'
          replace: ' | ${green}\1{reset}'

        - match: '^ \| (Best match.*)'
          replace: ' | ${green}\1{reset}'

        - match: '^ \| (WARNING|warning)'
          replace: ' | ${yellow}\1{reset}'

        - match: '^ \| Installed(.*)'
          replace: ' | Installed\1\n'
          pop: true

.. _Config Reference:

Reference
----------

Main Level
~~~~~~~~~~

**root**
    Specifies the primary context

All other keys represent a context you ``pushed`` somewhere.


Contexts
~~~~~~~~

A context is simply a list of rules

Rules
~~~~~

**match**
    *Type*: ``string``

    A `python regular expression`_. If this matches somewhere in the input
    line, all occurrences will be replaced with the string specified in
    ``replace``.

    .. note::

      While YAML does not enforce you to enclose strings in quotes, I is
      strongly recommend you use **single** quotes for regexps to avoid trouble
      with string escapes (backslashes).

    .. note::

      For very long regexes, YAML makes it possible to split them into multiple
      lines. This time, a double-quote is required however to support adding a
      trailing backslash to lines. This trailing backslash joins the following
      line *without* adding a space! Example:

      .. code-block:: yaml

        match: "a very long regular\
          expression"

      The above will result in the string ``a very long regularexpression``


**replace**
    *Type*: ``string``

    If ``continue`` is false (the default), this string will be emitted to
    ``stdout``. Otherwise, this string will be passed to the next matching
    rule. Note that the following rule sees the *modified* string!

**continue**
    *Type*: ``boolean``

    If true, don't write the string yet to ``stdout``. Instead, pass it on to
    the next matching rule.

**push**
    *Type*: ``string``

    Pushes a new context onto the stack. All following lines from ``stdin``
    will be matched against rules in the new context.

**pop**
    *Type*: ``boolean``

    If this is set to true, then return to the previous context after this
    rule has been processed. If in the ``root`` context, this is a no-op.


.. _python regular expression: http://docs.python.org/library/re.html#regular-expression-syntax
