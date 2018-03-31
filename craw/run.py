import logging

import redis
import requests
from bs4 import BeautifulSoup
from util import point, response_info, static_var_util, db_util
static=static_var_util.StaticVar()

import time
import threading

lock = threading.Lock()
r= redis.Redis(host='127.0.0.1', port=6379, db=0)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    , 'Origin': 'https://vpn.just.edu.cn',
    'Upgrade-Insecure-Requests': '1'
}


def login():
    lock.acquire()
    session = requests.session()
    vpn_account={}
    try:
        flag = True
        while flag:
            time.sleep(0.5)
            if r.lrange('vpn_account', 0, -1):#若缓存中没有账号则等待
                flag = False
                vpn_account = eval(r.lpop('vpn_account'))
                url = "https://vpn.just.edu.cn/dana-na/auth/url_default/login.cgi"
                data = {
                    'tz_offset': '480',
                    'username': vpn_account['username'],
                    'password': vpn_account['password'],
                    'realm': 'LDAP-REALM',
                    'btnSubmit': '登录'
                }
                cookies = {
                    'lastRealm': 'LDAP-REALM',
                    'DSSIGNIN': 'url_default',
                    'WWHTJIKTLSN_Impl': 'javascript',
                    'DSLastAccess': '1510459958'

                }
                session.post(url=url, data=data, cookies=cookies, headers=headers, verify=False)
                session.get('https://vpn.just.edu.cn/,DanaInfo=jwgl.just.edu.cn,Port=8080+', verify=False)
    except Exception as e:
        logging.exception(e)
    finally:
        # 改完了一定要释放锁:
        lock.release()
    return session,vpn_account

def getSport(username,password):
    session,vpn_account=login()
    data_list = []
    try:
        sport_data = {

            'chkuser': 'true',
            'username': username,
            'password': password
        }
        session.post('https://vpn.just.edu.cn/,DanaInfo=202.195.195.147+index1.asp', headers=headers, data=sport_data,
                     verify=False)
        response = session.get('https://vpn.just.edu.cn/zcgl/,DanaInfo=202.195.195.147+xskwcx.asp?action=zccx',
                               headers=headers, verify=False)
        response.encoding = 'gb2312'
        # print (response.text)

        form_list = []
        info = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        isVpnLoginSuccess = soup.find('span', class_='cssLarge')
        if not isVpnLoginSuccess:
            title = soup.find('p', attrs={'align': 'center'})
            isSportAccountLoginSuccess = title.find('font', attrs={'size': '3'})

            print(isSportAccountLoginSuccess.string)

            if not isSportAccountLoginSuccess:
                title = soup.find('p', attrs={'align': 'center'})
                name = title.find('font', attrs={'size': '6'}).text
                info['name'] = name
                year = title.find('font', attrs={'size': '4'}).text
                info['year'] = year
                form = soup.find('form')
                trs = form.find_all('tr')
                for tr in trs[1:-1]:
                    data = {}
                    tds = tr.find_all('td')
                    data['number'] = tds[0].text
                    data['date'] = tds[1].text
                    data['time'] = tds[2].text
                    form_list.append(data)
                total = trs[-1].text
                info['total'] = total
                data_list.append(info)
                data_list.append(form_list)
                data_list = response_info.success("早操查询成功", data_list)
                #通过一个模糊比较

            elif isSportAccountLoginSuccess.string=="很抱歉，数据库中没有相关信息！":
                data_list = response_info.error(static.JUST_SPORT_NO_DATA, '很抱歉，数据库中没有相关信息！', '')
            else:
                data_list = response_info.error(static.JUST_SPORT_ACCOUNT_ERROR, '体育学院密码错误', '')
        else:
            data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)

    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
    finally:
        session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
    return data_list,vpn_account





if __name__ == '__main__':
    s=getSport('152210702119','PXC')
    print (s)
