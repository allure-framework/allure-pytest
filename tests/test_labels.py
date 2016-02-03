"""
Test for labels markings in allure

Created on Jun 5, 2014

@author: F1ashhimself
"""
from __future__ import absolute_import

import pytest
from .matchers import has_label
from hamcrest import assert_that, equal_to, is_not, has_property, has_properties, has_item, anything, all_of, any_of

from allure.constants import Label
from allure.utils import thread_tag, host_tag


def has_failure(test_name, message=anything()):
    return has_property('{}test-cases',
                        has_property('test-case',
                                     has_item(
                                         has_properties({'name': equal_to(test_name),
                                                         'failure': any_of(
                                                             has_property('stack-trace', equal_to(message)),
                                                             has_property('message', equal_to(message)))}))))


def test_labels(report_for):
    """
    Checks that label markers for tests are shown in report.
    """
    report = report_for("""
    import allure

    @allure.label('label_name1', 'label_value1')
    class TestMy:

        @allure.label('label_name2', 'label_value2')
        def test_a(self):
            pass
    """)

    assert_that(report, all_of(
        has_label('TestMy.test_a', 'label_name1', 'label_value1'),
        has_label('TestMy.test_a', 'label_name2', 'label_value2')))


def test_labels_inheritance(report_for):
    """
    Checks that label markers can be inherited.
    """
    report = report_for("""
    import allure

    pytestmark = allure.label('label_name1', 'label_value1')

    @allure.label('label_name2', 'label_value2')
    class TestMy:

        @allure.label('label_name3', 'label_value3')
        @allure.label('label_name4', 'label_value4')
        def test_a(self):
            pass

        def test_b(self):
            pass
    """)

    assert_that(report, all_of(
        has_label('TestMy.test_a', 'label_name1', 'label_value1'),
        has_label('TestMy.test_a', 'label_name2', 'label_value2'),
        has_label('TestMy.test_a', 'label_name3', 'label_value3'),
        has_label('TestMy.test_a', 'label_name4', 'label_value4'),
        has_label('TestMy.test_a', 'label_name1', 'label_value1'),
        has_label('TestMy.test_a', 'label_name2', 'label_value2')))


def test_feature_and_stories(report_for):
    """
    Checks that feature and stories markers for tests are shown in report.
    """
    report = report_for("""
    import allure

    @allure.feature('Feature1')
    class TestMy:

        @allure.story('Story1')
        def test_a(self):
            pass
    """)

    assert_that(report, all_of(
        has_label('TestMy.test_a', 'feature', 'Feature1'),
        has_label('TestMy.test_a', 'story', 'Story1')))


def test_feature_and_stories_inheritance(report_for):
    """
    Checks that feature and stories markers can be inherited.
    """
    report = report_for("""
    import allure

    pytestmark = allure.feature('Feature1')

    @allure.feature('Feature2')
    class TestMy:

        @allure.story('Story1')
        def test_a(self):
            pass

        def test_b(self):
            pass
    """)

    assert_that(report, all_of(
        has_label('TestMy.test_a', 'feature', 'Feature1'),
        has_label('TestMy.test_a', 'feature', 'Feature2'),
        has_label('TestMy.test_a', 'story', 'Story1'),
        has_label('TestMy.test_a', 'feature', 'Feature1'),
        has_label('TestMy.test_a', 'feature', 'Feature2')))


def test_multiple_features_and_stories(report_for):
    """
    Checks that we can handle multiple feature and stories markers.
    """
    report = report_for("""
    import allure

    @allure.feature('Feature1', 'Feature2')
    @allure.feature('Feature3')
    def test_a():
        pass

    @allure.story('Story1', 'Story2')
    @allure.story('Story3')
    def test_b():
        pass
    """)

    assert_that(report, all_of(
        has_label('test_a', 'feature', 'Feature1'),
        has_label('test_a', 'feature', 'Feature2'),
        has_label('test_a', 'feature', 'Feature3'),
        has_label('test_b', 'story', 'Story1'),
        has_label('test_b', 'story', 'Story2'),
        has_label('test_b', 'story', 'Story3')))


@pytest.mark.parametrize('features, stories, expected_failure',
                         [(None, None, (False, False, False)),
                          ('Feature1', 'Story1,Story2', (False, False, True)),
                          (None, 'Story1', (False, False, True)),
                          ('Feature2', None, (True, False, True))])
def test_specified_feature_and_story(report_for, features, stories, expected_failure):
    """
    Checks that tests with specified Feature or Story marks will be run.
    """

    extra_run_args = list()
    if features:
        extra_run_args.extend(['--allure_features', features])
    if stories:
        extra_run_args.extend(['--allure_stories', stories])

    report = report_for("""
    import allure

    @allure.feature('Feature1')
    @allure.story('Story1', 'Story2')
    def test_a():
        pass

    @allure.feature('Feature1')
    @allure.feature('Feature2')
    @allure.story('Story1')
    def test_b():
        pass

    def test_c():
        pass
    """, extra_run_args=extra_run_args)

    for test_num, test_name in enumerate(['test_a', 'test_b', 'test_c']):
        if expected_failure[test_num]:
            # Dynamically collecting skip message.
            skipped_message = ["('feature', '%s')" % feature.strip() for feature in (features.split(',') if features else ())]
            skipped_message.extend(["('story', '%s')" % story.strip() for story in (stories.split(',') if stories else ())])
            skipped_message = 'Skipped: Not suitable with selected labels: %s.' % ', '.join(skipped_message)

            assert_that(report, has_failure(test_name, skipped_message))
        else:
            assert_that(report, is_not(has_failure(test_name)))


def test_issues(report_for):
    """
    Checks that issues markers for tests are shown in report.
    """
    report = report_for("""
    import allure

    @allure.issue('Issue1')
    def test_a():
        allure.dynamic_issue('Issue11', 'Issue12')
        pass

    @allure.issue('Issue2')
    class TestMy:

        @allure.issue('Issue3')
        def test_b(self):
            allure.dynamic_issue('Issue31', 'Issue32')
            pass

        def test_c(self):
            pass
    """)

    assert_that(report, all_of(
        has_label('test_a', 'issue', 'Issue1'),
        has_label('test_a', 'issue', 'Issue11'),
        has_label('test_a', 'issue', 'Issue12'),
        has_label('TestMy.test_b', 'issue', 'Issue2'),
        has_label('TestMy.test_b', 'issue', 'Issue3'),
        has_label('TestMy.test_b', 'issue', 'Issue31'),
        has_label('TestMy.test_b', 'issue', 'Issue32'),
        has_label('TestMy.test_c', 'issue', 'Issue2')
        ))


def test_testcases(report_for):
    """
    Checks that issues markers for tests are shown in report.
    """
    report = report_for("""
    import allure

    @allure.testcase('http://my.bugtracker.com/TESTCASE-1')
    def test_a():
        pass

    @allure.testcase('http://my.bugtracker.com/TESTCASE-2')
    class TestMy:

        @allure.testcase('http://my.bugtracker.com/TESTCASE-3')
        def test_b(self):
            pass

        def test_c(self):
            pass
    """)

    assert_that(report, all_of(
        has_label('test_a', 'testId', 'http://my.bugtracker.com/TESTCASE-1'),
        has_label('TestMy.test_b', 'testId', 'http://my.bugtracker.com/TESTCASE-2'),
        has_label('TestMy.test_b', 'testId', 'http://my.bugtracker.com/TESTCASE-3'),
        has_label('TestMy.test_c', 'testId', 'http://my.bugtracker.com/TESTCASE-2')))


# only run local reports -- this test makes no sense for xdisted ones
# see `reports_for` docstring
@pytest.mark.parametrize('reports_for', ['local'], indirect=True)
def test_environ_labels(report_for):
    report = report_for("""
    import pytest

    def test_foo():
        pass
    """)

    assert_that(report, all_of(
        has_label('test_foo', label_value=thread_tag(), label_name=Label.THREAD),
        has_label('test_foo', label_value=host_tag(), label_name=Label.HOST)
    ))
