"""
Tests for module ``common``

Created on Feb 23, 2014

@author: pupssman
"""
from lxml import etree
from allure.constants import Status


def test_module_is_importable():
    import allure.common  # @UnusedImport


class TestCommonImpl:
    def test_class_exists(self):
        import allure.common as c

        assert c.AllureImpl

    def test_smoke(self, tmpdir, schema):
        """
        Check that a very basic common workflow results in a valid XML produced
        """
        import allure.common as c

        result_dir = tmpdir.mkdir('target')
        impl = c.AllureImpl(str(result_dir))

        impl.start_suite(name='A_suite')
        impl.start_case(name='A_case')
        impl.stop_case(status=Status.PASSED)
        impl.stop_suite()

        assert len(result_dir.listdir()) == 1

        schema.assertValid(etree.parse(str(result_dir.listdir()[0])))
