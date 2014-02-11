# -*- coding: utf-8 -*-

u"""
У этого модуля, как и у его тестов, кириллические описания, данные в юникоде

Created on Oct 19, 2013

@author: pupssman
"""


def test_pass():
    u'Этот тест проходит'

    assert True


def test_fail():
    u'Этот тест падает'

    assert False


def test_raise_cyrilling():
    u'Этот тест выкидывает исключение с русскими буквами'

    raise Exception(u'Невероятная проблема!')
