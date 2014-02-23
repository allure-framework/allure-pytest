import pytest

from _pytest.junitxml import mangle_testnames

from allure.constants import Status, \
    AttachmentType, Severity, FAILED_STATUSES
from allure.utils import parent_module, parent_down_from_module, \
    severity_of, all_of, get_exception_message
from _pytest.runner import Skipped
from functools import wraps
import argparse
from allure.common import AllureImpl
from collections import namedtuple


def pytest_addoption(parser):
    parser.getgroup("reporting").addoption('--alluredir',
                                           action="store",
                                           dest="allurereportdir",
                                           metavar="DIR",
                                           default=None,
                                           help="Generate Allure report in the specified directory (may not exist)")

    severities = [v for (_, v) in all_of(Severity)]

    def severity_type(string):
        entries = [x.strip() for x in string.split(',')]

        for entry in entries:
            if not entry in severities:
                raise argparse.ArgumentTypeError('Illegal severity value [%s], only values from [%s] are allowed.' % (entry, ', '.join(severities)))

        return entries

    parser.getgroup("general").addoption('--allure_severities',
                                         action="store",
                                         dest="allureseverities",
                                         metavar="SEVERITIES_LIST",
                                         default=None,
                                         type=severity_type,
                                         help="""Comma-separated list of severity names.
                                         Tests only with these severities will be run.
                                         Possible values are:%s.""" % ', '.join(severities))


def pytest_configure(config):
    reportdir = config.option.allurereportdir
    if reportdir and not hasattr(config, 'slaveinput'):
        config._allurexml = AllureTestListener(reportdir, config)
        config.pluginmanager.register(config._allurexml)
        config.pluginmanager.register(AllureCollectionListener(reportdir))
        pytest.allure._allurexml = config._allurexml  # FIXME: maybe we need a different injection mechanism


def pytest_runtest_setup(item):
    severity = severity_of(item)
    if item.config.getoption('--allure_severities') and severity not in item.config.getoption('--allure_severities'):
        pytest.skip("Not running test of severity %s" % severity)


def pytest_namespace():
    class AllureHelper(object):
        """
        This object holds various utility methods used from ``pytest.allure`` namespace, like ``pytest.allure.attach``
        """
        def __init__(self):
            self._allurexml = None  # FIXME: this gets injected in the pytest_configure

        def attach(self, name, contents, type=AttachmentType.TEXT):  # @ReservedAssignment
            """
            Attaches ``contents`` to a current context with given ``name`` and ``type``.
            """
            if self._allurexml:
                self._allurexml.attach(name, contents, type)

        def severity(self, level):
            """
            A decorator factory that returns ``pytest.mark`` for a given allure ``level``.
            """
            return pytest.mark.allure_severity(level)

        def step(self, title):
            """
            A contextmanager/decorator for steps.

            TODO: when moving to python 3, rework this with ``contextlib.ContextDecorator``.

            Usage examples::

              import pytest

              def test_foo():
                 with pytest.allure.step('mystep'):
                     assert False

              @pytest.allure.step('make test data')
              def make_test_data():
                  raise ValueError('No data today')

              def test_bar():
                  assert make_test_data()

              @pytest.fixture()
              @pytest.allure.step('test fixture')
              def steppy_fixture():
                  return 1

              def test_baz(steppy_fixture):
                  assert steppy_fixture
            """
            class StepContext:
                def __init__(self, allure_helper):
                    self.allure_helper = allure_helper
                    self.step = None

                @property
                def allure(self):
                    return self.allure_helper._allurexml

                def __enter__(self):
                    if self.allure:
                        self.step = self.allure.start_step(title)

                def __exit__(self, exc_type, exc_val, exc_tb):  # @UnusedVariable
                    if self.allure:
                        if exc_type is not None:
                            if exc_type == Skipped:
                                self.step.status = Status.SKIPPED
                            else:
                                self.step.status = Status.FAILED
                        else:
                            self.step.status = Status.PASSED
                        self.allure.stop_step()

                def __call__(self, func):
                    """
                    Pretend that we are a decorator -- wrap the ``func`` with self.
                    FIXME: may fail if evil dude will try to reuse ``pytest.allure.step`` instance.
                    """
                    @wraps(func)
                    def impl(*a, **kw):
                        with self:
                            return func(*a, **kw)
                    return impl

            return StepContext(self)

        @property
        def attach_type(self):
            return AttachmentType

        @property
        def severity_level(self):
            return Severity

        def __getattr__(self, attr):
            """
            Provides fancy shortcuts for severity::

                # these are the same
                pytest.allure.CRITICAL
                pytest.allure.severity(pytest.allure.severity_level.CRITICAL)

            """
            if attr in dir(Severity) and not attr.startswith('_'):
                return self.severity(getattr(Severity, attr))
            else:
                raise AttributeError

    return {'allure': AllureHelper()}


class AllureTestListener(object):

    def __init__(self, logdir, config):
        self.impl = AllureImpl(logdir)
        self.config = config

        # FIXME: maybe we should write explicit wrappers?
        self.attach = self.impl.attach
        self.start_step = self.impl.start_step
        self.stop_step = self.impl.stop_step

        self.testsuite = None

    def _stop_case(self, report, status=None):
        """
        Finalizes with important data the test at the top of ``self.stack`` and returns it
        """
        [self.attach(name, contents, AttachmentType.TEXT) for (name, contents) in dict(report.sections).items()]

        if status in FAILED_STATUSES:
            self.impl.stop_case(status,
                                message=get_exception_message(report),
                                trace=report.longrepr or report.wasxfail)
        elif status == Status.SKIPPED:
            # FIXME: see pytest.runner.pytest_runtest_makereport
            self.impl.stop_case(status,
                                message='skipped',
                                trace=type(report.longrepr) == tuple and report.longrepr[2] or report.wasxfail)
        else:
            self.impl.stop_case(status)

    def pytest_runtest_protocol(self, __multicall__, item, nextitem):
        if not self.testsuite:
            module = parent_module(item)

            self.impl.start_suite(name='.'.join(mangle_testnames(module.nodeid.split("::"))),
                                  description=module.module.__doc__ or None)
            self.testsuite = 'Yes'

        name = '.'.join(mangle_testnames([x.name for x in parent_down_from_module(item)]))

        self.impl.start_case(name, description=item.function.__doc__, severity=severity_of(item))

        result = __multicall__.execute()

        if not nextitem or parent_module(item) != parent_module(nextitem):
            self.impl.stop_suite()
            self.testsuite = None

        return result

    def pytest_runtest_logreport(self, report):
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                self._stop_case(report, status=Status.PASSED)
        elif report.failed:
            if report.when != "call":
                self._stop_case(report, status=Status.BROKEN)
            else:
                self._stop_case(report, status=Status.FAILED)
        elif report.skipped:
                self._stop_case(report, status=Status.SKIPPED)

    def pytest_runtest_makereport(self, item, call, __multicall__):
        """
        That's the place we inject extra data into the report object from the actual Item.
        """

        report = __multicall__.execute()
        report.__dict__.update(
            exception=call.excinfo,
            result=self.config.hook.pytest_report_teststatus(report=report)[0])  # get the failed/passed/xpassed thingy
        return report


CollectFail = namedtuple('CollectFail', 'name status message trace')


class AllureCollectionListener(object):
    def __init__(self, logdir):
        self.impl = AllureImpl(logdir)
        self.fails = []

    def pytest_collectreport(self, report):
        if not report.passed:
            if report.failed:
                status = Status.BROKEN
            else:
                status = Status.SKIPPED

            self.fails.append(CollectFail(name=mangle_testnames(report.nodeid.split("::"))[-1],
                                          status=status,
                                          message=get_exception_message(report),
                                          trace=report.longrepr))

    def pytest_collection_finish(self):
        """
        Writes Collection testsuite only if there were failures.
        """

        if self.fails:
            self.impl.start_suite(name='test_collection_phase',
                                  title='Collection phase',
                                  description='This is the tests collection phase. Failures are modules that failed to collect.')
            for fail in self.fails:
                self.impl.start_case(name=fail.name)
                self.impl.stop_case(status=fail.status, message=fail.message, trace=fail.trace)
            self.impl.stop_suite()
