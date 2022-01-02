Configuration
=============

When executing, *strec* searches several locations for configuration files in
order:

* ``STREC_CONFIG_PATH`` (environment variable)
* ``~/.strec/conf.d``
* ``/etc/strec/conf.d``
* ``/usr/share/strec/conf.d``

In each path, it supports different filename patterns, each mapping to a
different config-style:

* ``<conf-name>.yml`` maps to the new YAML parser
* ``conf.<conf-name>`` maps to the *grc* compatibility parser

If a command has multiple configurations, the YAML parser wins.

When going through the list of folders, the first matching config file wins.
This means, you can override any system-wide configs with your own definitions.

.. toctree::
    :maxdepth: 2

    yaml
    garabik
