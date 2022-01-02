Usage
=====

As a pipe element
-----------------

Synopsis
~~~~~~~~

.. code-block:: bash

    <some_process> | strec -c <config-name-or-path>

Example
~~~~~~~

::

    tail -f /var/log/apache2/access.log | strec -c apache_access

**Advantages**
    * Only the stream you are sending to ``strec`` is affected.
    * No known side-effects

**Disadvantages**
    * As ``strec`` only sees a stream, it cannot determine what application is
      emitting the stream. You have to specify the config manually using the
      ``-c`` option.

Spawn a subprocess, capture it's output
---------------------------------------

Synopsis
~~~~~~~~

::

    strec -- <some_procss>

Example
~~~~~~~

::

    strec -- aptitude search python

**Advantages**
    * Much less to type
    * Can auto-detect the config by using the sub-process application name.

**Disadvantages**
    * Spawning a subprocess and interacting with it's IO is non-trivial on a
      TTY/PTY and may be less reliable than using a pipe.
    * To disambiguate the CLI options of ``strec`` with the options of the
      sub-command, the ``--`` separator is needed.
