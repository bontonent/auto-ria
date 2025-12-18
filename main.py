# parsing
import requests
from lxml import html
import json

# visual load
from tqdm import tqdm

# treading
from concurrent.futures import ThreadPoolExecutor, as_completed

# user agent random
import random
from user_agents import user_agents
from pathlib import Path

# py script
from car_page import product_page
from database import connect

class main_auto_ria:
    def __init__(self):
        self.datas = []
        self.page_urls = []
        # Get random User Agent
        self.base_dir = Path(__file__).resolve().parent
        dir_with_user_agent = "/".join([str(self.base_dir),"user_agents"])
        self.array_user_agents = user_agents.get_agent(dir_with_user_agent)
    
    # Change user_agent
    def update_headers(self):
        choose_user_agent = self.array_user_agents[random.randrange(0,len(self.array_user_agents)-1)]
        headers = {
            "User-Agent": choose_user_agent,
            "cookie": 'Path=/; ab_redesign=1; ab_test_new_pages=1; chk=1; ui=d97ff2002e387632; PHPSESSID=eyJ3ZWJTZXNzaW9uQXZhaWxhYmxlIjp0cnVlLCJ3ZWJQZXJzb25JZCI6MCwid2ViQ2xpZW50SWQiOjM2NDkwNDA4OTYsIndlYkNsaWVudENvZGUiOjc3NTQ1MjIxMCwid2ViQ2xpZW50Q29va2llIjoiZDk3ZmYyMDAyZTM4NzYzMiIsIl9leHBpcmUiOjE3NjYwNDMxMDk2NTMsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; PHPLOGINSESSID=p37mu2plcdc7efpc0t79lavsk3; project_id=2; project_base_url=https://auto.ria.com/iframe-ria-login; showNewFeatures=7; _504c2=http://10.42.2.152:3000; g_state={"i_l":0,"i_ll":1765979996400,"i_b":"ceOMXJAK8LcP7a3V22ut0+DcCPGEJlD1kHJNS6obTq0","i_e":{"enable_itp_optimization":0}}'
        }
        return headers
    
    def main(self):
        # parsing catalog
        self.get_url_from_catalog()
        
        # parsing product_page
        self.get_data_from_product_page()
        
        # save data in postgres
        self.pull_data()

    # Pull data
    def pull_data(self):
        for data in self.datas:
            connect.create_row(data)
    
    def get_url_from_catalog(self):
        i_page = 0
        while True:
            tqdm(i_page)
            payload = f"page={i_page}&langId=4&device=desktop-web&search_type=2&mileage%5B0%5D=0&abroad=0&customs_cleared=1&onlyItems=1&limit=20"
            catalog_url = f"https://auto.ria.com/uk/search/?indexName=auto&page={i_page}"
            
            headers = self.update_headers()
            response = requests.get(catalog_url,headers = headers,data = json.dumps(payload))
            
            # Check, have close or not
            page_catalog = html.fromstring(response.content)
            buttons_dis = page_catalog.xpath('//button[@disabled]/@title')
            
            # script
            script_catalog_page = page_catalog.xpath('//script[contains(text(),"window.__PINIA__")]/text()')
            slipt_json_script = str(script_catalog_page).split("publishTime")
            for i_tql, try_get_link in enumerate(slipt_json_script[1:]):
                self.page_urls.append(str(try_get_link).split('"link":')[1].split(',')[0].replace('\"',""))
                
                # avoid douplicate(describe in README.md)
                if i_tql == 19:
                    break
            
            # if find Next page disactivate, It is end page.
            for button_dis in buttons_dis:
                if button_dis == 'Next':
                    print("find end")
                    break
            i_page = i_page+1
        
    def get_data_from_product_page(self):
        headers = self.update_headers()
        
        # Get data from product pages
        max_workers = 5
        time_delay = 2
        retries_work = 1
        futures = {}

        # Treading
        with ThreadPoolExecutor(max_workers) as thread:
            for page_url in tqdm(self.page_urls):
                futures[thread.submit(product_page.get_data, page_url, headers)] = page_url
            for fut in tqdm(as_completed(futures),total=len(futures)):
                src = futures[fut]
                try:
                    result_data = fut.result(timeout=time_delay)
                    self.datas.append(result_data)
                except Exception as e:
                    # if error try again
                    if retries_work > 0: 
                        for n in range(retries_work):
                            try:
                                headers = update_headers()
                                retry_res = thread.submit(product_page.get_data, page_url,headers).result(timeout=time_delay)
                                
                                result_data = retry_res
                                self.datas.append(result_data)
                                break
                            except Exception as e:
                                continue
        
# Run
if __name__ == "__main__":
    class_auto_ria = main_auto_ria()
    class_auto_ria.main()
