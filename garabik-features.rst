This file contains a quick feature-analysis of garabik/grc and follows up with
a small prioritisation of implementation.

The following is a list of config-keywords (taken from the grc readme) and a
note whether it's used or not in the official config files.

Analysis/Review
===============

.. note::

  See the next section for prioritisation

* key: regexp (used everywhere: key feature)

  value: any regex

* key: colours (used everywhere: key feature)

  values:

    ``previous`` (used in only one instance: ``contrib/nmh-in-color/configs/conf.mail``)
      Uses the same colour definition as the previous line. The documentation is
      unclear what "previous line" means. Is it the previous matched line? Or
      the previous line from the input?


    ``unchanged``
      Used in many configs (example: "conf.id")
      "grc" expects a colour for each "group" in the regex match.
      "unchanged" is a placeholder for groups that don't need to be colourised.

    ``douple-quoted-string`` (Used only in conf.sql)
    Is injected literally at the beginning of the matched string. The docs say
    that it's eval'ed which I have not confirmed yet. It can f.ex. be used to
    support 256-colours (f.ex.: ``"\033[38;5;172m"``)
* key: command (unused)

  value: any console command

* key: concat (unused)

  value: a filename

* key: skip (used very rarely, example conf.ss)

  values:

  ``yes``
    Don't include the line matching this regex in the output.

* key: replace

  values:

  any string with regex backrefs
    Replaces the current line with the template (using backrefs). All
    subsequent regexes will match against the replaced text

* key: count

  values:

  ``once`` (used sporadically, example=gcc)
    documentation is vague. It states:

      ... if the regexp is matched, its first occurrence is coloured and the
      program will continue with other regexp's.

    Does that mean that only the first occurrence in the line is colored? Or
    does it mean that it is only coloured once per stream? Not sure
  ``more`` (used in many places)
    When this is set, following regexes will be matched without advancing the line.
  ``stop`` (used sporadically)
    When this is set, immediately go to the next line on the input, ignoring any
    regexes following the "stop" rule.
  ``previous`` (only used once in a contrib rule)
    Reuses the same "count" rule as the previous line. The documentation is
    unclear what this means though: Previous *matched* line or previous line in
    the input (even if it didn't match).
  ``block`` (used sporadically)
    starts a block that all should have the same colour (until "unblock") is
    reached.
  ``unblock`` (used almost never)
    Ends a multiline-block that was started with "block"


Prioritisation
==============

Following the above analysis, the features will be implemented in this order:

* ``regexp=...`` **(key feature)**
* ``colours=unchanged`` **(key feature)**
* ``colours=colour_1,colour_2,...,colour_n`` **(key feature)**
* ``count=more``
* ``count=once``
* ``count=stop``
* ``count=block``
* ``count=unblock``
* ``count=previous``
* ``colours=previous``
* ``skip=yes``
* ``replace=...``
* Colour as double-quoted-string
* ``command=...`` *currently unused*
* ``concat=...`` *currently unused*
