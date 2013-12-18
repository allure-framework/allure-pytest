'''
This module holds some basic structure examples -- module tests, class-nested tests, etc
'''


def test_at_module():
    'this is module-level test'
    assert True


def test_also_at_module():
    '''this is another module-level test
    with a multi-line description
    a long one'''
    assert False


class TestClass:
    'A test class!'

    def test_foo(self):
        'some class-level tests'

    def test_bar(self):
        'some more class-level tests'


class TestDeepNest:
    'Outer class for deep nested tests'
    class TestInner:
        'Inner class for deep nested tests'
        def test_deeply_nested(self):
            'this test is nested way too deep)'

    def test_not_so_deep(self):
        'this is not so deeply-nested'
