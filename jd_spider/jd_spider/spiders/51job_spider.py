from scrapy import Spider, Request
from jd_spider.items import WuYiJDItem
import json

"""
wuyi job website's search function works well, and ensure the result content will have the exact search words
but the search words may not be in the JD part, maybe in keywords part, hence being excluded
"""

# all at once
class WuYiJDSpider(Spider):
    name="wuyi_job_female_first"
    # 51job.com search box: male first, whole country
    # start_urls = ["https://search.51job.com/list/000000,000000,0000,00,9,99,%25E7%2594%25B7%25E7%2594%259F%25E4%25BC%2598%25E5%2585%2588,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="]
    # start_urls = ["https://search.51job.com/list/000000,000000,0000,00,9,99,%25E7%2594%25B7%25E7%2594%259F%25E4%25BC%2598%25E5%2585%2588,2,1.html"]
    start_urls = ["https://search.51job.com/list/000000,000000,0000,00,9,99,%25E5%25A5%25B3%25E7%2594%259F%25E4%25BC%2598%25E5%2585%2588,2,1.html"]
    def parse(self, response):
       """find the next url"""
       jd_urls = []
       for p in response.css("p.t1"):
           url = p.css("span a::attr(href)").get()
           jd_urls.append(url)
           yield Request(url, callback=self.parse_content)
           # todo: dump the jd urls to a json file 
       # next page should be li with text "next page"        
       next_page = response.xpath("//li/a[contains(text(), '下一页')]").xpath("@href").get()
       if next_page:
           yield Request(next_page, callback=self.parse)

    def parse_content(self, response):
        jd_header_dom = response.css("div.tHjob div.in div.cn")
        jd_item = WuYiJDItem()
        jd_item["url"] = response.url
        jd_item["job_title"] = jd_header_dom.css("h1::text").get()
        # todo: salary range contains text
        jd_item["salary_range"] = jd_header_dom.css("strong::text").get()
        # jdItem.job_title = response.xpath("//div[@class='tHeader tHjob']/div[@class='in']/div[@class='cn']/h1/text()").get()
        jd_item["company_name"] = jd_header_dom.css("p.cname a::text").get()
        location = jd_header_dom.css("p.msg::text").get().strip()
        if location:
            try:
                city, district = location.split("-")
                jd_item["city"] = city
                jd_item["district"] = district
            except:
                # location only has city name, no district
                jd_item["city"] = location
                jd_item["district"] = location
        jd_content_dom = response.xpath("//div[@class='bmsg job_msg inbox']")
        # jd_content = jd_content_dom.xpath("./p/text() | ./p/span/text() | ./text()").extract()
        # jd_content_dom.xpath("./descendant::*/text()[not(ancestor::div[@class='share']) and not(ancestor::div[@class='mt10'])]").extract()  
        jd_content = jd_content_dom.xpath("./descendant::*/text()[not(ancestor::div[@class='share'] or ancestor::div[@class='mt10'])] | ./text()").extract()  
        # todo: remove 1. 2. or 1、2、 unnecesseary data
        jd_item["job_description"] = [] # a list of string
        for s in jd_content:
            if s.strip():
                jd_item["job_description"].append(s.strip())
        # TODO: change the criteria key workds here!        
        jd_item["descrimination_content"] = ' '.join([s for s in jd_item["job_description"] if '女生' in s]).strip()
        # jd_item["job_type"] = jd_content_dom.css("p.fp a.tdn::text").get()
        jd_item["job_type"] = jd_content_dom.xpath("./div[@class='mt10']/p/span[contains(text(), '职能类别')]/following-sibling::a/text()").extract()
        jd_item["keywords"] = jd_content_dom.xpath("./div[@class='mt10']/p/span[contains(text(), '关键字')]/following-sibling::a/text()").extract()
        company_info = response.css("div.tCompany_sidebar div.com_tag")
        jd_item["company_type"] = company_info.xpath("./p[1]/text()").get()
        jd_item["company_size"] =  company_info.xpath("./p[2]/text()").get()

        yield jd_item


# step 1
class WuYiJDUrlSpider(Spider):
    """ save the urls to somewhere and pass the content on another class"""
    name="step_one_get_wuyi_job_urls"
    # male first, whole country (51job.com search box)
    # start_urls = ["https://search.51job.com/list/000000,000000,0000,00,9,99,%25E7%2594%25B7%25E7%2594%259F%25E4%25BC%2598%25E5%2585%2588,2,1.html"]
    # female first, whole country
    start_urls = ["https://search.51job.com/list/000000,000000,0000,00,9,99,%25E5%25A5%25B3%25E7%2594%259F%25E4%25BC%2598%25E5%2585%2588,2,1.html"]
    
    def parse(self, response):
       """find the next url"""
       for p in response.css("p.t1"):
           url = p.css("span a::attr(href)").get()
           yield {"url": url}                      
       # next page should be li with text "next page"
       next_page = response.xpath("//li/a[contains(text(), '下一页')]").xpath("@href").get()
       if next_page:
           yield Request(next_page, callback=self.parse)


# step 2
class WuYiJDParsingSpider(Spider):
    """read the json file to get all urls, request each jd url to parse the content"""
    name = "step_two_parse_wuyi_job_jd"

    def start_requests(self):
        """read the extra_urls_with_next.json file"""
        with open("./wuyi_missed_parsing_urls_female.json", "r") as f:
            data = json.load(f)
        try:
            for item in data:
                yield Request(url=item.get('url'), callback=self.parse)
        except:
            return []   
                
    # TODO: parse gender info as extra args
    def parse(self, response):
        jd_header_dom = response.css("div.tHjob div.in div.cn")
        job_title = jd_header_dom.css("h1::text").get()
        # TODO: salary range contains text
        # monthly wage，有的以万为单位 有的以千为单位 => collect in original status and clean before analysis, to avoid losing data 
        salary_range = jd_header_dom.css("strong::text").get()
        # jdItem.job_title = response.xpath("//div[@class='tHeader tHjob']/div[@class='in']/div[@class='cn']/h1/text()").get()
        company_name = jd_header_dom.css("p.cname a::text").get()
        location = jd_header_dom.css("p.msg::text").get().strip()
        company_address = response.xpath("//div[@class='bmsg inbox']/p/text()").get()
        
        jd_content_dom = response.xpath("//div[@class='bmsg job_msg inbox']")
        # jd_content = jd_content_dom.xpath("./p/text() | ./p/span/text()").extract()
        jd_content = jd_content_dom.xpath("./descendant::*/text()[not(ancestor::div[@class='share'] or ancestor::div[@class='mt10'])] | ./text()").extract()  
        # todo: remove 1. 2. or 1、2、 unnecesseary data
        job_description = [] # a list of string
        for s in jd_content:
            if s.strip():
                job_description.append(s.strip())
        descrimination_content = ' '.join([s for s in job_description if '女' in s or '男' in s]).strip()
        # jd_item["job_type"] = jd_content_dom.css("p.fp a.tdn::text").get()
        job_type = jd_content_dom.xpath("./div[@class='mt10']/p/span[contains(text(), '职能类别')]/following-sibling::a/text()").extract()
        keywords = jd_content_dom.xpath("./div[@class='mt10']/p/span[contains(text(), '关键字')]/following-sibling::a/text()").extract()
        company_info = response.css("div.tCompany_sidebar div.com_tag")
        company_type = company_info.xpath("./p[1]/text()").get()
        # TODO:  '50-150人' => need future cleaning before analysis
        company_size =  company_info.xpath("./p[2]/text()").get()
        company_industry = company_info.xpath("./p[3]/a/text()").getall() # [str]
        
        jd_item = WuYiJDItem()
        jd_item["url"] = response.url
        jd_item["job_title"] = job_title
        jd_item["salary_range"] = salary_range
        jd_item["company_name"] = company_name
        try:
            city, district = location.split("-")
            jd_item["city"] = city
            jd_item["district"] = district
        except:
            # location only has city name, no district
            jd_item["city"] = location
            jd_item["district"] = location
        jd_item["job_description"] = job_description
        jd_item["descrimination_content"] = descrimination_content
        jd_item["job_type"] = job_type
        jd_item["keywords"] = keywords
        jd_item["company_type"] = company_type
        jd_item["company_size"] = company_size
        jd_item["company_industry"] = company_industry
        jd_item["company_address"] = company_address

        yield jd_item
