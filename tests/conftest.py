import os

import pytest

from lxml import etree, objectify

from allure.common import AllureImpl

pytest_plugins = ["pytester"]


@pytest.fixture
def schema():
    """
    schema copied from https://github.com/allure-framework/allure-core/blob/allure-core-1.4.1/allure-model/src/main/resources/allure.xsd
    Returns :py:class:`lxml.etree.XMLSchema` object configured with schema for reports
    """
    path_to_schema = os.path.join(os.path.dirname(__file__), 'allure.xsd')
    return etree.XMLSchema(etree.parse(path_to_schema))


@pytest.fixture
def reportdir(testdir):
    return testdir.tmpdir.join("my_report_dir")


@pytest.fixture(params=['local', 'xdist-parallel'])
def reports_for(request, testdir, reportdir, schema):
    """
    Fixture that takes a map of name-values, runs it with --alluredir,
    parses all the XML, validates them against ``schema`` and
    :returns list of :py:module:`lxml.objectify`-parsed reports

    Parametrized by mode of execution:
      `local` is py.test's default mode
      `xdist-parallel` is via xdist's -n multi-process feature

    Results are expected to be identical.

    TODO: add `xdist-remote` mode
    """
    def impl(body='', extra_run_args=[], **kw):
        testdir.makepyfile(body, **kw)

        resultpath = str(reportdir)
        if request.param == 'xdist-parallel':
            extra_run_args += ['-n', '1']
        testdir.inline_run("--alluredir", resultpath, *extra_run_args)

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


@pytest.fixture
def allure_impl(reportdir):
    return AllureImpl(str(reportdir))


@pytest.fixture(scope="session")
def properties_file_name():
    return "environment.xml"


@pytest.fixture
def environment_xml(reportdir, properties_file_name):
    return lambda: objectify.parse(os.path.join(str(reportdir), properties_file_name)).getroot()
