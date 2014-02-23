"""
Created on Feb 23, 2014

@author: pupssman
"""
import os
import py
import uuid

from lxml import etree
from contextlib import contextmanager

from allure.utils import now
from allure.constants import AttachmentType, Severity
from allure.structure import Attach, TestStep, TestCase, TestSuite


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
        attach = Attach(source=self._save_attach(contents, attach_type=attach_type),
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

    def start_case(self, name, description=None, severity=Severity.NORMAL):
        """
        Starts a new :py:class:`allure.structure.TestCase` and pushes it to the ``self.stack``
        """
        test = TestCase(name=name,
                        description=description,
                        severity=severity,
                        start=now(),
                        attachments=[],
                        steps=[])
        self.stack.append(test)

    def stop_case(self, status, failure=None):
        """
        Finalizes with important data the test at the top of ``self.stack`` and returns it
        """
        test = self.stack[-1]
        test.status = status
        test.stop = now()

        if failure:
            test.failure = failure

        self.testsuite.tests.append(test)

        return test

    def start_suite(self, name, description=None):
        """
        Starts a new Suite with given ``name`` and ``description``
        """
        self.testsuite = TestSuite(name=name,
                                   description=description,
                                   tests=[],
                                   start=now())

    def stop_suite(self):
        """
        Writes currently active testuite and prepares for the next one blanking ``self.testsuite``
        """
        self.testsuite.stop = now()

        with self._reportfile('%s-testsuite.xml' % uuid.uuid4()) as f:
            self._write_suite(f, self.testsuite)

        self.testsuite = None

    def _save_attach(self, body, attach_type=AttachmentType.TEXT):
        """
        Saves attachment to the report folder and returns file name

        :arg body: str or unicode with contents. str is written as-is in byte stream, unicode is written as utf-8 (what do you expect else?)
        """

        # FIXME: we should generate attachment name properly
        with self._attachfile("%s-attachment.%s" % (uuid.uuid4(), attach_type)) as f:
            if isinstance(body, unicode):
                f.write(body.encode('utf-8'))
            else:
                f.write(body)
            return os.path.basename(f.name)

    @contextmanager
    def _attachfile(self, filename):
        """
        Yields open file object in the report directory with given name
        """
        reportpath = os.path.join(self.logdir, filename)

        with open(reportpath, 'wb') as f:
            yield f

    @contextmanager
    def _reportfile(self, filename):
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

    def _write_suite(self, logfile, suite):
        logfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
        logfile.write(etree.tostring(suite.toxml(), pretty_print=True))
