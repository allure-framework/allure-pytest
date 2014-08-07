# encoding: utf-8

'''
This module holds utils for the adaptor

Created on Oct 22, 2013

@author: pupssman
'''

import time
import hashlib
import inspect
from traceback import format_exception_only

from _pytest.python import Module

from allure.constants import Severity, Label
from allure.structure import TestLabel


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


def labels_of(item):
    """
    Returns list of TestLabel elements.
    """

    def get_marker_that_starts_with(item, name):
        """ get a list of marker object from item node that starts with given
        name or empty list if the node doesn't have a marker that starts with
        that name."""
        suitable_names = filter(lambda x: x.startswith(name), item.keywords.keys())

        markers = list()
        for name in suitable_names:
            markers.append(item.get_marker(name))

        return markers

    labels = LabelsList()
    label_markers = get_marker_that_starts_with(item, Label.DEFAULT)
    for label_marker in label_markers:
        label_name = label_marker.name.split('.', 1)[-1]
        for label_value in label_marker.args or ():
            labels.append(TestLabel(name=label_name, value=label_value))

    return labels


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
        return unicodify(format_exception_only(SyntaxError, e))


def get_exception_message(report):
    """
    get exception message from pytest's internal ``report`` object
    """
    return (getattr(report, 'exception', None) and present_exception(report.exception.value)) or (hasattr(report, 'result') and report.result) or report.outcome


class LabelsList(list):

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        other = other[:]
        for el in self:
            if el not in other:
                return False

            other.remove(el)

        return True

    def __add__(self, other):
        return self.__class__(super(LabelsList, self).__add__(other))

    def __and__(self, other):
        result = self.__class__()
        for el in self:
            if el in other and el not in result:
                result.append(el)

        return result

    def __str__(self):
        return ', '.join(map(str, [(el.name, el.value) for el in self]))
