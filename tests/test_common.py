"""
Tests for module ``common``

Created on Feb 23, 2014

@author: pupssman
"""
from lxml import etree
from allure.constants import Status


class TestCommonImpl:

    def test_smoke(self, reportdir, allure_impl, schema):
        """
        Check that a very basic common workflow results in a valid XML produced
        """

        allure_impl.start_suite(name='A_suite')
        allure_impl.start_case(name='A_case')
        allure_impl.stop_case(status=Status.PASSED)
        allure_impl.stop_suite()

        assert len(reportdir.listdir()) == 1

        schema.assertValid(etree.parse(str(reportdir.listdir()[0])))

    def test_empty_initial_environment(self, allure_impl):
        assert allure_impl.environment == {}

    def test_not_store_environment_file_if_environment_empty(self, reportdir, allure_impl):
        allure_impl.store_environment()
        assert not reportdir.listdir()

    def test_store_environment_file_if_environment_present(self, reportdir, allure_impl, properties_file_name):
        allure_impl.environment.update({'foo': 'bar'})
        allure_impl.store_environment()
        assert reportdir.listdir()[0].basename == properties_file_name
