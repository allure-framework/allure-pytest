# encoding: utf-8

"""
Test for xml object convertion

Created on Oct 22, 2013

@author: pupssman
"""
from lxml import etree


from allure.rules import Attribute, xmlfied, Element, Nested, WrappedMany
from hamcrest.core.assert_that import assert_that
from hamcrest.library.text.stringcontainsinorder import string_contains_in_order
from hamcrest.core.core.allof import all_of


def get_xml_string(doc):
    return etree.tostring(doc).decode('utf-8')


def test_element():
    ElementTest = xmlfied('element_test', ab=Element())

    a = ElementTest(ab='foo')
    assert_that(get_xml_string(a.toxml()), string_contains_in_order('<element_test>',
                                                                    '<ab>foo</ab>',
                                                                    '</element_test>'))


def test_attribute():
    AttrTest = xmlfied('attr_test', foo=Attribute())

    a = AttrTest(foo='bar')

    assert_that(get_xml_string(a.toxml()), string_contains_in_order('<attr_test', 'foo=', '"bar"', ">"))


def test_nested():
    Top = xmlfied('top', foo=Nested())
    Down = xmlfied('down', bar=Element(), baz=Attribute())

    d = Down(bar='123', baz='456')
    t = Top(foo=d)

    assert_that(get_xml_string(t.toxml()), string_contains_in_order(
        '<top>',
        '<down',
        'baz=', '"456"',
        '<bar>',
        '123',
        '</bar>',
        '</down>',
        '</top>'
    ))


def test_many_elements():
    Box = xmlfied('box', foos=WrappedMany(Element(name='foo')))

    box = Box(foos=['a', 'b', 'c'])

    assert_that(get_xml_string(box.toxml()), all_of(
        string_contains_in_order('<box>', '<foos>', '<foo>', 'a', '</foo>', '</foos>', '</box>'),
        string_contains_in_order('<box>', '<foos>', '<foo>', 'b', '</foo>', '</foos>', '</box>'),
        string_contains_in_order('<box>', '<foos>', '<foo>', 'c', '</foo>', '</foos>', '</box>')
    ))


def test_many_nested():
    Item = xmlfied('item', value=Element())
    Box = xmlfied('box', items=WrappedMany(Nested()))

    box = Box(items=[])
    box.items.append(Item('a'))
    box.items.append(Item('a'))
    box.items.append(Item('a'))

    assert_that(get_xml_string(box.toxml()), all_of(
        string_contains_in_order('<box>',
                                 '<items>',
                                 '<item>', 'a', '</item>',
                                 '<item>', 'a', '</item>',
                                 '<item>', 'a', '</item>',
                                 '</items>',
                                 '</box>'),
    ))


def test_elements_order():
    Foo = xmlfied('foo', fields=[
        ('bar', Element()),
        ('baz', Element()),
        ('gaz', Element()),
        ('daz', Element())])

    foo = Foo(bar=3, baz=4, gaz=5, daz=6)

    assert_that(get_xml_string(foo.toxml()), string_contains_in_order(
        '<bar>', '3', '</bar>',
        '<baz>', '4', '</baz>',
        '<gaz>', '5', '</gaz>',
        '<daz>', '6', '</daz>'
    ))


def test_optional():
    foo = xmlfied('foo', bar=Element().if_(lambda x: '123' not in x))

    assert_that(get_xml_string(foo(bar=' 123 ').toxml()), string_contains_in_order('<foo/>'))
    assert_that(get_xml_string(foo(bar=' 12 3').toxml()), string_contains_in_order('<foo>', '<bar>'))


def test_element_name():
    foo = xmlfied('foo', bar=Element(name='foo-bar'))

    assert_that(get_xml_string(foo(bar='123').toxml()), string_contains_in_order('<foo>', '<foo-bar>', '123', '</foo-bar>', '</foo>'))


def test_bad_symbols_replacement():
    foo = xmlfied('foo', bar=Element(name='bar'))

    assert_that(get_xml_string(foo(bar=u'abОЛОЛОcd'.encode('cp1251')).toxml()), string_contains_in_order('<bar>', 'ab', '&#65533;' * 4, 'cd', '</bar>'))


def test_illegal_xml_symbols():
    foo = xmlfied('foo', bar=Element(name='bar'))

    foo(bar=''.join(map(chr, range(128)))).toxml()
