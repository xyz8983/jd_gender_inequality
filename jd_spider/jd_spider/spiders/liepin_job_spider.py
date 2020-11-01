from scrapy import Spider, Request
from jd_spider.items import LiePinJDItem
import json

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

class LiePinJDSpider(Spider):
    name = "step_two_liepin_jd_content"

    # start_urls = [
    #     "https://www.liepin.com/job/1915641888.shtml",
    #     "https://www.liepin.com/job/1916303431.shtml",
    #     "https://www.liepin.com/job/1928752089.shtml"
    # ]

    def start_requests(self):
        """read the extra_urls_with_next.json file"""
        with open("./liepin_male_urls.json", "r") as f:
            data = json.load(f)
        try:
            for item in data:
                yield Request(url=item.get('url'), callback=self.parse)
        except:
            return []   

    def parse(self, response):
        # some jd does not have a whole phrase 男生优先 or 男性优先, but separately
        # like 男性 in one sentence, 优先 in another sentence, which is not the target JD
        
        job_title = response.css("div.title-info h1::text").get()
        company_name = response.css("div.title-info h3 a::text").get()
        job_general_dom = response.xpath("//div[@class='job-title-left']")
        # 月薪*12 or 面议
        salary_range = job_general_dom.css("p.job-item-title::text").get().strip()
        location = job_general_dom.css("p.basic-infor a::text").get().strip()
        try:
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
            if ('男生优先' in s) or '男性优先' in s:
               descrimination_content.append(s.strip())      
        descrimination_content = ' '.join(descrimination_content).strip()
        company_info_dom = response.css("ul.new-compintro")
        company_industry = company_info_dom.xpath("./li[1]/a/text()").get() # 经营范围，可只截取前3个
        company_size = company_info_dom.xpath("./li[2]/text()").get() # 公司规模
        try:
            company_size = company_size.split("：")[1] # special ":"
        except:
            pass
        
        # no company type
        jd_item = LiePinJDItem()
        jd_item["url"] = response.url
        jd_item["job_title"] = job_title
        jd_item["job_description"] = job_description
        jd_item["descrimination_content"] = descrimination_content
        # keywords = Field() #[str]  #todo: the first 2-3 is enough
        # job_type = Field() #[str] 
        jd_item["city"] = city
        jd_item["district"] = district
        jd_item["company_name"] = company_name
        # company_type = Field() # str
        jd_item["company_size"] = company_size
        jd_item["salary_range"] = salary_range
        jd_item["company_industry"] = company_industry
        if descrimination_content:
            yield jd_item

class LiepinJDSpiderW(Spider):
    """complete urls and content parsing in one try"""

    name="liepin_female_jd_contents"
    # search "女性优先", "女生优先"
    start_urls = [
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=a9b1aabb1d7c380e106d6f46abf02e70&d_ckId=a9b1aabb1d7c380e106d6f46abf02e70&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=wSCrzhkotIBcV9OGxXD1rg%7EfA9rXquZc5IkJpXC-Ycixw&key=%E5%A5%B3%E6%80%A7%E4%BC%98%E5%85%88",
        "https://www.liepin.com/zhaopin/?industries=&subIndustry=&dqs=&salary=&jobKind=&pubTime=&compkind=&compscale=&searchType=1&isAnalysis=&sortFlag=15&d_headId=dc7d2b94f8d9dc8b045a49082c39ca9a&d_ckId=dc7d2b94f8d9dc8b045a49082c39ca9a&d_sfrom=search_prime&d_curPage=0&d_pageSize=40&siTag=YX6bUD1fG5pEsNX9LXYV6g%7EfA9rXquZc5IkJpXC-Ycixw&key=%E5%A5%B3%E7%94%9F%E4%BC%98%E5%85%88"
    ]

    def parse(self, response):
        """find the next url"""
        job_section_dom = response.css("div.sojob-result")
        job_listings = job_section_dom.css("ul.sojob-list li")
        for job_list in job_listings:
            url = job_list.css("div.job-info h3 a::attr(href)").get()
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
        salary_range = job_general_dom.css("p.job-item-title::text").get().strip()
        location = job_general_dom.css("p.basic-infor a::text").get().strip()
        try:
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
            if any(phrase in s for phrase in ['女生优先', '女性优先', '限女', '女生，']):
            # if ('女生优先' in s) or ('女性优先' in s) or ('限女' in s) or ('女生,' in s):
               descrimination_content.append(s.strip())      
        descrimination_content = ' '.join(descrimination_content).strip()
        company_info_dom = response.css("ul.new-compintro")
        company_industry = company_info_dom.xpath("./li[1]/a/text()").get()
        company_size = company_info_dom.xpath("./li[2]/text()").get()
        try:
            company_size = company_size.split("：")[1] # special ":"
        except:
            pass

        jd_item = LiePinJDItem()
        jd_item["url"] = response.url
        jd_item["job_title"] = job_title
        jd_item["job_description"] = job_description
        jd_item["descrimination_content"] = descrimination_content
        # keywords = Field() #[str]  #todo: the first 2-3 is enough
        # job_type = Field() #[str] 
        jd_item["city"] = city
        jd_item["district"] = district
        jd_item["company_name"] = company_name
        # company_type = Field() # str
        jd_item["company_size"] = company_size
        jd_item["salary_range"] = salary_range
        jd_item["company_industry"] = company_industry
        if descrimination_content:
            yield jd_item