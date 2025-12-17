import requests
from lxml import html
import json
from pprint import pprint

def get_data_payload(url,headers):
    response = requests.get(url,headers=headers)
    page_product = html.fromstring(response.content)
    script_content = page_product.xpath('//script[contains(text(), "__PINIA__")]/text()')
    make_split = ["callToAction","buttons",'"actionData":']
    for make_sp in make_split:
        script_content = str(script_content).split(make_sp)[1]
    json_payload = json.loads(script_content.split(',"elements"')[0])
    # Need add elements
    json_payload['params']["target"]= {}
    json_payload['params']["formId"]= 'null'
    json_payload['params']["langId"]= 4
    json_payload['params']["device"]= "desktop-web"
    return json_payload

if __name__ == "__main__":
    url = "https://auto.ria.com/uk/auto_kia_niro_39232724.html"
    headers = {
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Cookie":"""Path=/; ab_redesign=1; ab_test_new_pages=1; chk=1; ui=d97ff2002e387632; PHPSESSID=eyJ3ZWJTZXNzaW9uQXZhaWxhYmxlIjp0cnVlLCJ3ZWJQZXJzb25JZCI6MCwid2ViQ2xpZW50SWQiOjM2NDkwNDA4OTYsIndlYkNsaWVudENvZGUiOjc3NTQ1MjIxMCwid2ViQ2xpZW50Q29va2llIjoiZDk3ZmYyMDAyZTM4NzYzMiIsIl9leHBpcmUiOjE3NjYwNDMxMDk2NTMsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; PHPLOGINSESSID=p37mu2plcdc7efpc0t79lavsk3; project_id=2; project_base_url=https://auto.ria.com/iframe-ria-login; showNewFeatures=7; _504c2=http://10.42.2.152:3000; gdpr=[]; bffState={}; slonik_utm_campaign=autoforzsu1; slonik_utm_medium=message; slonik_utm_source=main_page; g_state={"i_l":0,"i_ll":1766002028347,"i_b":"cx0fqTOTawRixicxFkwTHzlovF0XET1ib5aGLV7dXzo","i_e":{"enable_itp_optimization":0}}""",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(get_data_payload(url, headers))