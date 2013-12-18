'''
Holds some long-running (in milliseconds) test to demo the time chart a bit
'''

import time
import pytest


def test_50():
    time.sleep(0.05)


@pytest.mark.parametrize('run', range(10))
def test_10(run):
    time.sleep(0.01)
