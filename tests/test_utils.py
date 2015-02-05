# -*- coding: utf-8 -*-

from allure.utils import all_of, unicodify
from hamcrest import assert_that, only_contains, equal_to
import pytest


def test_all_of_ignore_name():
    class A(object):
        name = "long_name"
        value = "val"
        t = "ololo"

    assert_that(all_of(A), only_contains(("t", "ololo"),))


@pytest.mark.parametrize('arg,result', [
    (u'привет', u'привет'),
    (u'привет'.encode('utf-8'), u'привет'),
    (123, u'123'),
    (Exception(u'привет'), u'привет'),
])
def test_unicodify(arg, result):
    assert_that(unicodify(arg), equal_to(result))
