# encoding: utf-8

'''
Tests for various attachment thingies

Created on Oct 21, 2013

@author: pupssman
'''
import pytest

from hamcrest import has_entries, assert_that, is_, contains, has_property
from allure.constants import AttachmentType
from allure.utils import all_of


@pytest.mark.parametrize('package', ['pytest.allure', 'allure'])
def test_smoke(report_for, package):
    report = report_for("""
    import pytest
    import allure

    def test_x():
        %s.attach('Foo', 'Bar')
    """ % package)

    assert_that(report.findall('test-cases/test-case/attachments/attachment'), contains(has_property('attrib', has_entries(title='Foo'))))


@pytest.mark.parametrize('a_type', map(lambda x: x[0], all_of(AttachmentType)))
def test_attach_types(report_for, a_type):
    report = report_for("""
    import allure as A

    def test_x():
        A.attach('Foo', 'Bar', A.attach_type.%s)
    """ % a_type)

    assert_that(report.find('.//attachment').attrib, has_entries(title='Foo', type=getattr(AttachmentType, a_type).mime_type))


class TestContents:

    @pytest.fixture
    def attach_contents(self, report_for, reportdir):
        """
        Fixture that returns contents of the attachment file for given attach body
        """
        def impl(body):
            report = report_for("""
            from pytest import allure as A

            def test_x():
                A.attach('Foo', %s, A.attach_type.TEXT)
            """ % repr(body))

            filename = report.find('.//attachment').get('source')

            return reportdir.join(filename).read('rb')
        return impl

    def test_ascii(self, attach_contents):
        assert_that(attach_contents('foo\nbar\tbaz'), is_(b'foo\nbar\tbaz'))

    def test_unicode(self, attach_contents):
        assert_that(attach_contents(u'ололо пыщьпыщь').decode('utf-8'), is_(u'ололо пыщьпыщь'))

    def test_broken_unicode(self, attach_contents):
        assert_that(attach_contents(u'ололо пыщьпыщь'.encode('cp1251')), is_(u'ололо пыщьпыщь'.encode('cp1251')))


def test_attach_in_fixture_teardown(report_for):
    """
    Check that calling ``pytest.allure.attach`` in fixture teardown works and attaches it there.
    """
    report = report_for("""
    import pytest

    @pytest.yield_fixture(scope='function')
    def myfix():
        yield
        pytest.allure.attach('Foo', 'Bar')

    def test_x(myfix):
        assert True
    """)

    assert_that(report.find('.//attachment').attrib, has_entries(title='Foo'))


def test_deep_step_attach_contents(report_for, reportdir):
    report = report_for("""
    import pytest

    def test_x():
        with pytest.allure.step('foo'):
            with pytest.allure.step('bar'):
                pytest.allure.attach('ololo', 'pewpew')
    """)
    filename = report.find('.//step//attachment').get('source')

    assert_that(reportdir.join(filename).read('rb'), is_(b'pewpew'))
