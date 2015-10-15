"""
Created on Oct 16, 2015

@author: pupssman
"""


def test_smoke(report_for):
    report_for("""
    import pytest
    def test():
        assert True
    """, extra_run_args=['-n', '2'])
