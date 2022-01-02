Stream Coloriser
================

*strec* allows to colorise a stream (like ``stdout`` or ``stderr``) by mapping
regular expression groups to color names.

The project was originally inspired by `garabik/grc
<https://github.com/garabic/grc>`_.

Possible Use-Cases
------------------

* Colorise log-files during monitoring::

   tail -f /var/log/apache/access.log | strec -c /path/to/apache-colors.yml

* Apply coloring rules to existing commands::

   strec -- ls -l

* Alias existing commands with their colorised wrapper::

   alias ls="strec -- ls"

Screenshots
-----------

================ ================
A python setup session
---------------------------------
Before           After
================ ================
|pysetup-shot-b| |pysetup-shot-a|
================ ================

================= =================
Simple aptitude search
-----------------------------------
Before            After
================= =================
|aptitude-shot-b| |aptitude-shot-a|
================= =================

====================== ======================
Apache access_log
---------------------------------------------
Before                 After
====================== ======================
|apache_access-shot-b| |apache_access-shot-a|
====================== ======================

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   installation
   usage
   configuration/index
   inspiration

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. |pysetup-shot-b| image:: /screenshots/pysetup_before.png
.. |pysetup-shot-a| image:: /screenshots/pysetup_after.png
.. |aptitude-shot-b| image:: /screenshots/aptitude_before.png
.. |aptitude-shot-a| image:: /screenshots/aptitude_after.png
.. |apache_access-shot-b| image:: /screenshots/apache_access_before.png
.. |apache_access-shot-a| image:: /screenshots/apache_access_after.png
