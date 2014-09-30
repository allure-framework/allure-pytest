import os
import pytest

from lxml import etree, objectify

from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.base_matcher import BaseMatcher

pytest_plugins = ["pytester"]


@pytest.fixture
def schema():
    """
    Returns :py:class:`lxml.etree.XMLSchema` object configured with schema for reports
    """
    path_to_schema = os.path.join(os.path.dirname(__file__), 'allure.xsd')
    return etree.XMLSchema(etree.parse(path_to_schema))


@pytest.fixture
def reportdir(testdir):
    return testdir.tmpdir.join("my_report_dir")


@pytest.fixture
def reports_for(testdir, reportdir, schema):
    """
    Fixture that takes a map of name-values, runs it with --alluredir,
    parses all the XML, validates them against ``schema`` and
    :returns list of :py:module:`lxml.objectify`-parsed reports
    """
    def impl(body='', extra_run_args=[], **kw):
        testdir.makepyfile(body, **kw)

        resultpath = str(reportdir)
        testdir.runpytest("--alluredir", resultpath, *extra_run_args)

        files = [os.path.join(resultpath, f) for f in os.listdir(resultpath) if '-testsuite.xml' in f]

        [schema.assertValid(etree.parse(f)) for f in files]

        return [objectify.parse(f).getroot() for f in files]

    return impl


@pytest.fixture
def report_for(reports_for):
    """
    as ``reports_for``, but returns a single report
    """
    def impl(*a, **kw):
        reports = reports_for(*a, **kw)

        assert len(reports) == 1

        return reports[0]
    return impl


class HasFloat(BaseMatcher):

    def __init__(self, str_matcher):
        self.str_matcher = str_matcher

    def _matches(self, item):
        return self.str_matcher.matches(float(item))

    def describe_to(self, description):
        description.append_text('an object with float ')          \
                    .append_description_of(self.str_matcher)


def has_float(match):
    return HasFloat(wrap_matcher(match))
