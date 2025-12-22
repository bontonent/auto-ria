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



# user agent random
import random
from user_agents import user_agents
from pathlib import Path

# py script
from car_page import product_page
from database import connect

# treading
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ThreadPoolExecutor


class main_auto_ria:
    def __init__(self):
        self.datas = []
        self.link_product_pages = []
        
        #self.end_page = None

        # First page scraping
        self.i_page= 0
        # Finally page scraping
        self.end_page = 10

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
        
        #make unique data
        unique_link_product_pages = np.unique(self.link_product_pages)
        self.link_product_pages = [[str(url.replace("\n","").strip())] for url in unique_link_product_pages]

        
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

    def time_change(self, history_time, time_up):
        
        if time_up:
            time_step = 0,4
        else:
            time_step = -0,4
        # if a lot of history we remove change time
        change_step = len(history_time)/100
        if change_step > 1:
            step_time = time_step/change_step
            history_el = -int(change_step/10)
        else:
            step_time = time_step
            history_el = -2
        all_time_sleep_max = 10
        self.time_at_the_moment = np.average(history_time[history_el:])+step_time
        if all_time_sleep_max <= self.time_at_the_moment:
            all_time_sleep_max = self.time_at_the_moment


    
    def get_data_from_product_page(self):
        headers = self.update_headers()
        # Setting get data from product page

        max_workers = 3     # speed
        retry_work = 1      # retry work
        

        # setting time sleep
        time_delay = 2      # if delay time error thread
        history_time = [5, 5, 5, 5]
        self.time_at_the_moment = 5
        
        
        
        retries_work_break = 2    # for reload with error 429 how real human
        time_delay_for_break = 0.01
        at_the_moment_time = np.average(history_time)
        

        futures = {}
        # Treading
        with ThreadPoolExecutor(max_workers) as thread:
            for page_url_ar in tqdm(self.link_product_pages):
                page_url = page_url_ar[0]
                futures[thread.submit(product_page.get_data, page_url, headers)] = page_url
            for fut in tqdm(as_completed(futures),total=len(futures)):
                
                try:
                    src = futures[fut]
                    time.sleep(self.time_at_the_moment/4)
                    result_data = fut.result(timeout=time_delay)
                    if str(result_data) == 'break':
                        raise ValueError('Error')
                    self.datas.append(result_data)
                    time.sleep(self.time_at_the_moment/4)
                    
                    self.time_change(history_time,time_up=False)
                except Exception as e:
                    print(src,e)
                    # if error try again
                    
                    
                    #retry work
                    if retry_work > 0:
                        for retry_work_n in range(retry_work):
                            if retries_work_break > 0:    
                                # break work for reload page
                                for n in range(retries_work_break): # this kill reload funtion - reload retries times and kill thamselve
                                    try:
                                        headers = self.update_headers()
                                        retry_res = thread.submit(product_page.get_data, src, headers).result(timeout=time_delay_for_break)
                                        result_data = retry_res
                                        if str(result_data) == 'break':
                                            raise ValueError('Error')
                                        
                                        self.datas.append(result_data)
                                        break
                                    except Exception as e:
                                        None
                                        continue
                            
                            # retry get data
                            try:
                                time.sleep(self.time_at_the_moment/2)
                                headers = self.update_headers()
                                retry_res = thread.submit(product_page.get_data, src, headers).result(timeout=time_delay_for_break)
                                result_data = retry_res
                                if str(result_data) == 'break':
                                    raise ValueError('Error')
                                
                                self.datas.append(result_data)
                                break
                            except Exception as e:
                                self.time_change(history_time,time_up=True)
                                print(src,e)
                                continue
                time.sleep(self.time_at_the_moment/2)



# Run
if __name__ == '__main__':
    class_auto_ria = main_auto_ria()
    class_auto_ria.main()
#asyncio.run(run_asyncio())   