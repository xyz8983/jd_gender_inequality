### Gender Inequality in Job Posting
In some job postings, the contents contains gender discrimination words such as "male first" or "female first", some even listing "male only" or "female only". This project crawls 3 most popular recruiting websites(51 job, zhuo bo zhao pin, lie pin) that contain the gender discrimination words, then compare different genders across several angles: industry, job type, company type, the gender specific requirements, etc, to analyze what is the gender discrimination situation in current job markets.

#### Data Collection
##### Crawling and Parsing
Using Scrapy Spiders to crawl and parse job posting contents from several recruiting websites  
Each recruiting website has a corresponding Spider class due to different html structure of different websites.

`scrapy crawl <spider_class_name> --output=<output_path>`  
Example:
`scrapy crawl a_spider --output=./jd_spider/spiders/output/test.json`

##### Data fields 
Please check jd_spider/spiders/items.py for details
Fields include:
- url 
- company_name
- company_type (nullable for example: 民营公司)
- company_size
- company_industry (for example: 互联网/电子商务 批发/零售)
- company_address (nullable, detailed address)
- city
- district (nullable)
- province (nullable)
- job_title
- job_type (nullable, for example: 职能类别)
- job_description
- descrimination_content 
- keywords (nullable, for example: 职位标签, 关键字)
- salary_range
- gender_preference （an aggregation field, However, zhuobo has particular fields for gender in the job posting page)
- age_requirement (nullable, usualy in the text, needs extra cleanning)

##### Data Outputs
Each recruiting website will have a separate spider job due to the different web page structure for data parsing. Each spider job will generate 4 json files:
- urls for "male first" job posts
- data for "male first" job posts
- urls for "female first" job posts
- data for "female first" job posts

All Data is stored in a sqlite database, please using the following commands to check the table  
start sqlite3 command prompt `sqlite3`  
open db file `.open job_description.db`  
listing all the table schemas `.tables`  

