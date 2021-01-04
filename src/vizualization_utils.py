import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import gensim
import jieba
import wordcloud
from pathlib import Path
BASE_DIR = Path(".").resolve().parents[0]
DIR = BASE_DIR.joinpath("src")

matplotlib.rc('font', family='Heiti TC') # enable to display chinese characters
co = matplotlib.cm.get_cmap('tab20')
male_color = matplotlib.colors.rgb2hex(co(0))
female_color = matplotlib.colors.rgb2hex(co.reversed()(0))

user_stop_words = set()
with open(DIR.joinpath("user_stopwords.txt"), 'r') as f:
    user_stop_words = set(f.read().splitlines())


def platform_overview_bar_chart(count_df):
    """
    :param count_df: pandas dataframe, platform as index, with two columns: "female_count" and "male_count"
    representing the number of records
    """
    # tODO: display text in bar?
    perc_count_df = count_df.apply(lambda x: x*100/sum(x), axis=1)
    title = "各招聘平台含性别优先字样的广告百分比"
    ax = perc_count_df.plot(
        kind='bar', stacked=True, ylabel="百分比", xlabel='',
        colormap='tab20',
    )
    plt.xticks(rotation=0)
    plt.legend(bbox_to_anchor=(1.05, 1), frameon=False, labels=['男性优先', '女性优先'])
    ax.set(frame_on=False)
    ax.set_title(title, pad=25)


def process_descrimination_contents(df, user_stop_words):
    """
    # param: df: pandas data frame, containing column "descrimination_content"
    # param: stop_words: set of customized stop words

    # return: [[str]] list of list of tokenized words
    """
    res = []
    for item in df['descrimination_content']:
        phrase = gensim.utils.tokenize(item)  # return a generator， remove number and special characters
        temp = []
        for p in phrase:
            words = jieba.lcut(p)
            temp.extend([w for w in words if len(w) > 1 and w not in user_stop_words])
        if temp:
            res.append(temp)
    return res


def generate_word_cloud(des_texts):
    """
    # param: des_texts: [str], list of words
    # return: a word cloud img
    """
    wc = wordcloud.WordCloud(font_path='./PingFang.ttc', collocations=False, background_color="white")
    wc.generate(' '.join(des_texts))
    plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


def process_jd_contents(df, user_stop_words):
    """
    # param: df: pandas data frame columns => "job_description"
    # param: stop_words: set of customized stop words

    # return: [str] list of list of tokenized words
    """
    res = []
    for item in df:
        phrase = gensim.utils.tokenize('.'.join(item)) # return a generator， remove number and special characters
        for p in phrase:
            words = jieba.lcut(p)
            temp = [w for w in words if len(w) > 1 and w not in user_stop_words]
        if temp:
            res.extend(temp)
    return res


def process_salary(f_df, m_df):
    """
    :param f_df: pandas dataframe, containing "salary_high", "salaray_low" two columns
    :param m_df: pandas dataframe
    """

    def _helper(df):
        return np.append(
            df[["salary_low", "salary_high"]].dropna().mean(axis=1).values,
            [df["salary_low"].min(), df["salary_high"].max()]
        )

    f_salary = pd.DataFrame(_helper(f_df), columns=["salary"])
    f_salary["gender"] = "女性"
    m_salary = pd.DataFrame(_helper(m_df), columns=["salary"])
    m_salary["gender"] = "男性"
    return f_salary.append(m_salary, ignore_index=True)


def salary_jitter_chart(salary_df):
    """
    create the jitter chart for salary column
    :param salary_df: generated by process_salary() method
    :return: None, generate a jitter chart
    """
    title = "不同性别工资范围"
    ax = sns.stripplot(x="gender", y="salary", data=salary_df, jitter=0.1, palette=[female_color, male_color])
    ax.set(frame_on=False, xlabel="", ylabel="工资（月薪）")
    ax.set_title(title, pad=25)


def process_job_title(jt_list):
    """
    :param jt_list: [str] for job title
    """
    job_title = []
    for title in jt_list:
        temp = [w for w in jieba.cut(title)
                if len(w)>1
                and not any(s.isdigit() for s in w)
                and w not in user_stop_words]
        job_title.extend(temp)
    return job_title

if __file__ == 'main':
    pass