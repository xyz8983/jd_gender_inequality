import re
from datetime import datetime
import string
import jieba
import jieba.posseg as pseg

punctuation_list = '，。？！：；‘ “（）、'+ string.punctuation
ignore_word_list = ['女生', '男生', '女性', '男性', '优先', '考虑', '年龄', '女','男']
pos_tag_list = ['n', 'nr','nz','v','vd','vn','a','ad','an']


def find_age_exist(text):
    """
    @param text: string
    return None or age number in str
    """
    if "岁" in text:
        age_range = re.findall("(\d\d)", text)
        return ', '.join([str(age) for age in age_range if int(age) >=18])
    else:
        age_range = re.findall('\d\d后', text) # '95后', '90后', '85后'
        if age_range:
            try:
                high_age_range = datetime.now().year - min([int('19'+re.search("(\d\d)", age_text).group(0)) for age_text in age_rage])
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
        age_range = re.findall("(\d\d)", text)
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
        age_range = re.findall('(\d\d)后', text) # '95后', '90后', '85后'
        if age_range:
            try:
                high_age_range = datetime.now().year - min([int('19'+re.search("(\d\d)", age_text).group(0)) for age_text in age_rage])
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