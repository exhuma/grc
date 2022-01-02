Installation
============

Installing can simply be done by running::

   pip install strec

or, into userspace (as ``~/.local/bin/strec``) running::

   pip install --user strec

Or, in any case install it into an isolated environment::

   python3 -m venv /path/to/your/installation
   /path/to/your/installation/bin/pip install strec


Config Files
------------

When installing into the system, syntax files will be written to
``/usr/share/strec/conf.d``. Otherwise they will be written into
``~/.strec/conf.d``.
