Installation
============

Installing can simply be done by running::

   pip install grc

or, into userspace (as ``~/.local/bin/grc``) running::

   pip install --user grc

Or, in any case install it into an isolated environment::

   python3 -m venv /path/to/your/installation
   /path/to/your/installation/bin/pip install grc


Config Files
------------

When installing into the system, syntax files will be written to
``/usr/share/grc/conf.d``. Otherwise they will be written into
``~/.grc/conf.d``.
