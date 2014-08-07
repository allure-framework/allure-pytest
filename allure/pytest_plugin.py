import argparse
from collections import namedtuple

from _pytest.junitxml import mangle_testnames
import pytest

from allure.common import AllureImpl, StepContext
from allure.utils import LabelsList
from allure.constants import Status, AttachmentType, Severity, \
    FAILED_STATUSES, Label
from allure.utils import parent_module, parent_down_from_module, severity_of, \
    labels_of, all_of, get_exception_message
from allure.structure import TestLabel


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
            if entry not in severities:
                raise argparse.ArgumentTypeError('Illegal severity value [%s], only values from [%s] are allowed.' % (entry, ', '.join(severities)))

        return entries

    def features_label_type(string):
        return LabelsList([TestLabel(name=Label.FEATURE, value=x) for x in string.split(',')])

    def stories_label_type(string):
        return LabelsList([TestLabel(name=Label.STORY, value=x) for x in string.split(',')])

    parser.getgroup("general").addoption('--allure_severities',
                                         action="store",
                                         dest="allureseverities",
                                         metavar="SEVERITIES_LIST",
                                         default=None,
                                         type=severity_type,
                                         help="""Comma-separated list of severity names.
                                         Tests only with these severities will be run.
                                         Possible values are:%s.""" % ', '.join(severities))

    parser.getgroup("general").addoption('--allure_features',
                                         action="store",
                                         dest="allurefeatures",
                                         metavar="FEATURES_LIST",
                                         default=LabelsList(),
                                         type=features_label_type,
                                         help="""Comma-separated list of feature names.
                                         Run tests that have at least one of the specified feature labels.""")

    parser.getgroup("general").addoption('--allure_stories',
                                         action="store",
                                         dest="allurestories",
                                         metavar="STORIES_LIST",
                                         default=LabelsList(),
                                         type=stories_label_type,
                                         help="""Comma-separated list of story names.
                                         Run tests that have at least one of the specified story labels.""")


def pytest_configure(config):
    reportdir = config.option.allurereportdir
    if reportdir and not hasattr(config, 'slaveinput'):
        config._allurelistener = AllureTestListener(reportdir, config)
        config.pluginmanager.register(config._allurelistener)
        config.pluginmanager.register(AllureCollectionListener(reportdir))
        pytest.allure._allurelistener = config._allurelistener  # FIXME: maybe we need a different injection mechanism


def pytest_runtest_setup(item):
    severity = severity_of(item)
    item_labels = labels_of(item)

    option = item.config.option
    if option.allureseverities and severity not in \
            option.allureseverities:
        pytest.skip("Not running test of severity %s." % severity)

    arg_labels = option.allurefeatures + option.allurestories

    if arg_labels and not item_labels & arg_labels:
        pytest.skip('Not suitable with selected labels: %s.' % arg_labels)


class LazyInitStepContext(StepContext):
    """
    This is a step context used for decorated steps.
    It provides a possibility to create step decorators, being initiated before pytest_configure, when no AllureListener initiated yet.
    """
    def __init__(self, allure_helper, title):
        self.allure_helper = allure_helper
        self.title = title
        self.step = None

    @property
    def allure(self):
        return self.allure_helper.get_listener()


class AllureHelper(object):
    """
    This object holds various utility methods used from ``pytest.allure`` namespace, like ``pytest.allure.attach``
    """
    def __init__(self):
        self._allurelistener = None  # FIXME: this gets injected elsewhere, like in the pytest_configure

    def get_listener(self):
        return self._allurelistener

    def attach(self, name, contents, type=AttachmentType.TEXT):  # @ReservedAssignment
        """
        Attaches ``contents`` to a current context with given ``name`` and ``type``.
        """
        if self._allurelistener:
            self._allurelistener.attach(name, contents, type)

    def severity(self, level):
        """
        A decorator factory that returns ``pytest.mark`` for a given allure ``level``.
        """
        return pytest.mark.allure_severity(level)

    def label(self, name, *value):
        """
        A decorator factory that returns ``pytest.mark`` for a given label.
        """

        allure_label = getattr(pytest.mark, '%s.%s' %
                               (Label.DEFAULT, name.encode('utf-8', 'ignore')))
        return allure_label(*value)

    def feature(self, *features):
        """
        A decorator factory that returns ``pytest.mark`` for a given features.
        """
        return self.label(Label.FEATURE, *features)

    def story(self, *stories):
        """
        A decorator factory that returns ``pytest.mark`` for a given stories.
        """

        return self.label(Label.STORY, *stories)

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
          def make_test_data_bar():
              raise ValueError('No data today')

          def test_bar():
              assert make_test_data_bar()

          @pytest.allure.step
          def make_test_data_baz():
              raise ValueError('No data today')

          def test_baz():
              assert make_test_data_baz()

          @pytest.fixture()
          @pytest.allure.step('test fixture')
          def steppy_fixture():
              return 1

          def test_baz(steppy_fixture):
              assert steppy_fixture
        """
        if callable(title):
            return LazyInitStepContext(self, title.__name__)(title)
        else:
            return LazyInitStepContext(self, title)

    def single_step(self, text):
        """
        Writes single line to report.
        """
        if self._allurelistener:
            with self.step(text):
                pass

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

MASTER_HELPER = AllureHelper()


def pytest_namespace():
    return {'allure': MASTER_HELPER}


class AllureTestListener(object):
    """
    Listens to pytest hooks to generate reports for common tests.
    """
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
            skip_message = type(report.longrepr) == tuple and \
                report.longrepr[2] or report.wasxfail
            trim_msg_len = 89
            short_message = skip_message.split('\n')[0][:trim_msg_len]

            # FIXME: see pytest.runner.pytest_runtest_makereport
            self.impl.stop_case(status,
                                message=(short_message + '...' *
                                         (len(skip_message) > trim_msg_len)),
                                trace=None if short_message ==
                                skip_message else skip_message)
        else:
            self.impl.stop_case(status)

    def pytest_runtest_protocol(self, __multicall__, item, nextitem):
        if not self.testsuite:
            module = parent_module(item)
            self.impl.start_suite(name='.'.join(mangle_testnames(module.nodeid.split("::"))),
                                  description=module.module.__doc__ or None)
            self.testsuite = 'Yes'

        name = '.'.join(mangle_testnames([x.name for x in parent_down_from_module(item)]))
        self.impl.start_case(name, description=item.function.__doc__, severity=severity_of(item),
                             labels=labels_of(item))
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

    def pytest_runtest_makereport(self, item, call, __multicall__):  # @UnusedVariable
        """
        That's the place we inject extra data into the report object from the actual Item.
        """

        report = __multicall__.execute()
        report.__dict__.update(
            exception=call.excinfo,
            result=self.config.hook.pytest_report_teststatus(report=report)[0])  # get the failed/passed/xpassed thingy
        return report

    def pytest_sessionfinish(self):
        if self.testsuite:
            self.impl.stop_suite()
            self.testsuite = None


CollectFail = namedtuple('CollectFail', 'name status message trace')


class AllureCollectionListener(object):
    """
    Listens to pytest collection-related hooks
    to generate reports for modules that failed to collect.
    """
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
        Creates a testsuite with collection failures if there were any.
        """

        if self.fails:
            self.impl.start_suite(name='test_collection_phase',
                                  title='Collection phase',
                                  description='This is the tests collection phase. Failures are modules that failed to collect.')
            for fail in self.fails:
                self.impl.start_case(name=fail.name)
                self.impl.stop_case(status=fail.status, message=fail.message, trace=fail.trace)
            self.impl.stop_suite()
