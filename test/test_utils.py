import pytest
from jd_gender_inequality.src.analysis_utils import (  
    find_age, 
    find_outlooking,
    company_size_clean,
    zhuobo_salary_clean,
    job_title_cleans
)
import numpy as np

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
    

@pytest.mark.parametrize(
    ["s", "exp_res"],
    [
        ('少于50人', (0, 50)),
        ('10000人以上', (10000, 0)),
        (None, (0, 0) ),
        ('50-150人', (50, 150))
    ]
)
def test_wuyi_company_size_clean(s, exp_res):
    processed_s = company_size_clean(s)
    assert processed_s==exp_res, f'expcted result is {exp_res}, but get {processed_s}'
    
    
@pytest.mark.parametrize(
    ["s", "exp_res"],
    [
        ('¥4.5-6K', (4500, 6000)),
        ('', (np.nan, np.nan))
    ]
)    
def test_zhuobo_salary_clean(s, exp_res):
    processed_s = zhuobo_salary_clean(s)
    assert processed_s == exp_res, f'expcted result is {exp_res}, but get {processed_s}'