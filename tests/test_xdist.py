"""
Created on Oct 16, 2015

@author: pupssman
"""

import pickle
import pytest
import inspect

import allure.structure


@pytest.mark.parametrize('clzname', [name
                                     for (name, _) in inspect.getmembers(allure.structure, lambda c: hasattr(c, 'toxml'))])
def test_serializability(clzname):
    """
    Check that allure.structure stuff is properly picklable/unpicklable
    """

    clazz = getattr(allure.structure, clzname)

    assert clazz() == pickle.loads(pickle.dumps(clazz()))


def test_smoke(report_for):
    report_for("""
    import pytest
    def test():
        assert True
    """, extra_run_args=['-n', '2'])
