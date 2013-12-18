# encoding: utf-8

'''
This module holds utils for the adaptor

Created on Oct 22, 2013

@author: pupssman
'''
from collections import namedtuple
from lxml import objectify
from _pytest.python import Module
from allure.contrib.recordtype import recordtype
import hashlib
import time
from allure.constants import Severity
import inspect


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
# limited to first 128 chars
VALID_ASCII = map(chr, [0x09, 0x0A, 0x0D] + range(0x20, 0x7F))
MAGIC = u'�'


class Element(Rule):
    def __init__(self, name='', namespace=''):
        self.name = name
        self.namespace = namespace

    def value(self, name, what):
        if not isinstance(what, basestring):
            return self.value(name, str(what))

        if not isinstance(what, unicode):
            what = ''.join(x if x in VALID_ASCII else MAGIC for x in what)

        return element_maker(self.name or name, self.namespace)(what)


class Attribute(Rule):
    def value(self, name, what):
        return str(what)


class Nested(Rule):
    def value(self, name, what):
        return what.toxml()


class Many(Rule, namedtuple('Many', 'rule')):
    def value(self, name, what):
        return [self.rule.value(name, x) for x in what]


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
