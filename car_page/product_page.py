# parsing
import requests
from lxml import html

# work with data
import json
import re

# for test work
try:
    import phone_json
except:
    from car_page import phone_json
    
# time
import time
import random

from pprint import pprint

def get_data(url_get,headers):
    url = str(url_get).strip()
    car_vim = None
    data = {
        'url':url
        , 'title': None
        , 'price_usd' : None
        , 'odometer' : None
        , 'username' : None
        , 'phone_number' : None
        , 'image_url' : None
        , 'images_count' : 0
        , 'car_number' : None
        , 'car_vim' : None
    }

    # preparing instruments
    phone_number = None
    one_retry = False
    fast_return = False
    dolar = False
    images = []
    headers["Cookie"]='Path=/; ab_redesign=1; ab_test_new_pages=1; chk=1; ui=d97ff2002e387632; PHPLOGINSESSID=p37mu2plcdc7efpc0t79lavsk3; project_id=2; project_base_url=https://auto.ria.com/iframe-ria-login; showNewFeatures=7; _504c2=http://10.42.2.152:3000; gdpr=[]; bffState={}; slonik_utm_campaign=autoforzsu1; slonik_utm_medium=message; slonik_utm_source=main_page; PHPSESSID=eyJ3ZWJTZXNzaW9uQXZhaWxhYmxlIjp0cnVlLCJ3ZWJQZXJzb25JZCI6MCwid2ViQ2xpZW50SWQiOjM2NDkwNDA4OTYsIndlYkNsaWVudENvZGUiOjc3NTQ1MjIxMCwid2ViQ2xpZW50Q29va2llIjoiZDk3ZmYyMDAyZTM4NzYzMiIsIl9leHBpcmUiOjE3NjYxMzQzMzIwODIsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; extendedSearch=1; informerIndex=1; g_state={"i_l":0,"i_ll":1766083440692,"i_b":"XjCU8wi2Uy/XDFHLadrCIhzkLOB3kKHQigxpahrzJPA","i_e":{"enable_itp_optimization":0}}'
    headers["accept-language"] = "uk,en-US;q=0.9,en;q=0.8,ru;q=0.7"

    # __cpo=aHR0cHM6Ly9hdXRvLnJpYS5jb20 must be
    payload = "".join([f"__cpo=aHR",str(random.randrange(0,9)),chr(random.randint(97, 122)),"HM",str(random.randrange(0,9)),"Ly",str(random.randrange(0,9)),"hdXRvLnJpYS",str(random.randrange(0,9)),chr(random.randint(97, 122)),chr(random.randint(97, 122)),str(random.randrange(0,9)),str(random.randrange(0,9))])
    url_req = "".join([url,"?",payload])
    
    # try_parsing
    response = requests.get(url_req,headers=headers, data = json.dumps(payload))

    page_product = html.fromstring(response.content)
    
    if str(response) == "<Response [429]>":
        time.sleep(1)
        response = requests.get(url_req,headers=headers,data = json.dumps(payload))
        page_product = html.fromstring(response.content)
        one_retry = True
        if str(response) == "<Response [429]>":
            print("<Response [429]>")
            return 'break'
        
    script_content = page_product.xpath('//script[contains(text(), "__PINIA__")]/text()')
    all_json_item = json.loads(";".join(str(script_content[0]).split('window.__PINIA__ = ')[1].split(";")[:-1]))

    # code_next = "".join([str(url).replace(" ","").replace("https://auto.ria.com",""),"/"])
    # code_next_get=code_next.replace("-","_").strip()
    for key in all_json_item["page"]["structures"].keys():
        templates = all_json_item["page"]["structures"][key]["templates"]
        # page
        for template in templates:
            if template['id'] == 'bannerStatus':
                second_templates = template['templates']
                for second_template in second_templates:
                    if second_template['id'] == 'bannerStatusRow':
                        thierd_templates = template['templates']
                        for thierd_template in thierd_templates:
                            forth_templates = thierd_template['templates']
                            for forth_template in forth_templates:
                                if forth_template['id'] == 'bannerStatusText':
                                    try:
                                        elements = forth_template['elements']
                                        for element in elements:
                                            # It is mean don't have car info
                                            if element['content'] == 'видалене і не бере участі в пошуку':
                                                fast_return = True
                                            elif element['typography'] == 'titleS':
                                                name_car = element['content']
                                        if fast_return:
                                            data['title'] = name_car
                                            return data, one_retry
                                    except:
                                        None
                                
            if template['id'] == 'main':
                second_templates = template['templates']
                for second_template in second_templates:
                    third_templates = second_template['templates']
                    for third_template in third_templates:
                        # get images
                        try:
                            elements =  third_template["elements"]
                            for element in elements:
                                if element['type'] == "Image":
                                    images.append(element['formats']["fullHD"])
                        except:
                            None
                    
                        # Get vim
                        if third_template["id"] == "badges":
                            frouth_templates = third_template["templates"]
                            try:
                                for frouth_template in frouth_templates:   
                                    second_temps = temp["templates"]
                                    for second_temp in second_temps:
                                        elemens = second_temp["elements"]
                                        
                                        for elemen in elemens:
                                            if elemen['type'] == "Text":
                                                car_vim = elemen['content']
                            except Exception as e:
                                frouth_templates = third_template["templates"]
                                
                                for frouth_template in frouth_templates:
                                    
                                    if frouth_template['id'] == 'badgesVinGrid':
                                        #pprint(frouth_template)
                                        fifth_templates = frouth_template['templates']
                                        for fifth_template in fifth_templates:

                                            try:
                                                elemens = fifth_template['elements']
                                                for elemen in elemens:
                                                    car_vim = elemen['actionData']['copy']
                                            except:
                                                None

                        
                        # Get price
                        if second_template["id"] == "col":
                            templatets = second_template['templates']
                            for templatet in templatets:
                                if templatet["id"] == "basicInfo":
                                    second_templatets = templatet['templates']
                                    for second_templatet in second_templatets:
                                        if second_templatet["id"] == "basicInfoPriceRow":
                                            third_templatets = second_templatet["templates"]
                                            for third_templatet in third_templatets:
                                                if third_templatet['id'] == "basicInfoPriceWrapText":
                                                    fouth_templatets = third_templatet["templates"]
                                                    for fouth_templatet in fouth_templatets:
                                                        elements = fouth_templatet['elements']
                                                        try:
                                                            for element in elements:
                                                                if (dolar == False):
                                                                    price = element["content"]
                                                                    price_dolar = price.replace("$","")
                                                                    if price_dolar != price:
                                                                        result_price_dolar = "".join(re.findall(r'\d+',price_dolar))
                                                                        dolar=True
                                                        except:
                                                            None

                                        # odometer
                                        if second_templatet["id"] == "basicInfoTableMainInfo":
                                            row_templates = second_templatet["templates"]
                                            for row_template in row_templates:
                                                if row_template["id"] == "basicInfoTableMainInfoInfo":
                                                    try:
                                                        second_row_templates = row_template['templates']
                                                        for second_row_template in second_row_templates:
                                                            elements = second_row_template['elements']
                                                            if elements[0]["style"] == "ic_16_speedometer":
                                                                drive = elements[1]["content"]
                                                                drive = "".join(re.findall(r"\d+",drive.replace("тис.","000")))
                                                    except:
                                                        None
                                                                    
                        # payload
                        if third_template["id"]=="photoSlider":                       
                            buttons = third_template['component']['photoSlider']["callToAction"]["buttons"]
                            for button in buttons:
                                if button['id'] == 'autoPhone':
                                    json_payload = button['actionData']

        # Title
        title = json_payload['params']['title']

        # User Name
        user_name = json_payload['params']['userName']
        if user_name == 'Ім`я не вказане':
            user_name = None
        
        # Car id
        autoid = json_payload['autoId']
        try: 
            len_images = len(images)
        except:
            len_images = 0

        data['title']=title
        data['price_usd']=result_price_dolar
        data['odometer']=drive
        data['username']=user_name
        data['phone_number']=None
        data['image_url']=images
        data['images_count']=len_images
        data['car_number']=autoid
        data['car_vim']=car_vim

        
        # Try get number telephone
        sold_car = False
        for have_car in page_product.xpath('//main/div/div/div/div/div/div/div/text()'):
            if have_car == 'Авто продане':
                sold_car = True
        if sold_car == False:   
            # Need add default items
            json_payload['params']["target"]= {}
            json_payload['params']["formId"]= 'null'
            json_payload['params']["langId"]= 4
            json_payload['params']["device"]= "desktop-web"
            headers["content-type"]="application/json"
            try:
                phone_number = phone_json.get_data_json(headers,json_payload)
                if phone_number == None:
                    time.sleep(1)
                    phone_number = phone_json.get_data_json(headers,json_payload)
            except:
                try:
                    time.sleep(1)
                    phone_number = phone_json.get_data_json(headers,json_payload)
                except:
                    None

            data['phone_number'] = phone_number 
        return data, one_retry
    
if __name__ == "__main__":
    # url = "https://auto.ria.com/uk/auto_renault_trafic_38644737.html"
    url = "https://auto.ria.com/uk/auto_audi_q7_39237458.html"
    # url = "https://auto.ria.com/uk/auto_bmw_5-series_39266704.html"

    headers = {
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Cookie":"""Path=/; ab_redesign=1; ab_test_new_pages=1; chk=1; ui=d97ff2002e387632; PHPSESSID=eyJ3ZWJTZXNzaW9uQXZhaWxhYmxlIjp0cnVlLCJ3ZWJQZXJzb25JZCI6MCwid2ViQ2xpZW50SWQiOjM2NDkwNDA4OTYsIndlYkNsaWVudENvZGUiOjc3NTQ1MjIxMCwid2ViQ2xpZW50Q29va2llIjoiZDk3ZmYyMDAyZTM4NzYzMiIsIl9leHBpcmUiOjE3NjYwNDMxMDk2NTMsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; PHPLOGINSESSID=p37mu2plcdc7efpc0t79lavsk3; project_id=2; project_base_url=https://auto.ria.com/iframe-ria-login; showNewFeatures=7; _504c2=http://10.42.2.152:3000; gdpr=[]; bffState={}; slonik_utm_campaign=autoforzsu1; slonik_utm_medium=message; slonik_utm_source=main_page; g_state={"i_l":0,"i_ll":1766002028347,"i_b":"cx0fqTOTawRixicxFkwTHzlovF0XET1ib5aGLV7dXzo","i_e":{"enable_itp_optimization":0}}""",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(get_data(url, headers))