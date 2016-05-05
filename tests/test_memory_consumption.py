import gc
import resource

import pytest

ATTACH_SIZE_KB = 2 * 1024


TEST_BODY = '''
import allure
import pytest

@pytest.mark.parametrize('run', range({runs}))
def test_big_attach(run):
    allure.attach('large_data', 'X' * {attach} * 100)
'''


@pytest.fixture
def mem_usage(reports_for):
    """
    Function runs given `tests` via `reports_for` and returns memory consumption in Kilobytes.

    As `reports_for` runs in-process, measure this process consumption.
    """
    def mem_usage_impl(**tests):
        gc.collect()
        mem_before_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        reports_for(**tests)

        gc.collect()
        mem_after_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        return mem_after_kb - mem_before_kb

    return mem_usage_impl


def test_attach_memory_consumption(mem_usage):
    """
    Test for issue https://github.com/allure-framework/allure-python/issues/98

    Check that attachments do not consume too much memory of py.test process.

    Run lots of tests with big attachments and observe that memory usage rises well below total volume of all attachments.

    Each test modules generates at least `ATTACH_SIZE * 100` kilobytes of attachments, totalling to `ATTACH_SIZE * 200` kilobytes for two modules.

    Expect actual consumption increase to be withing `2 x ATTACH_SIZE`, comparing to one test run.
    """

    usage_one_test = mem_usage(test_a=TEST_BODY.format(attach=ATTACH_SIZE_KB, runs=1),
                               test_b=TEST_BODY.format(attach=ATTACH_SIZE_KB, runs=1))

    usage_lots_tests = mem_usage(test_a=TEST_BODY.format(attach=ATTACH_SIZE_KB, runs=100),
                                 test_b=TEST_BODY.format(attach=ATTACH_SIZE_KB, runs=100))

    assert usage_lots_tests - usage_one_test < ATTACH_SIZE_KB * 2
