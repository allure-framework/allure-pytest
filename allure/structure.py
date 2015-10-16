'''
This holds allure report xml structures

Created on Oct 23, 2013

@author: pupssman
'''

from allure.rules import xmlfied, Attribute, Element, WrappedMany, Nested, Many
from allure.constants import ALLURE_NAMESPACE, COMMON_NAMESPACE


class Attach(xmlfied('attachment',
                     source=Attribute(),
                     title=Attribute(),
                     type=Attribute())):pass


class Failure(xmlfied('failure',
                      message=Element(),
                      trace=Element('stack-trace'))):pass


class TestCase(xmlfied('test-case',
                       name=Element(),
                       title=Element().if_(lambda x: x),
                       description=Element().if_(lambda x: x),
                       failure=Nested().if_(lambda x: x),
                       steps=WrappedMany(Nested()),
                       attachments=WrappedMany(Nested()),
                       labels=WrappedMany(Nested()),
                       status=Attribute(),
                       start=Attribute(),
                       stop=Attribute())):pass


class TestSuite(xmlfied('test-suite',
                        namespace=ALLURE_NAMESPACE,
                        name=Element(),
                        title=Element().if_(lambda x: x),
                        description=Element().if_(lambda x: x),
                        tests=WrappedMany(Nested(), name='test-cases'),
                        labels=WrappedMany(Nested()),
                        start=Attribute(),
                        stop=Attribute())):pass


class TestStep(xmlfied('step',
                       name=Element(),
                       title=Element().if_(lambda x: x),
                       attachments=WrappedMany(Nested()),
                       steps=WrappedMany(Nested()),
                       start=Attribute(),
                       stop=Attribute(),
                       status=Attribute())):pass


class TestLabel(xmlfied('label',
                        name=Attribute(),
                        value=Attribute())):pass


class EnvParameter(xmlfied('parameter',
                           name=Element(),
                           key=Element(),
                           value=Element())):pass


class Environment(xmlfied('environment',
                          namespace=COMMON_NAMESPACE,
                          id=Element(),
                          name=Element(),
                          parameters=Many(Nested()))):pass
