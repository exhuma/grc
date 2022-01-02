Stream Coloriser
================

.. image:: https://readthedocs.org/projects/strec/badge/?version=latest
   :target: https://strec.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


*strec* allows to colorise a stream (like ``stdout`` or ``stderr``) by mapping
regular expression groups to color names.

See `the full documentation`_ for more information.

Possible Use-Cases
------------------

* Colorise log-files during monitoring::

   tail -f /var/log/apache/access.log | strec -c /path/to/apache-colors.yml

* Apply coloring rules to existing commands::

   strec -- ls -l

* Alias existing commands with their colorised wrapper::

   alias ls="strec -- ls"


.. _the full documentation: https://strec.readthedocs.io/en/latest/?badge=latest
