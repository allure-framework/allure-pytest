Allure Pytest Adaptor
=====================

.. image:: https://pypip.in/v/pytest-allure-adaptor/badge.png
        :alt: Release Status
        :target: https://pypi.python.org/pypi/pytest-allure-adaptor
.. image:: https://pypip.in/d/pytest-allure-adaptor/badge.png
        :alt: Downloads
        :target: https://pypi.python.org/pypi/pytest-allure-adaptor

This repository contains a plugin for ``py.test`` which automatically prepares input data used to generate ``Allure Report``.

Usage
=====
.. code:: python

 py.test --alluredir [path_to_report_dir]
 # WARNING [path_to_report_dir] will be purged at first run


This plugin gets automatically connected to ``py.test`` via ``entry point`` if installed.

Connecting to IDE:

.. code:: python

 pytest_plugins = 'allure.pytest_plugin',\


Advanced usage
==============

Attachments
===========

To attach some content to test report:

.. code:: python

 import allure

 def test_foo():
     allure.attach('my attach', 'Hello, World')


Steps
=====

To divide a test into steps:

.. code:: python

 import pytest

 def test_foo():
     with pytest.allure.step('step one'):
         # do stuff

     with pytest.allure.step('step two'):
         # do more stuff


Can also be used as decorators. By default step name is generated from method name:

.. code:: python

 import pytest

 @pytest.allure.step
 def make_test_data_foo():
     # do stuff

 def test_foo():
     assert make_some_data_foo() is not None

 @pytest.allure.step('make_some_data_foo')
 def make_some_data_bar():
     # do another stuff

 def test_bar():
     assert make_some_data_bar() is not None


Steps can also be used without pytest. In that case instead of ``pytest.allure.step`` simply use ``allure.step``:

.. code:: python

 import allure

 @allure.step('some operation')
 def do_operation():
     # do stuff


Steps support is limited when used with fixtures.


Severity
========

Any test, class or module can be marked with different severity:

.. code:: python

 import pytest

 @pytest.allure.severity(pytest.allure.severity_level.MINOR)
 def test_minor():
     assert False


 @pytest.allure.severity(pytest.allure.severity_level.CRITICAL)
 class TestBar:

     # will have CRITICAL priority
     def test_bar(self):
         pass

     # will have BLOCKER priority via a short-cut decorator
     @pytest.allure.BLOCKER
     def test_bar(self):
         pass


To run tests with concrete priority:

.. code:: rest

 py.test my_tests/ --allure_severities=critical,blocker


Extending
=========

Use ``allure.common.AllureImpl`` class to bind your logic to this adapter.








