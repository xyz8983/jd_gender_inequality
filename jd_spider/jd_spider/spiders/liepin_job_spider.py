from scrapy import Spider, Request
from jd_spider.items import LiePinJDItem, JDItem
import json
import os

class LiePinJDUrlSpider(Spider):
    name="step_one_liepin_jd_urls"
    # 关键字：男生优先， 男性优先
    start_urls = [
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=13725ba05aa5eb5e5608ab73ecd29faa&d_ckId=13725ba05aa5eb5e5608ab73ecd29faa&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=wSCrzhkotIBcV9OGxXD1rg%7EfA9rXquZc5IkJpXC-Ycixw&key=%E7%94%B7%E6%80%A7%E4%BC%98%E5%85%88",
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=13725ba05aa5eb5e5608ab73ecd29faa&d_ckId=13725ba05aa5eb5e5608ab73ecd29faa&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=wSCrzhkotIBcV9OGxXD1rg%7EfA9rXquZc5IkJpXC-Ycixw&key=%E7%94%B7%E7%94%9F%E4%BC%98%E5%85%88"
    ]

    def parse(self, response):
        job_section_dom = response.css("div.sojob-result")
        job_listings = job_section_dom.css("ul.sojob-list li")
        for job_list in job_listings:
            url = job_list.css("div.job-info h3 a::attr(href)").get()
            yield {"url": url}    
        # next page should be li with text "next page"
        next_page = response.xpath("//div[@class='pagerbar']/a[contains(text(), '下一页')]/@href").get()
        base_url = "https://www.liepin.com"
        if next_page:
            yield Request(base_url+next_page, callback=self.parse)


class LiepinJDSpider(Spider):
    """complete urls and content parsing in one try"""

    name = "liepin_job_spider"
    gender = "uni"
    # search "*性优先", "*生优先"
    # start_urls = [str] # initialize in children class
    #     "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=a9b1aabb1d7c380e106d6f46abf02e70&d_ckId=a9b1aabb1d7c380e106d6f46abf02e70&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=wSCrzhkotIBcV9OGxXD1rg%7EfA9rXquZc5IkJpXC-Ycixw&key=%E5%A5%B3%E6%80%A7%E4%BC%98%E5%85%88",
    #     "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=dc7d2b94f8d9dc8b045a49082c39ca9a&d_ckId=dc7d2b94f8d9dc8b045a49082c39ca9a&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=YX6bUD1fG5pEsNX9LXYV6g%7EfA9rXquZc5IkJpXC-Ycixw&key=%E5%A5%B3%E7%94%9F%E4%BC%98%E5%85%88"
    # ]
    start_urls = []
    gender_desc_keywords = [] # [str]
    def parse(self, response):
        """find the all and next urls of each job posting"""
        job_section_dom = response.css("div.sojob-result")
        job_listings = job_section_dom.css("ul.sojob-list li")
        for job_list in job_listings:
            url = job_list.css("div.job-info h3 a::attr(href)").get()
            with open("./liepin_urls_"+self.gender+".txt", "a") as f:
                # f.write(url)
                # f.write("\n")
                f.write(url+"\n")  
            yield Request(url, callback=self.parse_content)
        # next page should be li with text "next page"
        next_page = response.xpath("//div[@class='pagerbar']/a[contains(text(), '下一页')]/@href").get()
        base_url = "https://www.liepin.com"
        if next_page:
            yield Request(base_url+next_page, callback=self.parse)
    
    def parse_content(self, response):
        """parse the jd page"""
        
        job_title = response.css("div.title-info h1::text").get()
        company_name = response.css("div.title-info h3 a::text").get()
        job_general_dom = response.xpath("//div[@class='job-title-left']")
        salary_range = job_general_dom.css("p.job-item-title::text").get()
        if salary_range:
            salary_range = salary_range.strip()
        location = job_general_dom.css("p.basic-infor a::text").get()
        try:
            location = location.strip()
            city, district = location.split("-")
        except:
            city, district = location, location    
        
        jd_content_dom = response.css("div.job-description")
        jd_content = jd_content_dom.css("div.content-word::text").extract()
        job_description = []
        descrimination_content =[]
        for s in jd_content:
            if s.strip():
                job_description.append(s.strip())
            # example: if any(phrase in s for phrase in ['女生优先', '女性优先', '限女', '女生，']
            if any(phrase in s for phrase in self.gender_desc_keywords):
            # if ('女生优先' in s) or ('女性优先' in s) or ('限女' in s) or ('女生,' in s):
               descrimination_content.append(s.strip())      
        descrimination_content = ' '.join(descrimination_content).strip()
        company_info_dom = response.css("ul.new-compintro")
        company_industry = company_info_dom.xpath("./li[1]/a/text()").get()
        company_size = company_info_dom.xpath("./li[2]/text()").get()
        company_address = company_info_dom.xpath("./li[3]/text()").get()
        company_address = company_address.split("：")[-1] if company_address else None
        try:
            company_size = company_size.split("：")[1] # special ":"
        except:
            pass

        jd_item = JDItem()
        jd_item["url"] = response.url
        jd_item["company_name"] = company_name
        # company_type = Field() # null
        jd_item["company_size"] = company_size
        jd_item["company_industry"] = company_industry
        jd_item["company_address"] = company_address
        jd_item["city"] = city
        jd_item["district"] = district
        # province null
        
        jd_item["job_title"] = job_title
        # job_type null
        jd_item["job_description"] = job_description
        jd_item["descrimination_content"] = descrimination_content
        # keywords null
        # job_type null
        jd_item["salary_range"] = salary_range
        jd_item["gender_preference"] = self.gender
        # age_requirement null
        # jd_date null
        
        if descrimination_content:
            yield jd_item
        
            
class LiePinJDSpiderFemale(LiepinJDSpider):
    name = "liepin_job_spider_female"
    gender = "female"
    # search "*性优先", "*生优先"
    # initialize in children class
    start_urls = [
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=a9b1aabb1d7c380e106d6f46abf02e70&d_ckId=a9b1aabb1d7c380e106d6f46abf02e70&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=wSCrzhkotIBcV9OGxXD1rg%7EfA9rXquZc5IkJpXC-Ycixw&key=%E5%A5%B3%E6%80%A7%E4%BC%98%E5%85%88",
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=dc7d2b94f8d9dc8b045a49082c39ca9a&d_ckId=dc7d2b94f8d9dc8b045a49082c39ca9a&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=YX6bUD1fG5pEsNX9LXYV6g%7EfA9rXquZc5IkJpXC-Ycixw&key=%E5%A5%B3%E7%94%9F%E4%BC%98%E5%85%88"
    ]
    gender_desc_keywords = ['女生优先', '女性优先', '限女', '女生，']

class LiePinJDSpiderMale(LiepinJDSpider):
    name = "liepin_job_spider_male"
    gender = "male"
    start_urls = [
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=e4939778145f83f63c6969baba946b0c&d_ckId=e4939778145f83f63c6969baba946b0c&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=YX6bUD1fG5pEsNX9LXYV6g%7EfA9rXquZc5IkJpXC-Ycixw&key=%E7%94%B7%E6%80%A7%E4%BC%98%E5%85%88",
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=1a938bf2d0fae20cafa4498873a66396&d_ckId=1a938bf2d0fae20cafa4498873a66396&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=wSCrzhkotIBcV9OGxXD1rg%7EfA9rXquZc5IkJpXC-Ycixw&key=%E7%94%B7%E7%94%9F%E4%BC%98%E5%85%88"
    ]
    gender_desc_keywords = ['男生优先', '男性优先', '限男', '男生，']
    
class LiePinJDSpiderMale_two(LiepinJDSpider):
    """the urls crawling job gets back result but the actual parsing job is forced to be separated"""
    name = "liepin_job_spider_male_two"
    start_urls = None
    gender = "male"
    gender_desc_keywords = ['男生', '男性','优先', '限男', '男生，']
    def start_requests(self):
        """
        read liepiin urls file 
        used when crawling urls and crawling contents are forced to be separated.
        """
        # relative path wont work
        with open(os.path.dirname(os.path.abspath(__file__))+"/output/liepin_urls_male.txt", "r") as f:
            data = f.readlines()
        for url in data:
            try:
                yield Request(url=url, callback=self.parse_content)
            except:
                return   
    def parse(self, response):
        pass
class LiePinJDSpiderFemale_two(LiepinJDSpider):
    name = "liepin_job_spider_female_two"
    start_urls = None
    gender = "female" 
    gender_desc_keywords = ['女生优先', '女性','优先', '限女', '女生，']
    def start_requests(self):
        """
        read liepiin urls file 
        used when crawling urls and crawling contents are forced to be separated.
        """
        # relative path wont work
        with open(os.path.dirname(os.path.abspath(__file__))+"/output/liepin_urls_female.txt", "r") as f:
            data = f.readlines()
        for url in data:
            try:
                yield Request(url=url, callback=self.parse_content)
            except:
                return   
    def parse(self, response):
        pass