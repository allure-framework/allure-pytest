# encoding: utf-8

'''
This module holds utils for the adaptor

Created on Oct 22, 2013

@author: pupssman
'''

import re
import sys
import time
import hashlib
import inspect

from lxml import objectify
from traceback import format_exception_only

from _pytest.python import Module

from allure.contrib.recordtype import recordtype
from allure.constants import Severity


def element_maker(name, namespace):
    return getattr(objectify.ElementMaker(annotate=False, namespace=namespace,), name)


class Rule:
    _check = None

    def value(self, name, what):
        raise NotImplemented()

    def if_(self, check):
        self._check = check
        return self

    def check(self, what):
        if self._check:
            return self._check(what)
        else:
            return True


# see http://en.wikipedia.org/wiki/Valid_characters_in_XML#Non-restricted_characters

# We need to get the subset of the invalid unicode ranges according to
# XML 1.0 which are valid in this python build.  Hence we calculate
# this dynamically instead of hardcoding it.  The spec range of valid
# chars is: Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD]
#                    | [#x10000-#x10FFFF]
_legal_chars = (0x09, 0x0A, 0x0d)
_legal_ranges = (
    (0x20, 0x7E),
    (0x80, 0xD7FF),
    (0xE000, 0xFFFD),
    (0x10000, 0x10FFFF),
)
_legal_xml_re = [unicode("%s-%s") % (unichr(low), unichr(high)) for (low, high) in _legal_ranges if low < sys.maxunicode]
_legal_xml_re = [unichr(x) for x in _legal_chars] + _legal_xml_re
illegal_xml_re = re.compile(unicode('[^%s]') % unicode('').join(_legal_xml_re))


def legalize_xml(arg):
    def repl(matchobj):
        i = ord(matchobj.group())
        if i <= 0xFF:
            return unicode('#x%02X') % i
        else:
            return unicode('#x%04X') % i
    return illegal_xml_re.sub(repl, arg)


class Element(Rule):
    def __init__(self, name='', namespace=''):
        self.name = name
        self.namespace = namespace

    def value(self, name, what):
        if not isinstance(what, basestring):
            return self.value(name, str(what))

        if not isinstance(what, unicode):
            try:
                what = unicode(what, 'utf-8')
            except UnicodeDecodeError:
                what = unicode(what, 'utf-8', errors='replace')

        return element_maker(self.name or name, self.namespace)(legalize_xml(what))


class Attribute(Rule):
    def value(self, name, what):
        return str(what)


class Nested(Rule):
    def value(self, name, what):
        return what.toxml()


class Many(Rule):
    def __init__(self, rule, name='', namespace=''):
        self.rule = rule
        self.name = name
        self.namespace = namespace

    def value(self, name, what):
        el = element_maker(self.name or name, self.namespace)

        return el(*[self.rule.value(name, x) for x in what])


def xmlfied(el_name, namespace='', fields=[], **kw):
    items = fields + kw.items()

    class MyImpl(recordtype('XMLFied', [(item[0], None) for item in items])):
        def toxml(self):
            el = element_maker(el_name, namespace)
            entries = lambda clazz: [(name, rule.value(name, getattr(self, name))) for (name, rule) in items if isinstance(rule, clazz) and rule.check(getattr(self, name))]

            elements = entries(Element)
            attributes = entries(Attribute)
            nested = entries(Nested)
            manys = sum([[(m[0], v) for v in m[1]] for m in entries(Many)], [])

            return el(*([element for (_, element) in elements + nested + manys]),
                      **{name: attr for (name, attr) in attributes})

    return MyImpl


def parents_of(item):
    """
    Returns list of parents (i.e. object.parent values) starting from the top one (Session)
    """
    parents = [item]
    current = item

    while current.parent is not None:
        parents.append(current.parent)
        current = current.parent

    return parents[::-1]


def parent_module(item):
    return filter(lambda x: isinstance(x, Module), parents_of(item))[0]


def parent_down_from_module(item):
    parents = parents_of(item)
    return parents[parents.index(parent_module(item)) + 1:]


def sec2ms(sec):
    return int(round(sec * 1000.0))


def uid(name):
    """
    Generates fancy UID uniquely for ``name`` by the means of hash function
    """
    return hashlib.sha256(name).hexdigest()


def now():
    """
    Return current time in the allure-way representation. No further conversion required.
    """
    return sec2ms(time.time())


def severity_of(item):
    severity_marker = item.get_marker('allure_severity')
    if severity_marker:
        return severity_marker.args[0]
    else:
        return Severity.NORMAL


def all_of(enum):
    """
    returns list of name-value pairs for ``enum`` from :py:mod:`allure.constants`
    """
    return filter(lambda (n, v): not n.startswith('_'), inspect.getmembers(enum))


def unicodify(something):
    def convert(x):
        try:
            return unicode(x)
        except UnicodeDecodeError:
            return unicode(x, 'utf-8', errors='replace')

    try:
        return convert(something)  # @UndefinedVariable
    except TypeError:
        try:
            return convert(str(something))  # @UndefinedVariable
        except UnicodeEncodeError:
            return convert('<nonpresentable %s>' % type(something))  # @UndefinedVariable


def present_exception(e):
    """
    Try our best at presenting the exception in a readable form
    """
    if not isinstance(e, SyntaxError):
        return unicodify('%s: %s' % (type(e).__name__, unicodify(e)))
    else:
        return unicodify(format_exception_only(e))


def get_exception_message(report):
    """
    get exception message from pytest's internal ``report`` object
    """
    return (getattr(report, 'exception', None) and present_exception(report.exception.value)) or (hasattr(report, 'result') and report.result) or report.outcome
