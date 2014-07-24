'''
This holds allure report xml structures

Created on Oct 23, 2013

@author: pupssman
'''

from allure.rules import xmlfied, Attribute, Element, Many, Nested
from allure.constants import ALLURE_NAMESPACE


Attach = xmlfied('attachment',
                 source=Attribute(),
                 title=Attribute(),
                 type=Attribute())


Failure = xmlfied('failure',
                  message=Element(),
                  trace=Element('stack-trace'))


TestCase = xmlfied('test-case',
                   name=Element(),
                   title=Element().if_(lambda x: x),
                   description=Element().if_(lambda x: x),
                   failure=Nested().if_(lambda x: x),
                   steps=Many(Nested()),
                   attachments=Many(Nested()),
                   labels=Many(Nested()),
                   status=Attribute(),
                   start=Attribute(),
                   stop=Attribute(),
                   severity=Attribute())


TestSuite = xmlfied('test-suite',
                    namespace=ALLURE_NAMESPACE,
                    name=Element(),
                    title=Element().if_(lambda x: x),
                    description=Element().if_(lambda x: x),
                    tests=Many(Nested(), name='test-cases'),
                    labels=Many(Nested()),
                    start=Attribute(),
                    stop=Attribute())


TestStep = xmlfied('step',
                   name=Element(),
                   title=Element().if_(lambda x: x),
                   attachments=Many(Nested()),
                   steps=Many(Nested()),
                   start=Attribute(),
                   stop=Attribute(),
                   status=Attribute())

TestLabel = xmlfied('label',
                    name=Attribute(),
                    value=Attribute())
