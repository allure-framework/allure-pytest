# encoding: utf-8

'''
Demo for environment

@author: svchipiga
'''

import allure

def test_store_environment():
    allure.environment(foo='bar', country=u'Россия')
    assert True
