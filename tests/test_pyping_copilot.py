import pytest

from pypeduct import pyped


@pytest.mark.parametrize(
    "input_value, func, expected",
    [
        (5, lambda x: x + 2, 7),
        (True, lambda x: not x, False),
        (None, lambda x: x is None, True),
        ("hello", lambda x: x.upper(), "HELLO"),
    ],
)
def test_basic_pipeline(input_value, func, expected):
    @pyped
    def pipeline():
        result = input_value >> func
        return result

    assert pipeline() == expected


@pytest.mark.parametrize(
    "exception, func",
    [
        (TypeError, lambda x: x + "a"),  # Causes TypeError
        (ValueError, lambda x: int("a")),  # Causes ValueError
    ],
)
def test_exception_handling_in_pipeline(exception, func):
    @pyped
    def pipeline():
        5 >> func

    with pytest.raises(exception):
        pipeline()


@pytest.mark.parametrize(
    "input_value, func, expected",
    [
        (5, lambda x: x * 2, 10),
        (-3, lambda x: abs(x), 3),
        (True, lambda x: not x, False),
        ("hello", lambda x: x.upper(), "HELLO"),
        (None, lambda x: x is None, True),
    ],
)
def test_basic_pipeline_operations(input_value, func, expected):
    @pyped
    def pipeline():
        return input_value >> func

    assert pipeline() == expected


@pytest.mark.parametrize(
    "input_value, func, expected_exception",
    [
        (5, lambda x: x + "a", TypeError),
        (".", lambda x: int(x), ValueError),
        ([1, 2, 3], lambda x: x[5], IndexError),
        ({"a": 1}, lambda x: x["b"], KeyError),
    ],
)
def test_pipeline_exception_handling(input_value, func, expected_exception):
    @pyped
    def pipeline():
        return input_value >> func

    with pytest.raises(expected_exception):
        pipeline()
