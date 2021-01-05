from scrapy import Spider, Request
from jd_spider.items import JDItem
import json
import os 

# step 1
class ZhuoBoJDUrlSpider(Spider):
    domain_url = "https://www.jobcn.com"
    start_urls = None # need to initialize in the child class
    def parse(self, response):
       """find the next url"""

       job_section_dom = response.css("div.job_view div.item_job")
       for job in job_section_dom:
           uri = job.css("h4.job_name a::attr(href)").get()
           url = self.domain_url+uri 
           yield {"url": url}                    
       # next page should be li with text "next page"
       # next page is in the start url list already, this website disable the content of pagination

# step 2
class ZhuoBoJDSpider(Spider):
    name = None
    gender_desc_keywords = None 
    gender = None 

    def parse(self, response):
        jd_item = JDItem()
        company_info_dom = response.css("div.nav_pos div.info div.base")
        company_name = company_info_dom.css("h2::text").get()
        company_industry = company_info_dom.xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '行业')]/following-sibling::dd/a/text()").get()
        company_size = company_info_dom.xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '规模')]/following-sibling::dd/text()").get()
        company_address = company_info_dom.xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '地址')]/following-sibling::dd/text()").get()

        job_content_dom = response.xpath("//div[@id='jobcnMainContent']")
        company_location = job_content_dom.css("div.attributes.clearfix").xpath("./dl[3]/dd/text()").get()
        job_title = job_content_dom.css("div.name_pos h2.name span::text").get()
        # TODO: salary has different units
        salary_range = job_content_dom.css("div.name_pos div.salary div.salary_body::text").get()
        age_requirement = job_content_dom.css("div.info_pos").xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '年龄要求')]/following-sibling::dd/text()").get()
        gender_requirement = job_content_dom.css("div.info_pos").xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '性别要求')]/following-sibling::dd/text()").get()
        jd_content = job_content_dom.css("div.desc_pos::text").extract()
        job_description = []
        descrimination_content = []
        for s in jd_content:
            if s.strip():
                job_description.append(s.strip())
            if any(phrase in s for phrase in self.gender_desc_keywords):
                descrimination_content.append(s.strip())      
        descrimination_content = ' '.join(descrimination_content).strip()
        if gender_requirement and ('不限' not in gender_requirement):
            descrimination_content += (' 性别要求: '+ gender_requirement)
            
        job_type = job_content_dom.css("div.tip_pos").xpath("./dl/dt[contains(text(), '职位类别')]/following-sibling::dd/a/text()").extract()
        keywords = job_content_dom.css("div.tip_pos").xpath("./dl/dt[contains(text(), '职位标签')]/following-sibling::dd/a/text()").extract()
        
        jd_item["url"] = response.url
        jd_item["company_name"] = company_name
        jd_item["company_industry"] = company_industry
        jd_item["company_size"] = company_size
        # no "company_type"
        jd_item["company_address"] = company_address
        if company_location:
            jd_item["province"] = company_location
            jd_item["city"] = company_location
            jd_item["district"] = company_location
        else:    
            try:
                # TODO: now assume first two is city, next two is district
                # TODO: use 现居住地 as source of city
                jd_item["province"] = company_address[:2]
                jd_item["city"] = company_address[2:4]
                jd_item["district"] = company_address[2:4]
            except:
                jd_item["province"] = ""
                jd_item["city"] = ""
                jd_item["district"] = ""        
          
        jd_item["job_title"] = job_title
        jd_item["job_type"] = job_type
        jd_item["job_description"] = job_description
        jd_item["descrimination_content"] = descrimination_content
        # TODO: first 2-3 keywords are enough
        jd_item["keywords"] = keywords
        jd_item["salary_range"] = salary_range  # contains ¥ 月薪
         # TODO: needs extra cleanning
        jd_item["age_requirement"] = age_requirement
        jd_item["gender_preference"] = self.gender
        # jd_date is none

        if descrimination_content:
            yield jd_item
        
        
class ZhuoBoJDUrlSpider_Male(ZhuoBoJDUrlSpider):
    name="zhuobo_jd_urls_male"
    # male first 男性优先  男生优先
    start_urls = [
        "https://www.jobcn.com/search/result.xhtml?s=search%2Findex&p.includeNeg=1&p.sortBy=default&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.keyword=%C4%D0%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P1",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Findex&p.includeNeg=1&p.sortBy=default&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.keyword=%C4%D0%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P2",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C4%D0%C9%FA%D3%C5%CF%C8&p.keywordType=2&p.workLocation="
    ]

class ZhuoBoJDUrlSpider_FemMale(ZhuoBoJDUrlSpider):
    name="zhuobo_jd_urls_female"
    # 女性优先 女生优先 139 position
    start_urls =[
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P1",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P2",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P3",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P4",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%C9%FA%D3%C5%CF%C8&p.keywordType=2&p.workLocation="
    ]

class ZhuoBoJDSpider_Male(ZhuoBoJDSpider):
    name = 'zhuobo_jd_spider_male'
    gender_desc_keywords = ['男生', '男性','优先', '限男', '男生，'] 
    gender = 'male' 
    start_urls = None
    def start_requests(self):
        """read zhuobo_urls_male.json file"""
        with open(os.path.dirname(os.path.abspath(__file__))+"/output/zhuobo_urls_male.json", "r") as f:
            data = json.load(f)
        try:
            for item in data:
                yield Request(url=item.get('url'), callback=self.parse)
        except:
            return  
class ZhuoBoJDSpider_Female(ZhuoBoJDSpider):
    name = 'zhuobo_jd_spider_female'
    gender = 'female' 
    start_urls = None
    gender_desc_keywords = ['女生', '女性','优先', '限女', '女生，']
    def start_requests(self):
        """read zhuobo_urls_female.json file"""
        with open(os.path.dirname(os.path.abspath(__file__))+"/output/zhuobo_urls_female.json", "r") as f:
            data = json.load(f)
        try:
            for item in data:
                yield Request(url=item.get('url'), callback=self.parse)
        except:
            return  