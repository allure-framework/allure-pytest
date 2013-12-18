'''
This holds allure report xml structures

Created on Oct 23, 2013

@author: pupssman
'''

from allure.utils import xmlfied, Attribute, Element, Many, \
    Nested
from allure.constants import ALLURE_NAMESPACE


Attach = xmlfied('attachments', source=Attribute(),
                                title=Attribute(),
                                type=Attribute())


Failure = xmlfied('failure', fields=[
                                     ('message', Element()),
                                     ('trace', Element('stack-trace'))
                                     ])


TestCase = xmlfied('test-cases', fields=[
                                         ('title', Element()),
                                         ('description', Element().if_(lambda x: x)),
                                         ('failure', Nested().if_(lambda x: x)),
                                         ('steps', Many(Nested())),
                                         ('attachments', Many(Nested())),
                                         ],
                                 status=Attribute(),
                                 start=Attribute(),
                                 stop=Attribute(),
                                 severity=Attribute())


TestSuite = xmlfied('test-suite', namespace=ALLURE_NAMESPACE, fields=[
                                         ('title', Element()),
                                         ('description', Element().if_(lambda x: x)),
                                         ('tests', Many(Nested()))
                                         ],
                                 start=Attribute(),
                                 stop=Attribute())


TestStep = xmlfied('steps',
                   fields=[('title', Element()),
                           ('attachments', Many(Nested())),
                           ('steps', Many(Nested()))],
                   start=Attribute(),
                   stop=Attribute(),
                   status=Attribute())
