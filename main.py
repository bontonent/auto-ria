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
import threading


from multiprocessing import Process, Queue, cpu_count
import queue as _queue

class main_auto_ria:
    def __init__(self):
        self.datas = []
        self.link_product_pages = []
        #self.end_page = None

        # First page scraping
        self.i_page= 100
        # Finally page scraping
        self.end_page = 200

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
        q_catalog_product = Queue()
        q_product_database = Queue()

        # Setting parsing product page
        max_workers=10
        number_workers = Process(target=self.get_url_from_catalog, args=(q_catalog_product,))
        
        # Parsing product_page
        proc_product_page = Process(target=self.get_data_from_product_page, args=(q_catalog_product, q_product_database,))
        
        # Pull data
        proc_database = Process(target=self.pull_data, args=(q_product_database,))
        
        # Start all process
        number_workers.start()
        proc_product_page.start()
        proc_database.start()

        # Join all process(but stop themselve anyway)
        number_workers.join()

        # Start work process
        proc_product_page.join()
        proc_database.join()

    # Pull data
    def pull_data(self, q_product_database):
        finish_work = False
        while True:
            items = []

            try:
                while True:
                    item = q_product_database.get(timeout=0.5)
                    if item == 'STOP':
                        finish_work = True
                        break      # don't append the sentinel
                    items.append(item)
            except _queue.Empty:
                pass

            for ite in items:
                if ite is None:      # extra safety
                    continue
                # ensure ite is a dict (skip strings)
                if isinstance(ite, str):
                    print("Skipping string item (expected dict):", ite)
                    continue
                try:
                    connect.create_row(ite, "/".join([str(self.base_dir),"dumps"]))
                except Exception as e:
                    print("DB save error:", e)

            if finish_work:
                print("finish pull data")
                return

            time.sleep(0.5)

    
    #def 
    
    def get_url_from_catalog(self, q_catalog_product):
        while True:
            # parsing catalog
            headers = self.update_headers()
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
                                                q_catalog_product.put(str(link_product_page).split())
                                            except:
                                                None
            
            
            #if find Next page disactivate, It is end page.
            for button_dis in buttons_dis:
                if button_dis == 'Next':
                    self.end_page = self.i_page
                    break
            
            print("Catalog page:",self.i_page)
        
        q_catalog_product.put('STOP')
        
    def time_change(self, time_up: bool):
        # thread-safe update of timing based on history
        with self._time_lock:
            step = 0.8 if time_up else -0.2
            change_step = len(self.history_time) / 100.0
            if change_step >= 1.0:
                step_time = step / float(change_step)
                history_el = max(1, int(change_step / 10))
            else:
                step_time = step
                history_el = 5

            all_time_sleep_max = 10.0
            all_time_sleep_min = 0.3

            slice_len = min(len(self.history_time), history_el)
            avg_history = float(np.average(self.history_time[-slice_len:])) if slice_len > 0 else self.time_at_the_moment
            new_time = avg_history + step_time
            # clamp
            new_time = min(all_time_sleep_max, max(all_time_sleep_min, new_time))

            self.time_at_the_moment = new_time
            self.history_time.append(self.time_at_the_moment)


    def _worker_with_retries(self, url):
        max_retries = 2
        base_backoff = 0.5
        jitter = 0.1
        one_retry_flag = False

        for attempt in range(max_retries + 1):
            try:
                headers = self.update_headers()
                result_data, worker_saw_retry = product_page.get_data(url, headers)
                if str(result_data) == 'break':
                    raise ValueError('break')
                one_retry_flag = one_retry_flag or bool(worker_saw_retry)
                return result_data, one_retry_flag
            except Exception:
                if attempt == max_retries:
                    raise
                one_retry_flag = True
                backoff = base_backoff * (2 ** attempt) + random.uniform(0, jitter)
                time.sleep(backoff)


    def get_data_from_product_page(self, q_catalog_product, q_product_database):
        # make unique data
        headers = self.update_headers()
        
        max_workers = 3                 # max workers
        self.time_at_the_moment = 3.0   # Start point time
        self.history_time = [3.0, 3.0, 3.0, 3.0]
        self._time_lock = getattr(self, "_time_lock", threading.Lock()) 

        get_sentinel = False
        while True:
            items = []
            
            try:
                while True:
                    item = q_catalog_product.get(timeout=0.5)
                    if item == 'STOP':
                        get_sentinel = True
                    else:
                        for ite in item:
                            items.append(ite)
            except:
                None
            
            if items != []:
                link_product_pages = items
                unique_link_product_pages = np.unique(link_product_pages)
                link_product_pages = [[str(url.replace("\n","").strip())] for url in unique_link_product_pages]

                futures = {}
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for page_url_ar in link_product_pages:
                        page_url = page_url_ar[0]
                        futures[executor.submit(self._worker_with_retries, page_url)] = page_url

                    # main thread: consume results and apply centralized pacing
                    for fut in tqdm(as_completed(futures), total=len(futures)):
                        src = futures.get(fut, "<unknown>")
                        try:
                            result_data, one_retry = fut.result()  # worker handled retries/backoff
                            if str(result_data) == 'break':
                                raise ValueError("break signal")
                            q_product_database.put(result_data)
                            
                            # update pacing (thread-safe)
                            self.time_change(one_retry)
                        except Exception as e:
                            print(src, e)

                        with self._time_lock:
                            pause = max(0.01, min(1.0, self.time_at_the_moment / 4.0))
                        time.sleep(pause)
            
            if get_sentinel:
                q_product_database.put('STOP')
                
                return

            time.sleep(0.2)

if __name__ == '__main__':
    class_auto_ria = main_auto_ria()
    class_auto_ria.main()