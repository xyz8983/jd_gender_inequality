import re
from datetime import datetime
import string
import jieba
import jieba.posseg as pseg
import numpy as np
import json 
import pandas as pd 

punctuation_list = '，。？！：；‘ “（）、'+ string.punctuation
ignore_word_list = ['女生', '男生', '女性', '男性', '优先', '考虑', '年龄', '女','男']
pos_tag_list = ['n', 'nr','nz','v','vd','vn','a','ad','an']


def find_age_exist(text):
    """
    @param text: string
    return None or age number in str
    """
    if "岁" in text:
        age_range = re.findall(r"(\d\d)", text)
        return ', '.join([str(age) for age in age_range if int(age) >=18])
    else:
        age_range = re.findall(r'\d\d后', text) # '95后', '90后', '85后'
        if age_range:
            try:
                high_age_range = datetime.now().year - min([int('19'+re.search(r"(\d\d)", age_text).group(0)) for age_text in age_rage])
                return str(high_age_range)
            except:
                return None
    return None
        
    
def find_age(text):
    """
    maybe not that necessary to know the exact age range, 
    boolean as mentioning age or not is useful enough
    @param text: string
    return 
        low_age_range: int, default None
        high_age_range: int, default None
    """
    if "岁" in text:
        age_range = re.findall(r"(\d\d)", text)
        if len(age_range)==1:
            low_age_range, high_age_range = age_range[0], None
        elif len(age_range)==2:
            low_age_range, high_age_range = age_range
        elif len(age_range) > 2:
            # may extract the bullet point number out
            low_age_range, high_age_range = age_range[-2:]
        else:
            low_age_range, high_age_range = None, None
    else:
        age_range = re.findall(r'(\d\d)后', text) # '95后', '90后', '85后'
        if age_range:
            try:
                high_age_range = datetime.now().year - min([int('19'+re.search(r"(\d\d)", age_text).group(0)) for age_text in age_rage])
                low_age_range = None
            except:
                low_age_range, high_age_range = None, None
        else:
            low_age_range, high_age_range = None, None
    return low_age_range, high_age_range

def find_outlooking(text):
    """
    @param text: string
    return: boolean
    """
    outlooking_words = ["五官", "端正", "形象", "样貌", "外貌", "帅", "美", "气质"]
    return any([p in text for p in outlooking_words])

def find_other_words(text):
    """
    find other discriminative words other than age, gender
    Args:
        text ([str]): discrimination text from JD

    Returns:
        [set[str]]: discriminative words
    """
    result = set()
    # extract other words
    # for w in jieba.cut(text):
    # # way one: not number, not punctuation(maybe utf-8), not 女生 男生 女性 男性 优先 考虑, not number.
    #     if w.strip() and not (w.isnumeric() or w in punctuation_list or w in ignore_word_list):
    #         if not re.search("\d", w):  #deal with case containing number bullet point, cant found by isnuemeric
    #             result.append(w.strip())
                
    # way two: maybe consider only getting noun and verb? n, nv
    for w, flag in pseg.cut(text):
        if (flag in pos_tag_list) and (w not in ignore_word_list): 
            result.add(w)
    return result

def process_discrimination_words(text):
    """ 
    ideally each pandas cell apply this function and add three more cells/columns to the same rw
    """

    age_dis = find_age_exist(text)
    outlooking_dis = find_outlooking(text)
    other_dis = find_other_words(text)
    
    
def liepin_company_size_clean(s):
    """
    s: string, company size field value, clean to get result like "5000-10000"
    return: tuple of integer (low, high), default is (0, 0) for missing value
    """
    m = re.match(r"(?P<size_low>\d+)-(?P<size_high>\d+)", s)
    if m and 'size_low' in m.groupdict() and 'size_high' in m.groupdict():
        return (int(m.groupdict()['size_low']), int(m.groupdict()['size_high']))
    # a tuple of None to enforce the to_list() later separate value into two columns
    # series.to_list() is not stable, cant guarantee to have split the value into two or more lists. if the first value is None, then it will only have one column

    return (0, 0) 

def extract_first_word(s: str)->str:
    """s: string representing words like company industry, keywords, often separated by different punctuations
        only return the first one
    """
    if s:
        return re.split(r'\W+', s)[0]    
    
def liepin_jd_process(file_path):
    """clean jd content from liepin
        steps include: clean salary, company size, only return first company industry, add platform as new column
    Args:
        file_path ([string]): json file path for the jd data crawled from liepin website

    Returns:
        [dataframe]: a processed pandas dataframe
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
        df_liepin = pd.DataFrame(data)
        # process salary to monthly salary in K RMB
        # salary from liepin, example: '30-35k·12薪', last 5 chars k·12薪 are not needed, and specail case: 面议
        # transform it into two columns: salary_low, salary_high
        df_liepin[['salary_low', 'salary_high']] = (df_liepin['salary_range']
                                                    .str.slice(stop=-5)
                                                    .str.split("-", expand=True)
                                                    .replace('', np.nan)
                                                    .astype(float)
                                                    .multiply(1000)
                                                    )
        df_liepin[['company_size_low', 'company_size_high']] = pd.DataFrame(df_liepin["company_size"].apply(liepin_company_size_clean).to_list(), index=df_liepin.index)
        df_liepin['company_industry'] = df_liepin['company_industry'].apply(extract_first_word)
        df_liepin['platform'] = 'liepin'
        
        return df_liepin
        

def company_size_clean(s):
    """
    general question, can be used for wuyi job, and zhuobo job
    s: string, company size field value, clean to get result like "5000-10000"
    return: tuple of integer (low, high), default is (0, 0) for missing value
    """
    if s:
        m = re.match(r"(?P<size_low>\d+)-(?P<size_high>\d+)", s)
        if m and 'size_low' in m.groupdict() and 'size_high' in m.groupdict():
            return (int(m.groupdict()['size_low']), int(m.groupdict()['size_high']))
        # a tuple of None to enforce the to_list() later separate value into two columns
        # series.to_list() is not stable, cant guarantee to have split the value into two or more lists. if the first value is None, then it will only have one column
        m = re.match(r"少于(?P<size_high>\d+)",s)
        if m and 'size_high' in m.groupdict():
            return (0, int(m.groupdict()['size_high']))
        m = re.match(r"(?P<size_low>\d+)人以上", s)
        if m and 'size_low' in m.groupdict():
            return (int(m.groupdict()['size_low']), 0)
        
    return (0, 0) 

def wuyi_salary_clean(s):
    """process salary column
    Args:
        s ([string]): salary string, can be none

    Returns:
        [(float, float)]: a tuple of low salary and high salary, in monthly unit
    """
    if not s:
        return (np.nan, np.nan)
    elif re.search(r'千/月',s):
        low, high = re.match(r'(\d+\.?\d*)-(\d+\.?\d*)',s).groups()
        return float(low)*1000, float(high)*1000
    elif re.search(r'万/月',s):
        low, high = re.match(r'(\d+\.?\d*)-(\d+\.?\d*)',s).groups()
        return float(low)*10000, float(high)*10000
    elif re.search(r'元/天',s):
        salary = re.match(r'(\d+\.?\d*)', s).group()
        return float(salary)*30, float(salary)*30
    else:
        return (np.nan, np.nan)

def wuyi_jd_process(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        df[['company_size_low', 'company_size_high']] = pd.DataFrame(df["company_size"].apply(company_size_clean).to_list(), index=df.index)
        df['company_industry'] = df['company_industry'].astype('str').apply(lambda x: re.search(r'\w+',x).group() if x else None)
        df['job_type'] = df['job_type'].astype('str').apply(lambda x: re.search(r'\w+',x).group() if x else None)
        df['keywords'] = df['keywords'].astype('str').apply(lambda x: re.search(r'\w+',x).group() if x and x!='[]' else None)
        df[['salary_low','salary_high']] = pd.DataFrame(df['salary_range'].apply(wuyi_salary_clean).tolist(), index=df.index)
        # missing date set as 0
        df['jd_publish_month'] = pd.to_datetime(df['jd_date'], format='%m-%d', errors='coerce').dt.month.fillna(0).astype(int)
        df['platform'] = 'wuyi'
        return df
    
def job_title_cleans(s):
    """clean job title
    remove '/': '商务跟单/助理' => '商务跟单'
    remove words in parathese: '采购（急聘！）' => '采购', '(女生优先)销售代表' => '销售代表'
    Args:
        s ([string]): job title string

    Returns:
        [string]: cleaned string, or None
    """
    if s:
        s = s.split('/')[0] # remove '/', '商务跟单/助理' => '商务跟单'
        p = r'(\w*)(?<!（|）)(\w*)' # '采购（急聘！）' => '采购'
        res = re.match(p, s)
        if res:
            return res.group()
        p = r'\(|\)|（|）'  # '(女生优先)销售代表' => '销售代表'
        return re.split(p, s)[-1]
    return None

def zhuobo_salary_clean(s):
    """clean salary column for zhuobo jd content

    Args:
        s ([string]): string contains salary, typically in `¥ num-num K` format

    Returns:
        [(float, float)]: salary range, low and high
    """
    if s:
        res = re.match(r'¥(\d+\.?\d*)-(\d+\.?\d*)K',s)
        low, high = res.groups() if res else (np.nan, np.nan)
        return float(low)*1000, float(high)*1000
    return (np.nan, np.nan)
    
def zhuobo_jd_process(file_path):
    """process jd content from zhuobo website
    Args:
        file_path ([string]): json file path for the content crawled from spider

    Returns:
        [pandas dataframe]: a processed pandas dataframe
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        df['company_industry'] = df['company_industry'].str.split('、').str[0]
        df['job_title'] = df['job_title'].apply(job_title_cleans)
        df['job_type'] = df['job_type'].astype('str').apply(lambda x: re.search(r'\w+',x).group() if x and x!='[]' else None)
        df['keywords'] = df['keywords'].astype('str').apply(lambda x: re.search(r'\w+',x).group() if x and x!='[]' else None)
        df[['salary_low','salary_high']] = pd.DataFrame(df['salary_range'].apply(zhuobo_salary_clean).tolist(), index=df.index)
        df['platform'] = 'zhuobo'
        
        return df