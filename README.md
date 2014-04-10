## Allure-Pytest-Adaptor

Плагин для `py.test` который может генерировать отчеты в удобочитаемом виде для `allure-report`

### Usage
```
py.test --alluredir [path_to_report_dir]
```

Плагин автоматически подключается к py.test через entry point, если установлен.

Подключение плагина в IDE:
```python
pytest_plugins = 'allure.pytest_plugin',\
```

### Advanced usage

В плагине есть возможность генерировать данные сверх того, что делает pytest.

#### Attachments

Для того, чтобы сохранить что-нибудь в тесте:

```python
import allure

def test_foo():
    allure.attach('my attach', 'Hello, World')
```

#### Steps

Для того, чтобы побить тест на шаги:

```python
import pytest

def test_foo():
    with pytest.allure.step('step one'):
        # do stuff

    with pytest.allure.step('step two'):
        # do more stuff
```

Работает и как декоратор.
По умолчанию название степа - это имя декорируемого метода

```python
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
```

При необходимости использования step'ов в коде, который нужен и без pytest, вместо ```pytest.allure.step``` можно использовать ```allure.step```:

```python
import allure

@allure.step('some operation')
def do_operation():
    # do stuff
```

Для фикстур поддержка несколько ограничена.


#### Severity

Для тестов, модулей и классов можно задавать приоритеты:

```python
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
```

Чтобы запустить тесты только определенных приоритетов:
```
py.test my_tests/ --allure_severities=critical,blocker
```


### Extention

Для использования в других фреймворках выделен класс `allure.common.AllureImpl`, облегчающий создание привязок.