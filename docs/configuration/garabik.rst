"grc" style config
==================

This configuration style provides a way to easily reuse configuration files from
grc_.

For details on the configuration, please refer to the documentation of that
project.

Caveat
------

The grc_ config files show inconsistent behaviour with regex group
numbering. This requires a dummy color in the replacement rules in most
cases. **strec** will *always* match the regex-groups with the colour
names when processing grc-config-files so the dummy entries are not necessary.

This however means, that most config-files from grc_ are **not** usable
without modifcation.

Example
~~~~~~~

A rule for `blkid
<https://github.com/garabik/grc/blob/f4a579e08d356a3ea00a8c6fda7de84fff5f676a/colourfiles/conf.blkid#L7>`_
contains 3 colors, but only 2 regex groups. To make this config work in *strec*,
remove the first ``unchanged`` colour:

.. code-block:: diff

    --- conf.blkid  2021-11-14 14:11:25.063093310 +0100
    +++ conf.blkid.strec    2022-01-02 12:15:34.095626658 +0100
    @@ -4,7 +4,7 @@
    ======
    # Blk mapper
    regexp=^/dev/(mapper/)(.+):\s
    -colours=unchanged,underline green,bright_green
    +colours=underline green,bright_green
    ======
    # UUID
    regexp=\sUUID="([^"]+)

.. _grc: https://github.com/garabik/grc
