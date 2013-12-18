import os
import py
import uuid
import pytest

from lxml import etree
from contextlib import contextmanager
from traceback import format_exception_only

from _pytest.junitxml import mangle_testnames

from allure.structure import Attach, TestCase, Failure, TestSuite, TestStep
from allure.constants import Status, \
    AttachmentType, Severity, FAILED_STATUSES
from allure.utils import sec2ms, parent_module, parent_down_from_module, now, \
    severity_of, all_of
from _pytest.runner import Skipped
from functools import wraps
import argparse


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
        config._allurexml = AllureXML(reportdir, config)
        config.pluginmanager.register(config._allurexml)
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
                        if  exc_type is not None:
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


class AllureXML(object):

    def __init__(self, logdir, config):
        self.logdir = os.path.normpath(os.path.abspath(os.path.expanduser(os.path.expandvars(logdir))))
        self.config = config

        # Delete all files in report directory
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        else:
            for f in os.listdir(self.logdir):
                f = os.path.join(self.logdir, f)
                if os.path.isfile(f):
                    os.unlink(f)

        # That's the state stack. It can contain TestCases or TestSteps.
        # Attaches and steps go to the object at top of the stack.
        self.stack = []

        self.testsuite = None

    def attach(self, title, contents, attach_type):
        """
        Attaches ``contents`` with ``title`` and ``attach_type`` to the current active thing
        """
        attach = Attach(source=self.save_attach(contents, attach_type=attach_type),
                                       title=title,
                                       type=attach_type)
        self.stack[-1].attachments.append(attach)

    def start_step(self, title):
        """
        Starts an new :py:class:`allure.structure.TestStep` with given title,
        pushes it to the ``self.stack`` and returns the step.
        """
        step = TestStep(title=title,
                        start=now(),
                        attachments=[],
                        steps=[])
        self.stack[-1].steps.append(step)
        self.stack.append(step)
        return step

    def stop_step(self):
        """
        Stops the step at the top of ``self.stack``
        """
        step = self.stack.pop()
        step.stop = now()

    def _get_report_kwarg(self, report):
        names = mangle_testnames(report.nodeid.split("::"))

        return {
            'name': getattr(report, 'name', names[-1]),
            'startTime': sec2ms(getattr(report, 'start_time', 0)),
            'stopTime': sec2ms(getattr(report, 'stop_time', 0)),
            'description': getattr(report, 'desc', ''),
            'exceptionMessage': (getattr(report, 'exception', None) and ''.join(format_exception_only(type(report.exception.value),
                                                                                                      report.exception.value)).strip()) or (hasattr(report, 'result') and report.result) or report.outcome
        }

    def _start_case(self, name, severity=Severity.NORMAL):
        """
        Starts a new :py:class:`allure.structure.TestCase` and pushes it to the ``self.stack``
        """
        test = TestCase(title=name,
                        severity=severity,
                        attachments=[],
                        steps=[])
        self.stack.append(test)

    def _stop_case(self, report, **kw):
        """
        Finalizes with important data the test at the top of ``self.stack`` and returns it
        """
        [self.attach(name, contents, AttachmentType.TEXT) for (name, contents) in dict(report.sections).items()]
        kw.update(self._get_report_kwarg(report))
        test = self.stack[-1]
        test.description = kw['description']
        test.status = kw['status']
        test.start = kw['startTime']
        test.stop = kw['stopTime']

        if kw['status'] in FAILED_STATUSES:
            test.failure = Failure(message=kw['exceptionMessage'],
                                        trace=report.longrepr or ' ')
        return test

    def finish_suite(self):
        """
        Writes currently active testuite and prepares the Adaptor for the next one blanking ``self.testsuite``
        """
        self.testsuite.stop = now()

        with self.reportfile('%s-testsuite.xml' % uuid.uuid4()) as f:
            self.write_suite(f, self.testsuite)

        self.testsuite = None

    def pytest_runtest_protocol(self, __multicall__, item, nextitem):
        if not self.testsuite:
            module = parent_module(item)

            self.testsuite = TestSuite(title='.'.join(mangle_testnames(module.nodeid.split("::"))),
                                       description=module.module.__doc__ or None,
                                       tests=[],
                                       start=now())
        name = '.'.join(mangle_testnames([x.name for x in parent_down_from_module(item)]))
        self._start_case(name, severity_of(item))
        result = __multicall__.execute()

        if not nextitem or parent_module(item) != parent_module(nextitem):
            self.finish_suite()

        return result

    def pytest_runtest_logreport(self, report):
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                self.testsuite.tests.append(self._stop_case(report, status=Status.PASSED))
        elif report.failed:
            if report.when != "call":
                self.testsuite.tests.append(self._stop_case(report, status=Status.BROKEN))
            else:
                self.testsuite.tests.append(self._stop_case(report, status=Status.FAILED))
        elif report.skipped:
                self.testsuite.tests.append(self._stop_case(report, status=Status.SKIPPED))

    def pytest_collectstart(self):
        if not self.testsuite:
            self.testsuite = TestSuite(title='Collection phase',
                                       description='This is the tests collection phase. Failures are modules that failed to collect.',
                                       tests=[],
                                       start=now())

    def pytest_collectreport(self, report):
        if not report.passed:
            name = self._get_report_kwarg(report)['name']
            self._start_case(name)
            if report.failed:
                case = self._stop_case(report, status=Status.BROKEN)
            else:
                case = self._stop_case(report, status=Status.SKIPPED)

            # FIXME: pytest does not have that much hooks for us to get exact collect moments
            case.start = case.stop = now()

            self.testsuite.tests.append(case)

    def pytest_collection_finish(self):
        """
        Writes Collection testsuite only if there were failures.
        """

        if self.testsuite.tests:
            self.finish_suite()
        else:
            self.testsuite = None

    def pytest_runtest_makereport(self, item, call, __multicall__):
        """
        That's the place we inject extra data into the report object from the actual Item.
        """

        report = __multicall__.execute()
        report.__dict__.update(
            start_time=call.start,
            stop_time=call.stop,
            desc=item.function.__doc__,
            exception=call.excinfo,
            result=self.config.hook.pytest_report_teststatus(report=report)[0])  # get the failed/passed/xpassed thingy
        return report

    def save_attach(self, body, attach_type=AttachmentType.TEXT):
        """
        Saves attachment to the report folder and returns file name

        :arg body: str or unicode with contents. str is written as-is in byte stream, unicode is written as utf-8 (what do you expect else?)
        """

        # FIXME: we should generate attachment name properly
        with self.attachfile("%s-attachment.%s" % (uuid.uuid4(), attach_type)) as f:
            if isinstance(body, unicode):
                f.write(body.encode('utf-8'))
            else:
                f.write(body)
            return os.path.basename(f.name)

    @contextmanager
    def attachfile(self, filename):
        """
        Yields open file object in the report directory with given name
        """
        reportpath = os.path.join(self.logdir, filename)

        with open(reportpath, 'wb') as f:
            yield f

    @contextmanager
    def reportfile(self, filename):
        """
        Yields open file object in the report directory with given name
        """
        reportpath = os.path.join(self.logdir, filename)
        encoding = 'utf-8'

        if py.std.sys.version_info[0] < 3:  # @UndefinedVariable
            logfile = py.std.codecs.open(reportpath, 'w', encoding=encoding)  # @UndefinedVariable
        else:
            logfile = open(reportpath, 'w', encoding=encoding)

        try:
            yield logfile
        finally:
            logfile.close()

    def write_suite(self, logfile, suite):
        logfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
        logfile.write(etree.tostring(suite.toxml(), pretty_print=True))
