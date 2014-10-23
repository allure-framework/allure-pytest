# encoding: utf-8

'''
Demo for environment

@author: svchipiga
'''

import allure

def test_write_environment():
    allure.add_environment({'foo': 'bar', 'country': u'Россия'})
    assert True
