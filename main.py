# text
import json
import re
import numpy as np

# parsing
import requests
from lxml import html
import time

# visual load
from tqdm import tqdm

# treading
#from concurrent.futures import ThreadPoolExecutor, as_completed

# user agent random
import random
from user_agents import user_agents
from pathlib import Path

# py script
from car_page import product_page
from database import connect


from concurrent.futures import ThreadPoolExecutor

from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager

class main_auto_ria:
    def __init__(self):
        self.datas = []
        self.link_product_pages = []
        
        self.end_page = None

        # First page scraping
        self.i_page= 0
        # Finally page scraping
        self.end_page = 1

        # Get random User Agent
        self.base_dir = Path(__file__).resolve().parent
        dir_with_user_agent = "/".join([str(self.base_dir),"user_agents"])
        self.array_user_agents = user_agents.get_agent(dir_with_user_agent)
    
    # Change user_agent
    def update_headers(self):
        choose_user_agent = self.array_user_agents[random.randrange(0,len(self.array_user_agents)-1)]
        headers = {
            "User-Agent": choose_user_agent
            , "cookie": 'Path=/; ab_redesign=1; ab_test_new_pages=1; chk=1; ui=d97ff2002e387632; PHPSESSID=eyJ3ZWJTZXNzaW9uQXZhaWxhYmxlIjp0cnVlLCJ3ZWJQZXJzb25JZCI6MCwid2ViQ2xpZW50SWQiOjM2NDkwNDA4OTYsIndlYkNsaWVudENvZGUiOjc3NTQ1MjIxMCwid2ViQ2xpZW50Q29va2llIjoiZDk3ZmYyMDAyZTM4NzYzMiIsIl9leHBpcmUiOjE3NjYwNDMxMDk2NTMsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; PHPLOGINSESSID=p37mu2plcdc7efpc0t79lavsk3; project_id=2; project_base_url=https://auto.ria.com/iframe-ria-login; showNewFeatures=7; _504c2=http://10.42.2.152:3000; g_state={"i_l":0,"i_ll":1765979996400,"i_b":"ceOMXJAK8LcP7a3V22ut0+DcCPGEJlD1kHJNS6obTq0","i_e":{"enable_itp_optimization":0}}'
        }
        return headers
    
    def main(self):
        # parsing catalog
        headers = self.update_headers()

        # Setting parsing product page
        max_workers=10

        with ThreadPoolExecutor(max_workers) as executor:
            for i in range(max_workers):
                executor.submit(self.get_url_from_catalog,headers)
        
        # parsing product_page
        self.get_data_from_product_page()
        
        # # save data in postgres
        self.pull_data()

    # Pull data
    def pull_data(self):
        for data in tqdm(self.datas):
            connect.create_row(data, "/".join([str(self.base_dir),"dumps"]))
    
    def get_url_from_catalog(self,headers):
        while True:
            payload = f"indexName=auto&page={self.i_page}"
            catalog_url = f"https://auto.ria.com/uk/search/?indexName=auto&page={self.i_page}"
            self.i_page = self.i_page+1
            if self.end_page == None:
                None
            elif int(self.i_page) > int(self.end_page):
                break

            response = requests.get(catalog_url,headers = headers,data = json.dumps(payload))
            
            page_catalog = html.fromstring(response.content)
            # Check, have close or not
            buttons_dis = page_catalog.xpath('//button[@disabled]/@title')
            
            # script
            script_catalog_page = page_catalog.xpath('//script[contains(text(),"window.__PINIA__")]/text()')
            script_text = script_catalog_page[0]

            match = re.search(r'window\.__PINIA__\s*=\s*(\{.*?\});', script_text, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                all_json_item = json.loads(json_str)
                for templates in all_json_item["page"]["structures"]["/uk/search/"]["templates"]:
                    if templates['id'] == "formCW":
                        second_templates = templates['templates']
                        for second_template in second_templates:
                            if second_template['id'] == 'output':
                                thierd_templates = second_template['templates']
                                for thierd_template in thierd_templates:
                                    if thierd_template["id"] == 'items':
                                        fourth_templates = thierd_template['templates']
                                        for fourth_template in fourth_templates:
                                            try:
                                                link_product_page = fourth_template['component']['advertisementCard']['data']['link']
                                                self.link_product_pages.append(str(link_product_page).split())
                                            except:
                                                None
            
            
            #if find Next page disactivate, It is end page.
            for button_dis in buttons_dis:
                if button_dis == 'Next':
                    self.end_page = self.i_page
                    break
            
            print("Catalog page:",self.i_page-sleend_page," items get:",len(self.link_product_pages))
            # fist_give = self.link_product_pages
            # self.get_data_from_product_page(fist_give)


    def get_data_from_product_page(self):
        headers = self.update_headers()
        # Setting get data from product page

        max_workers = 3     # speed
        time_delay = 2      # don't longer than 2 seond on item
        retries_work = 3    # for reload with error 429 how real people
        futures = {}

        # Treading
        with ProcessPoolExecutor(max_workers) as process:
            for page_url_ar in tqdm(self.link_product_pages):
                page_url = page_url_ar[0]
                futures[process.submit(product_page.get_data, page_url, headers)] = page_url
            for fut in tqdm(as_completed(futures),total=len(futures)):
                try:
                    src = futures[fut]
                    time.sleep(0.4)
                    result_data = fut.result(timeout=time_delay)
                    if str(result_data) == 'break':
                        raise ValueError('Error')
                    self.datas.append(result_data)
                    time.sleep(0.4)
                except Exception as e:
                    print(src,e)

                    # if error try again
                    time_delay_for_break = 0.01
                    if retries_work > 0:    
                        for n in range(retries_work):
                            try:
                                headers = self.update_headers()
                                retry_res = process.submit(product_page.get_data, src, headers).result(timeout=time_delay_for_break)
                                result_data = retry_res
                                if str(result_data) == 'break':
                                    raise ValueError('Error')
                                
                                self.datas.append(result_data)
                                break
                            except Exception as e:
                                None
                                continue
                        try:
                            time.sleep(1.0)
                            headers = self.update_headers()
                            retry_res = process.submit(product_page.get_data, src, headers).result(timeout=time_delay_for_break)
                            result_data = retry_res
                            if str(result_data) == 'break':
                                raise ValueError('Error')
                            
                            self.datas.append(result_data)
                            break
                        except Exception as e:
                            print(src,e)
                            continue



# Run
if __name__ == '__main__':
    class_auto_ria = main_auto_ria()
    class_auto_ria.main()
#asyncio.run(run_asyncio())   