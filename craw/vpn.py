import datetime
import hashlib
import logging
import re
import redis
import requests
import time
from bs4 import BeautifulSoup
from util import point, response_info, static_var_util, db_util, xiaoli_util
import threading
static=static_var_util.StaticVar()
lock = threading.Lock()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    , 'Origin': 'https://vpn.just.edu.cn',
    'Upgrade-Insecure-Requests': '1'
}
#用vpn登陆教务处
r= redis.Redis(host='127.0.0.1', port=6379, db=0)
def login(username, password):
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
                try:
                    response = session.post(url=url, data=data, headers=headers, verify=False)
                    if response.text.find('DSIDFormDataStr') != -1:  # 已登录
                        DSIDFormDataStr = \
                        re.findall(r'<input id="DSIDFormDataStr" type="hidden" name="FormDataStr" value="(.*?)">',
                                   response.text)[0]
                        session.post(url=url, data={
                            'btnContinue': '继续会话',
                            'FormDataStr': DSIDFormDataStr
                        })
                        print("已登录")
                    else:
                        print("未登录")
                    html = session.get('https://vpn.just.edu.cn/dana/home/index.cgi', verify=False)
                    if html.text.find('江苏科技大学VPN服务') != -1:  # 登录失败
                        raise Exception("vpn登陆失败，登录账号:{},{}".format('152210702119', '935377012'))
                    session.post('https://vpn.just.edu.cn/jsxsd/xk/,DanaInfo=jwgl.just.edu.cn,Port=8080+LoginToXk',
                                 headers=headers,
                                 data={'USERNAME': username, 'PASSWORD': password}, verify=False)
                except Exception as e:
                    raise Exception("【】未知异常】:{}".format(e))
        return session,vpn_account
    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
    finally:
        # 改完了一定要释放锁:
        lock.release()

    return session,vpn_account

#获取校历 当前日期，当前周，当前学期和所有学期
def xiaoli(username,password):
    local_date=datetime.datetime.now()
    year=str(local_date.year)+'年'+str(local_date.month)+'月'+str(local_date.day)+'日'
    tab = local_date.isocalendar()[2]
    week = ''
    if tab == 1:
        week = '星期一'
    if tab == 2:
        week = '星期二'
    if tab == 3:
        week = '星期三'
    if tab == 4:
        week = '星期四'
    if tab == 5:
        week = '星期五'
    if tab == 6:
        week = '星期六'
    if tab == 7:
        week = '星期日'

    result={'year':year,'all_year':[
        "2018-2019-1",
        "2017-2018-2",
           "2017-2018-1",
              "2016-2017-2",
              "2016-2017-1",
               "2015-2016-2",
               "2015-2016-1",
          ],'week':week,'weekNum':(datetime.datetime.now().isocalendar()[1]-35)}
    data = response_info.success("校历查询成功", result)
    return  data


def vpnScore(username, password):
    session,vpn_account = login(username, password)
    try:
        response = session.get('https://vpn.just.edu.cn/jsxsd/kscj/,DanaInfo=jwgl.just.edu.cn,Port=8080+cjcx_list',
                               headers=headers, verify=False)

        data_list = []
        th_list = ['order_num', 'start_semester', 'course_num', 'course_name', 'score', 'credit', 'total_hours',
                   'examination_method', 'course_attribute', 'course_nature', 'alternative_course_number',
                   'alternative_course_name', 'mark_of_score']
        soup = BeautifulSoup(response.text, "html.parser")
        isVpnLoginSuccess=soup.find('span',class_='cssLarge')
        isAccountLoginSuccess=soup.find('div',class_='dlti')
        if not isVpnLoginSuccess:
            if not isAccountLoginSuccess:
                trs = soup.find_all("tr")[2:]
                is_pingjia=soup.find("table",id='dataList')
                if trs:
                    if is_pingjia:#判断是否评价
                        for tr in trs:
                            tds = tr.find_all("td")
                            i = 0
                            data = {}
                            for td in tds:
                                data[th_list[i]] = td.get_text()
                                i = i + 1
                            data_list.append(data)
                        data_list=response_info.success('成绩查询成功',data_list)
                        print("成绩查询 " + username)
                    else:
                        data_list=response_info.error(static.JUST_NO_EVALUATE,'未评价','')
                else:
                    data_list = response_info.error(static.JUST_NO_SCORE, '没有成绩', '')
            else:
                data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号或密码错误', '')
        else:
            data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
        raise
    finally:
        session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
    return data_list,vpn_account

#绩点查询
def vpnJidian(username, password):
    p = point.Point()
    data,vpn_account = vpnScore(username, password)
    each_list=[]
    try:
        if len(data['info'])>3:
            sum_point = p.get_average_point(data['info'])
            each_list = p.get_each_point(data['info'])
            each_list.insert(0, {'year': 'all', 'point': str(sum_point)})
            # 数据库操作
            result = db_util.get_student_jidian(username)
            each_list = response_info.success('绩点查询成功',each_list)
            if result == 0:
                jidian = ''
                for item in each_list['info']:
                    jidian += item['year'] + ':' + item['point'] + '&'
                db_util.add_student_jidian(jidian,username)
            else:
                jidian = ''
                for item in each_list['info']:
                    jidian += item['year'] + ':' + item['point'] + '&'
                db_util.update_student_jidian(jidian,username)
        else:
            each_list=data
    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
        raise
    return each_list,vpn_account

#当前学期当前周的课表,和切换课表
# def kebiaoBysemesterAndWeek(username,password,semester,week):
#     session, vpn_account = login(username, password)
#     data_list = []
#     try:
#         url = "https://vpn.just.edu.cn/jsxsd/xskb/,DanaInfo=jwgl.just.edu.cn,Port=8080+xskb_list.do"
#         paramrs = {'zc': week, 'xnxq01id': semester}
#         response = session.get(url, params=paramrs)
#         response.encoding = 'utf-8'
#         soup = BeautifulSoup(response.text, "html.parser")
#         isVpnLoginSuccess = soup.find('span', class_='cssLarge')
#         isAccountLoginSuccess = soup.find('div', class_='dlti')
#         if not isVpnLoginSuccess:
#             if not isAccountLoginSuccess:
#                 trs = soup.select("#kbtable tr")
#                 if len(trs) > 3:
#                     del trs[0]
#                     del trs[5]
#                     week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
#                     for tr in trs:
#                         data = {}
#                         tds = tr.select(".kbcontent")
#
#                         for i, td in enumerate(tds):
#                             string = StringUtil(td)
#                             data[week_list[i]] = string
#                         data_list.append(data)
#                     data_list=response_info.success("查询当日课表成功",data_list)
#                 else:
#                     data_list = response_info.error(static.JUST_NO_EVALUATE, '未评价', '')
#             else:
#                 data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号或密码错误', '')
#         else:
#             data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
#     except:
#         r.rpush("vpn_account", vpn_account)
#         raise
#     finally:
#         session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
#     return data_list, vpn_account
# def vpnCurrentKebiao(username,password):
#     temp,vpn_account1=xiaoli(username,password)
#     r.rpush("vpn_account", vpn_account1)
#     if len(temp['info'])>=3:
#         semester = temp['info']['all_year'][0]
#         weekNum = temp['info']['weekNum']
#         session, vpn_account = login(username, password)
#         data_list = []
#         try:
#             url = "https://vpn.just.edu.cn/jsxsd/xskb/,DanaInfo=jwgl.just.edu.cn,Port=8080+xskb_list.do"
#             paramrs = {'zc': weekNum, 'xnxq01id': semester}
#             response = session.get(url, params=paramrs)
#             response.encoding = 'utf-8'
#             soup = BeautifulSoup(response.text, "html.parser")
#             isVpnLoginSuccess = soup.find('span', class_='cssLarge')
#             isAccountLoginSuccess = soup.find('div', class_='dlti')
#             if not isVpnLoginSuccess:
#                 if not isAccountLoginSuccess:
#                     trs = soup.select("#kbtable tr")
#                     if len(trs) > 3:
#                         del trs[0]
#                         del trs[5]
#                         week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
#                         for tr in trs:
#                             data = {}
#                             tds = tr.select(".kbcontent")
#                             for i, td in enumerate(tds):
#                                 string = StringUtil(td)
#                                 data[week_list[i]] = string
#                             data_list.append(data)
#                         data_list = response_info.success("查询当前课表成功", data_list)
#                     else:
#                         data_list = response_info.error(static.JUST_NO_EVALUATE, '未评价', '')
#                 else:
#                     data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号或密码错误', '')
#             else:
#                 data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
#         except:
#             r.rpush("vpn_account", vpn_account)
#             raise
#         finally:
#             session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
#         return data_list,vpn_account
#     else:
#         data_list=temp
#         return data_list,''

def VpnGetSport(username,password):
    lock.acquire()
    session = requests.session()
    vpn_account = {}
    try:
        flag = True
        while flag:
            time.sleep(0.5)
            if r.lrange('vpn_account', 0, -1):  # 若缓存中没有账号则等待
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

        sport_data = {
            'chkuser': 'true',
            'username': username,
            'password': password
        }
        session.get('https://vpn.just.edu.cn/,DanaInfo=tyb.just.edu.cn+', headers=headers, verify=False)
        session.post('https://vpn.just.edu.cn/,DanaInfo=202.195.195.147+index1.asp', headers=headers, data=sport_data,
                     verify=False)
        response = session.get('https://vpn.just.edu.cn/zcgl/,DanaInfo=202.195.195.147+xskwcx.asp?action=jlbcx',
                               headers=headers, verify=False)
        response.encoding = 'gb2312'
        data_list = []
        form_list = []
        info = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        isVpnLoginSuccess = soup.find('span', class_='cssLarge')
        if not isVpnLoginSuccess:
            title = soup.find('p', attrs={'align': 'center'})
            isSportAccountLoginSuccess = title.find('font', attrs={'size': '3'})
            if not isSportAccountLoginSuccess:
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
                    if len(tds[1].text.split(" ")) > 2:
                        data['date'] = tds[1].text.split(" ")[0] + tds[1].text.split(" ")[1] + " " + \
                                       tds[1].text.split(" ")[2]
                    else:
                        data['date'] = tds[1].text
                    data['time'] = tds[2].text
                    form_list.append(data)
                total = trs[-1].text
                temp = ''
                for item in total.split("\r\n")[1:]:
                    temp = temp + item.strip() + '\r\n'
                info['total'] = temp
                info['sum'] = total.split("\r\n")[0]
                data_list.append(info)
                data_list.append(form_list)
                data_list=response_info.success("俱乐部查询成功",data_list)
            elif isSportAccountLoginSuccess.string=="很抱歉，数据库中没有相关信息！":
                data_list = response_info.error(static.JUST_SPORT_NO_DATA, '很抱歉，数据库中没有相关信息！', '')

            else:
                data_list = response_info.error(static.JUST_SPORT_ACCOUNT_ERROR, '体育学院密码错误', '')
        else:
            data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
        raise
    finally:
        session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
        lock.release()
    return data_list,vpn_account

def vpnGetClassrooms(username,password,school_year,area_id,building_id,zc1):
   session,vpn_account = login(username, password)
   try:
       zc2=int(zc1)+1
       str_zc2=str(zc2)
       classroom_data = {
           'xnxqh': school_year,
           'skyx': '',
           'xqid': area_id,
           'jzwid': building_id,
           'zc1': zc1,
           'zc2': str_zc2,
           'jc1': '',
           'jc2': ''
       }
       response = session.post(
           'https://vpn.just.edu.cn/jsxsd/kbcx/,DanaInfo=jwgl.just.edu.cn,Port=8080+kbxx_classroom_ifr',
           data=classroom_data,
           headers=headers, verify=False)
       data_list = []
       soup = BeautifulSoup(response.text, 'html.parser')
       isVpnLoginSuccess = soup.find('span', class_='cssLarge')
       isAccountLoginSuccess = soup.find('div', class_='dlti')
       if not isVpnLoginSuccess:
           if not isAccountLoginSuccess:
               trs = soup.find_all("tr")
               for tr in trs[2:]:
                   tds = tr.find_all('td')
                   i = -1
                   for td in tds:
                       i = i + 1
                       data = {}
                       if '\r' in td.text:
                           data['place'] = tr.find_all('td')[0].text
                           data['time'] = trs[1].find_all('td')[i].text
                           if i >= 1 and i <= 5:
                               data['weekday'] = 'Mon'
                           elif i >= 6 and i <= 10:
                               data['weekday'] = 'Tue'
                           elif i >= 11 and i <= 15:
                               data['weekday'] = 'Wedn'
                           elif i >= 16 and i <= 20:
                               data['weekday'] = 'Thur'
                           elif i > 21 and i <= 25:
                               data['weekday'] = 'Fri'
                           elif i >= 26 and i <= 30:
                               data['weekday'] = 'Sat'
                           else:
                               data['weekday'] = 'Sun'
                           data_list.append(data)
               data_list = response_info.success("空教室查询成功", data_list)
           else:
               data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号或密码错误', '')
       else:
           data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)

   except Exception as e:
       logging.exception(e)
       r.rpush("vpn_account", vpn_account)
       raise
   finally:
       session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
   return data_list,vpn_account

def vpnKebiao(username, password, semester):
    session,vpn_account = login(username, password)
    data_list = []
    try:
        url = "https://vpn.just.edu.cn/jsxsd/xskb/,DanaInfo=jwgl.just.edu.cn,Port=8080+xskb_list.do"
        paramrs = {'zc': '1', 'xnxq01id': semester}
        response = session.get(url, params=paramrs)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        isVpnLoginSuccess = soup.find('span', class_='cssLarge')
        isAccountLoginSuccess = soup.find('div', class_='dlti')
        isWeiPingJia=False
        if not isVpnLoginSuccess:
            if not isAccountLoginSuccess:
                weeks = soup.select("#zc option")
                week_list = []
                for week in weeks:
                    week_list.append(week.attrs['value'])
                for item in week_list[1:21]:
                    data = kebiaoUtil(session, item, semester)
                    if data=='未评价':
                        isWeiPingJia=True
                    else:
                        data_list.append({semester + '_' + item: data})
                        #db_util.add_kb(semester + '_' + item,data)
                if isWeiPingJia:
                    data_list = response_info.error(static.JUST_NO_EVALUATE, '未评价', '')
                else:
                    data_list=response_info.success("所有课表查询成功",data_list)
            else:
                data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号或密码错误', '')
        else:
            data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
        raise
    finally:
        session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
    print("课表查询" + username + ' ' + semester)
    return data_list,vpn_account

def get_all_kb(username, password, semester):
    session,vpn_account = login(username, password)
    data_list = []
    try:
        url = "https://vpn.just.edu.cn/jsxsd/xskb/,DanaInfo=jwgl.just.edu.cn,Port=8080+xskb_list.do"
        paramrs = {'zc': '', 'xnxq01id': semester}
        response = session.get(url, params=paramrs)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        isVpnLoginSuccess = soup.find('span', class_='cssLarge')
        isAccountLoginSuccess = soup.find('div', class_='dlti')
        isWeiPingJia=False
        if not isVpnLoginSuccess:
            if not isAccountLoginSuccess:
                week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                trs = soup.select("#kbtable tr")
                data_list = []

                for tr in trs[1:]:

                    data = {}
                    for i, td in enumerate(tr.select(".kbcontent")):
                        data[week_list[i]] = StringUtilALl(td)
                    data_list.append(data)

                if isWeiPingJia:
                    data_list = response_info.error(static.JUST_NO_EVALUATE, '未评价', '')
                else:
                    data_list=response_info.success("所有课表查询成功",data_list)
            else:
                data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号或密码错误', '')
        else:
            data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
        raise
    finally:
        session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
    print("课表查询" + username + ' ' + semester)
    print(data_list)
    return data_list,vpn_account
def StringUtilALl(td):
    items = str(td).split('---------------------')

    result = ''
    for i, item in enumerate(items):

        reg = '(<br\/>|.*style="display: none;">)(.*?)(<br\/>|<br>)(.*?)<br\/><font title="老师">(.*?)<\/font><br\/><font title="周次\(节次\)">(.*?)<\/font><br\/>'
        re_result = re.findall(reg, item)
        if len(re_result) == 0:  # 没课
            return ''
        class_num = re_result[0][1]
        class_name = re_result[0][3]
        class_teacher = re_result[0][4]
        class_week = re_result[0][5]
        resultItem = class_num + '@' + class_name + '@' + class_teacher + "@" + class_week
        reg_class = '<font title="教室">(.*?)</font>'
        if len(re.findall(reg_class, item)) != 0:
            resultItem = resultItem + '@' + re.findall(reg_class, item)[0]
        result=result+resultItem
        if i!=len(items)-1:
            result = result + '---------------------'

    return result
def kebiaoUtil(session, week, semester):
    data_list = []
    url = "https://vpn.just.edu.cn/jsxsd/xskb/,DanaInfo=jwgl.just.edu.cn,Port=8080+xskb_list.do"
    paramrs = {'zc': week, 'xnxq01id': semester}
    response = session.get(url, params=paramrs)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    trs = soup.select("#kbtable tr")
    if len(trs) > 3:
        del trs[0]
        del trs[5]
        week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for tr in trs:
            data = {}
            tds = tr.select(".kbcontent")
            for i, td in enumerate(tds):
                string=StringUtil(td)
                data[week_list[i]] =string
                temp = xiaoli_util.kb_date(semester, int(week))
            data_list.append(data)
        temp = xiaoli_util.kb_date(semester, int(week))
        data_list.append({'month': temp['month'],'date':temp['date']})
    else:
        data_list = '未评价'
    return data_list

def md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()

#获取学生基本信息
def vpnInfo(username, password):
    session,vpn_account = login(username, password)
    data_list = []
    try:
        response = session.get('https://vpn.just.edu.cn/jsxsd/grxx/,DanaInfo=jwgl.just.edu.cn,Port=8080+xsxx',
                               headers=headers, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        isVpnLoginSuccess = soup.find('span', class_='cssLarge')
        isAccountLoginSuccess = soup.find('div', class_='dlti')
        if not isVpnLoginSuccess:
            if not isAccountLoginSuccess:
                temp = []
                trs = soup.select("#xjkpTable tr")
                name = "".join((trs[3].select('td')[1].get_text()).split())
                birthday = "".join((trs[4].select('td')[1].get_text()).split())
                tds = trs[2].select('td')
                for td in tds:
                    temp.append(td.get_text()[3:])
                data_list = {"academy": temp[0], "major": temp[1], "class_num": temp[3], "name": name,
                             "birthday": birthday,
                             'username': username, 'password': password}
                data_list=response_info.success('个人信息查询成功',data_list)
                result =db_util.get_student_info(username)
                if result == 0:
                    db_util.add_student_info(username, md5(password), name, birthday, temp[1], temp[0], temp[3],datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    db_util.update_student_info(password, name, birthday, temp[1], temp[0], temp[3], username,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号或密码错误', '')
        else:
            data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
    except Exception as e:
        logging.exception(e)
        r.rpush("vpn_account", vpn_account)
        raise
    finally:
        session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers=headers, verify=False)
    return data_list, vpn_account

def StringUtil(td):
    class_teacher=td.select('font[title="老师"]')
    class_address=td.select('font[title="教室"]')
    class_week = td.select('font[title="周次(节次)"]')
    if len(class_week) > 0:
        class_week = class_week[0].text
    else:
        class_week = ''
    if len(class_teacher)>0:
        class_teacher=class_teacher[0].text
    else:
        class_teacher=''
    if len(class_address) > 0:
        class_address = class_address[0].text
    else:
        class_address = ''
    class_num=str(td).split(r">")
    if class_num:
        class_num=class_num[1].split(r"<")[0]
    else:
        class_num=''
    class_name = str(td).split(r"<br/>")
    if len(class_name)>1:
        class_name = class_name[1]
    else:
        class_name = ''
    result=''
    if class_num and class_name and class_teacher and class_address:
        result=class_num+'@'+class_name+'@'+class_teacher+'@'+class_address
    elif class_num and class_name and class_teacher:
        result = class_num+'@'+class_name + '@' + class_teacher
    else:
        result=''
    return result
def IsChinese(str):
    if str >= '\u4e00' and str<= '\u9fa5':
        return True
    else:
        return False

if __name__ == '__main__':
  print(get_all_kb('152210702119','935377012pxc','2017-2018-2'))
