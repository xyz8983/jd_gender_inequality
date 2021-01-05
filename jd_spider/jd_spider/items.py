# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field

class JDItem(scrapy.Item):
    url = Field() # str
    company_name = Field() # str
    company_type = Field() # str # nullable for example: 民营公司
    company_size = Field() # str # nullable, detailed address 
    company_industry = Field() # str # nullable example: 互联网/电子商务 批发/零售
    company_address = Field() # str
    city = Field() # str
    district = Field() # str # nullable
    province = Field() # str # nullable
    job_title = Field() # str 
    job_type = Field() #[str] # nullable for example: 职能类别
    job_description = Field() #[str]
    descrimination_content = Field() # str
    # TODO: first 2-3 keywords are enough
    keywords = Field() #[str]  # nullable, for example: 职位标签, 关键字 
    salary_range = Field() # str #nullable TODO: havent decided what it should look like
    gender_preference = Field() # str, an aggregation field
    age_requirement = Field() # str # nullable # TODO: needs extra cleanning
    jd_date = Field() # str, when the jd is published
    
    


class WuYiJDItem(scrapy.Item):
    url = Field() # str
    job_title = Field() # str
    job_description = Field() #[str]
    descrimination_content = Field() # str
    keywords = Field() #[str]  #todo: the first 2-3 is enough
    job_type = Field() #[str] 
    city = Field() # str
    district = Field() # str
    company_name = Field() # str
    company_type = Field() # str
    company_size = Field() # str
    salary_range = Field() # str


class ZhuoBoJDItem(JDItem):
    gender_requirement = Field() # str
    age_requirement = Field() # str
    province = Field() # str
    

    # company_type = Field() # here is actually company industry, is not neccessary => should abandon, it is different than that in WuyiJDItem

class LiePinJDItem(JDItem):
    
    # keywords = Field() #[str]  #todo: the first 2-3 is enough
    # job_type = Field() #[str] 
    # company_type = Field() # str
    company_industry = Field() # str