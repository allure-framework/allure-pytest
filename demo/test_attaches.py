'''
These tests show some attachment examples

Created on Oct 18, 2013

@author: pupssman
'''

from pytest import allure  # @UnresolvedImport


def test_with_print():
    'this one prinst stuff to stdout'

    print 'Hello'


def test_with_stderr():
    'this one writes stuff to stdderr'

    import sys

    sys.stderr.write('hello\n\n\nthere')


def test_with_stderr_and_stdout():
    'this one writes stuff to both stdderr and stdout'

    import sys

    sys.stdout.write('this goes to stdout\n\n')
    sys.stderr.write('this goes to stderr')


def test_custom_attach():
    allure.attach('Attach with PNG type', 'FooBar', allure.attach_type.PNG)
    allure.attach('Attach with XML type', '<foo><bar/></foo>', allure.attach_type.XML)
