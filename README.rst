Allure-Pytest-Adaptor
=====================

.. image:: https://pypip.in/v/pytest-allure-adaptor/badge.png
        :alt: Release Status
        :target: https://pypi.python.org/pypi/pytest-allure-adaptor
.. image:: https://pypip.in/d/pytest-allure-adaptor/badge.png
        :alt: Downloads
        :target: https://pypi.python.org/pypi/pytest-allure-adaptor

Плагин для ``py.test`` который может генерировать отчеты в удобочитаемом виде для ``allure-report``

Usage
=====
.. code:: python

 py.test --alluredir [path_to_report_dir]
 # WARNING [path_to_report_dir] will be purged at first run


Плагин автоматически подключается к ``py.test`` через ``entry point``, если установлен.

Подключение плагина в IDE:

.. code:: python

 pytest_plugins = 'allure.pytest_plugin',\


Advanced usage
==============

В плагине есть возможность генерировать данные сверх того, что делает ``pytest``.

Attachments
===========

Для того, чтобы сохранить что-нибудь в тесте:

.. code:: python

 import allure

 def test_foo():
     allure.attach('my attach', 'Hello, World')


Steps
=====

Для того, чтобы побить тест на шаги:

.. code:: python

 import pytest

 def test_foo():
     with pytest.allure.step('step one'):
         # do stuff

     with pytest.allure.step('step two'):
         # do more stuff


Работает и как декоратор.
По умолчанию название степа - это имя декорируемого метода

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


При необходимости использования step'ов в коде, который нужен и без pytest, вместо ``pytest.allure.step`` можно использовать ``allure.step``:

.. code:: python

 import allure

 @allure.step('some operation')
 def do_operation():
     # do stuff


Для фикстур поддержка несколько ограничена.


Severity
========

Для тестов, модулей и классов можно задавать приоритеты:

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


Чтобы запустить тесты только определенных приоритетов:

.. code:: rest

 py.test my_tests/ --allure_severities=critical,blocker


Features & Stories
========

Также для тестов и классов можно задавать feature и story:

.. code:: python

 import allure


 @allure.feature('Feature1')
 @allure.story('Story1')
 def test_minor():
     assert False


 @allure.feature('Feature2')
 @allure.story('Story2')
 class TestBar:

     # will have 'Feature2 and Story2'
     def test_bar(self):
         pass


Чтобы запустить тесты только определенных Feature и Story (story без feature указывать нельзя, все тесты будут пропущены):

.. code:: rest

 py.test my_tests/ --allure_features=feature1,feature2
 py.test my_tests/ --allure_features=feature1,feature2 --allure_stories=story1,story2



Extention
=========

Для использования в других фреймворках выделен класс ``allure.common.AllureImpl``, облегчающий создание привязок.
