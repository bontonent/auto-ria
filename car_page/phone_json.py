# parsing
import requests
from lxml import html

# work with json
import json

# get number telephone
def get_data_json(headers,payload):
    # every time same(change only payload)
    url = 'https://auto.ria.com/bff/final-page/public/auto/popUp/'
    response = requests.post(url,headers = headers,data=json.dumps(payload))
    json_page = response.json()

    # Get phone number
    templates = json_page['templates']
    for template in templates:
        if template['id'] == 'autoPhoneCallRequest':
            
            datas = template['actionData']['data']
            for data in datas:
                if data[0] == 'phone':
                    telephone = data[1]
                    telephone = int("".join(["380",str(telephone)]))
    return telephone

# test work
if __name__ == "__main__":
    payload = {'blockId': 'autoPhone', 'popUpId': 'autoPhone', 'isLoginRequired': False, 'isConfirmPhoneEmailRequired': False, 'autoId': 39232724, 'data': [['userId', '3916367'], ['phoneId', '676623426'], ['title', 'Kia Niro 2020'], ['isCheckedVin', ''], ['companyId', ''], ['companyEng', ''], ['avatar', 'https://cdn.riastatic.com/photos/avatars/all/391/39163/3916367/3916367l.jpg'], ['userName', 'Сергій Станіславович'], ['isCardPayer', '1'], ['dia', ''], ['isOnline', ''], ['isCompany', ''], ['workTime', ''], ['srcAnalytic', 'main_col_photoSlider_autoPhone_showBottomPopUp']], 'params': {'userId': '3916367', 'phoneId': '676623426', 'title': 'Kia Niro 2020', 'isCheckedVin': '', 'companyId': '', 'companyEng': '', 'avatar': 'https://cdn.riastatic.com/photos/avatars/all/391/39163/3916367/3916367l.jpg', 'userName': 'Сергій Станіславович', 'isCardPayer': '1', 'dia': '', 'isOnline': '', 'isCompany': '', 'workTime': '', 'target': {}, 'formId': 'null', 'langId': 4, 'device': 'desktop-web'}}
    headers = {
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Cookie":"""ab_redesign=1; ab_test_new_pages=1; chk=1; ui=d97ff2002e387632; PHPSESSID=eyJ3ZWJTZXNzaW9uQXZhaWxhYmxlIjp0cnVlLCJ3ZWJQZXJzb25JZCI6MCwid2ViQ2xpZW50SWQiOjM2NDkwNDA4OTYsIndlYkNsaWVudENvZGUiOjc3NTQ1MjIxMCwid2ViQ2xpZW50Q29va2llIjoiZDk3ZmYyMDAyZTM4NzYzMiIsIl9leHBpcmUiOjE3NjYwNDMxMDk2NTMsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; PHPLOGINSESSID=p37mu2plcdc7efpc0t79lavsk3; project_id=2; project_base_url=https://auto.ria.com/iframe-ria-login; showNewFeatures=7; _504c2=http://10.42.2.152:3000; gdpr=[]; bffState={}; slonik_utm_campaign=autoforzsu1; slonik_utm_medium=message; slonik_utm_source=main_page; g_state={"i_l":0,"i_ll":1766004790344,"i_b":"cx0fqTOTawRixicxFkwTHzlovF0XET1ib5aGLV7dXzo","i_e":{"enable_itp_optimization":0}}""",
        "content-type":"application/json"
    }
    answer = get_data_json(headers,payload)
    print(answer)

