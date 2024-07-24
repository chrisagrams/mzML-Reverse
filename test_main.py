from math import isclose
from main import simple_reverse, mass_reverse


def arrays_are_close(arr1, arr2, tol=1e-9):
    return all(isclose(a, b, abs_tol=tol) for a, b in zip(arr1, arr2))


def test_simple_reverse():
    test_array = [1000.0, 2000.0, 3000.0]
    expected_array = [3000.0, 2000.0, 1000.0]
    result = simple_reverse(test_array)
    assert arrays_are_close(expected_array, result)


def test_mass_reverse():
    test_array = [199.9, 1800.0, 2000.1]
    expected_array = [2000.1, 400.0, 199.9]
    result = mass_reverse(test_array)
    assert arrays_are_close(expected_array, result)