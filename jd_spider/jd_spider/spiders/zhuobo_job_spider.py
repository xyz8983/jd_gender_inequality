from scrapy import Spider, Request
from jd_spider.items import ZhuoBoJDItem
import json

# step 1
class ZhuoBoJDUrlSpider(Spider):
    name="step_one_zhuobo_jd_urls"
    # male first 男性优先  男生优先
    # start_urls = [
    #     "https://www.jobcn.com/search/result.xhtml?s=search%2Findex&p.includeNeg=1&p.sortBy=default&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.keyword=%C4%D0%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P1",
    #     "https://www.jobcn.com/search/result.xhtml?s=search%2Findex&p.includeNeg=1&p.sortBy=default&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.keyword=%C4%D0%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P2",
    #     "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C4%D0%C9%FA%D3%C5%CF%C8&p.keywordType=2&p.workLocation="
    # ]

    # 女性优先 女生优先 139 position
    start_urls =[
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P1",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P2",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P3",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%D0%D4%D3%C5%CF%C8&p.keywordType=2&p.workLocation=#P4",
        "https://www.jobcn.com/search/result.xhtml?s=search%2Ftop&p.includeNeg=1&p.sortBy=postdate&p.jobLocationId=&p.jobLocationTown=&p.jobLocationTownId=&p.querySwitch=0&p.keyword=%C5%AE%C9%FA%D3%C5%CF%C8&p.keywordType=2&p.workLocation="
    ]
    domain_url = "https://www.jobcn.com"
    def parse(self, response):
       """find the next url"""

       job_section_dom = response.css("div.job_view div.item_job")
       for job in job_section_dom:
           uri = job.css("h4.job_name a::attr(href)").get()
           url = self.domain_url+uri 
           yield {"url": url}                    
       # next page should be li with text "next page"
       # next page is in the start url list already, this website disable the content of pagination

class ZhuoBoJDSpider(Spider):
    name="step_two_zhuobo_jd_content"
    # start_urls = [
    #     "https://www.jobcn.com/position/detail.xhtml?redirect=0&posId=4024342&comId=361102&s=search/advanced&acType=1", 
    #     "https://www.jobcn.com/position/detail.xhtml?redirect=0&posId=4003669&comId=361102&s=search/advanced&acType=1"
    # ]

    def start_requests(self):
        """read the extra_urls_with_next.json file"""
        # with open("./zhuobo_male_urls_all.json", "r") as f:
        with open("./zhuobo_female_urls.json", "r") as f:
            data = json.load(f)
        try:
            for item in data:
                yield Request(url=item.get('url'), callback=self.parse)
        except:
            return []   

    def parse(self, response):
        jd_item = ZhuoBoJDItem()
        company_info_dom = response.css("div.nav_pos div.info div.base")
        company_name = company_info_dom.css("h2::text").get()
        # this should be industry, not type
        company_type = company_info_dom.xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '行业')]/following-sibling::dd/a/text()").get()
        company_size = company_info_dom.xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '规模')]/following-sibling::dd/text()").get()
        company_location = company_info_dom.xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '地址')]/following-sibling::dd/text()").get()
        
        job_content_dom = response.xpath("//div[@id='jobcnMainContent']")
        job_title = job_content_dom.css("div.name_pos h2.name span::text").get()
        salary_range = job_content_dom.css("div.name_pos div.salary div.salary_body::text").get()
        age_requirement = job_content_dom.css("div.info_pos").xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '年龄要求')]/following-sibling::dd/text()").get()
        gender_requirement = job_content_dom.css("div.info_pos").xpath("./div[@class='attributes clearfix']/dl/dt[contains(text(), '性别要求')]/following-sibling::dd/text()").get()
        jd_content = job_content_dom.css("div.desc_pos::text").extract()
        job_description = []
        for s in jd_content:
            if s.strip():
                job_description.append(s.strip())
        # descrimination_content = ' '.join([s for s in job_description if '男' in s]).strip()
        descrimination_content = ' '.join([s for s in job_description if '女' in s]).strip()
        job_type = job_content_dom.css("div.tip_pos").xpath("./dl/dt[contains(text(), '职位类别')]/following-sibling::dd/a/text()").extract()
        keywords = job_content_dom.css("div.tip_pos").xpath("./dl/dt[contains(text(), '职位标签')]/following-sibling::dd/a/text()").extract()
        
        jd_item["url"] = response.url
        jd_item["job_title"] = job_title
        jd_item["job_description"] = job_description
        jd_item["descrimination_content"] = descrimination_content
        jd_item["keywords"] = keywords
        jd_item["job_type"] = job_type
        try:
            # TODO: now assume first two is city, next two is district
            # TODO: use 现居住地 as source of city
            jd_item["province"] = company_location[:2]
            jd_item["city"] = company_location[2:4]
            jd_item["district"] = company_location[2:4]
        except:
            jd_item["province"] = ""
            jd_item["city"] = ""
            jd_item["district"] = ""        
        jd_item["company_location"] = company_location  
        jd_item["company_name"] = company_name
        jd_item["company_type"] = company_type
        jd_item["company_size"] = company_size
        jd_item["salary_range"] = salary_range  # contains ¥ 月薪
        jd_item["age_requirement"] = age_requirement
        jd_item["gender_requirement"] = gender_requirement

        yield jd_item