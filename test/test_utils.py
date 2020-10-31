import pytest
from ..src.analysis_utils import find_age, find_outlooking

@pytest.mark.parametrize(
    ["text","ex_result"],
    [
        ("18-40周岁（女生可放宽到44岁）", (18,40)),
        ("年龄22-30岁", (22, 30)),
        ("28岁以上", (28, None)),
        ("95后", (None, 25)),
        ("50岁以下",(None, 50)) # this one will faile
    ]
)
def test_find_age(text, ex_result):
    """not pass the test yet, the find_age function needs some tweaks"""
    result = find_age(text)
    assert result == ex_result, f"return {result} but expecte {ex_result}"
    
    
def test_find_outlooking():
    pass