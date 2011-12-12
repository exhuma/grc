Installation
============

Thanks to the liberal licensing of all third-party dependencies (pyyaml and
pexpect) I could re-package them into the grc namespace. This makes ``grc``
completely standalone. As a result you can safely install it into the system
(i.e. *without* using ``virtualenv``) without the risk of breaking other
packages.

As a consequence, installation is as easy as typing::

    sudo pip install grc

or::

    sudo python setup.py install

.. note:: ``easy_install`` will probably complain about a SandboxViolation
          because the installation needs to write to ``/usr/share/grc`` which
          is outside of the environment supported by ``easy_install``. If
          possible, use ``pip``. If you are still on an older system, run the
          setup script manually as outlined above.
