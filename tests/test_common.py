"""
Tests for module ``common``

Created on Feb 23, 2014

@author: pupssman
"""


def test_module_is_importable():
    import allure.common  # @UnusedImport


class TestCommonImpl:
    def test_class_exists(self):
        import allure.common as c

        assert c.AllureImpl

    def test_smoke(self, tmpdir):
        """
        Check that a very basic common workflow results in a XML produced
        """
        import allure.common as c
        result_dir = tmpdir.mkdir('target')
        impl = c.AllureImpl(str(result_dir))

        impl.start_suite(name='A suite')
        impl.start_case(name='A case')
        impl.stop_case(result='Sucess')
        impl.stop_suite()

        assert result_dir.listdir()
