Installation
============

When I was writing ``grc`` I wanted it to be free of dependencies. The
rationale behind this is that you can safely install it into your system
*without* using ``virtualenv``. Only one external dependency remains (pyyaml),
but I aim to remove that eventually.

Given that ``pyyaml`` is a fairly harmless dependency (i.e. it's not a big
framework), installation into your system, even with this dependency should be
safe.

Installation is as easy as typing::

    pip install grc

or::

    easy_install grc

