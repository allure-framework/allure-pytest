"""
Created on Feb 23, 2014

@author: pupssman
"""
from contextlib import contextmanager
from allure.constants import AttachmentType, Status, Severity
import os


class AllureImpl(object):

    def __init__(self, logdir):
        self.logdir = os.path.normpath(os.path.abspath(os.path.expanduser(os.path.expandvars(logdir))))

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

    def start_step(self, name):
        """
        Starts an new :py:class:`allure.structure.TestStep` with given title,
        pushes it to the ``self.stack`` and returns the step.
        """
        step = TestStep(name=name,
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
            'exceptionMessage': (getattr(report, 'exception', None) and present_exception(report.exception.value)) or (hasattr(report, 'result') and report.result) or report.outcome
        }

    def _start_case(self, name, severity=Severity.NORMAL):
        """
        Starts a new :py:class:`allure.structure.TestCase` and pushes it to the ``self.stack``
        """
        test = TestCase(name=name,
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
                                   trace=report.longrepr or report.wasxfail)
        elif kw['status'] == Status.SKIPPED:
            test.failure = Failure(message='skipped',
                                   trace=type(report.longrepr) == tuple and report.longrepr[2] or report.wasxfail)  # FIXME: see pytest.runner.pytest_runtest_makereport

        return test

    def finish_suite(self):
        """
        Writes currently active testuite and prepares the Adaptor for the next one blanking ``self.testsuite``
        """
        self.testsuite.stop = now()

        with self.reportfile('%s-testsuite.xml' % uuid.uuid4()) as f:
            self.write_suite(f, self.testsuite)

        self.testsuite = None

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

