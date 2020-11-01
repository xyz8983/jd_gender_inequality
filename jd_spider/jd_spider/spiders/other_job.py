import json

def find_unvisited_urls():
    with open("./zhuobo_male_urls_all.json", 'r') as f:
        all_urls = json.load(f)
        all_urls_list = [item["url"] for item in all_urls]
        print("how many urls: ", len(all_urls_list))  #86
        all_urls_set = set(all_urls_list)
        print("how many distinct urls:", len(all_urls_set))  #46

    with open("./zhuobo_male_all_jd_content.json", 'r') as f:
        jd_obj = json.load(f)
        visited_url_list = [item["url"] for item in jd_obj]
        print("how many visited urls:", len(visited_url_list))  #44
        visited_urls = set(visited_url_list)
        print("visited distinct urls:", len(visited_urls))  #44

    # with open("./zhuobo_unvisited_urls.json", 'w') as f:
    #     unvisited_urls = list(all_urls_set -  visited_urls)    
    #     json.dump(unvisited_urls, f)

def find_discrimation_word(keyword, fpath, ouputpath):
    with open(fpath, 'r') as f:
        data = json.load(f)
        for item in data:
            descrimination_content = ' '.join([s for s in item["job_description"] if keyword in s]).strip()
            item["descrimination_content"] = descrimination_content
    with open(ouputpath, 'w') as f:
        json.dump(data, f, ensure_ascii=False)

if __name__=='__main__':
    # find_unvisited_urls()
    find_discrimation_word('女', "./zhuobo_female_jd_contents_no.json", "./zhuobo_female_jd_contents.json")