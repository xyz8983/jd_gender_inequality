# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field

# TODO: only one class representing all
class JDItem(scrapy.Item):
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
    company_address = Field() # str
    salary_range = Field() # str


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