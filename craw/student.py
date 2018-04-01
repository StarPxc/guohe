import datetime
import requests
import time
from bs4 import BeautifulSoup
from util import response_info, static_var_util, db_util, point, xiaoli_util
import re

from util.db_util import md5

static=static_var_util.StaticVar()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    , 'Origin': 'https://vpn.just.edu.cn',
    'Upgrade-Insecure-Requests': '1'
}

def login(username, password):
    session = requests.session()
    cookies = {
                    'lastRealm': 'LDAP-REALM',
                    'DSSIGNIN': 'url_default',
                    'WWHTJIKTLSN_Impl': 'javascript',
                    'DSLastAccess': '1510459958'
                }
    try:
        session.post('http://jwgl.just.edu.cn:8080/jsxsd/xk/LoginToXk', headers=headers, cookies=cookies,
                     data={'USERNAME': username, 'PASSWORD': password}, verify=False)
    except:
        pass
    return  session

def get_score(username,password):
    reg=r'<font color="red">请先登录系统</font>'
    session=login(username,password)
    response=session.get('http://jwgl.just.edu.cn:8080/jsxsd/kscj/cjcx_list')
    if re.findall(reg,response.text):
        response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR,'用户名或密码错误','')
    else:
        th_list = ['order_num', 'start_semester', 'course_num', 'course_name', 'score', 'credit', 'total_hours',
                   'examination_method', 'course_attribute', 'course_nature', 'alternative_course_number',
                   'alternative_course_name', 'mark_of_score']
        data_list=[]
        soup = BeautifulSoup(response.text, "html.parser")
        trs = soup.find_all("tr")[2:]
        is_pingjia = soup.find("table", id='dataList')
        if trs:
            if is_pingjia:  # 判断是否评价
                for tr in trs:
                    tds = tr.find_all("td")
                    i = 0
                    data = {}
                    for td in tds:
                        data[th_list[i]] = td.get_text()
                        i = i + 1
                    data_list.append(data)
                data_list = response_info.success('成绩查询成功', data_list)
                print("成绩查询 " + username)
        return  data_list
def get_grade_point(username,password):
    reg = r'<font color="red">请先登录系统</font>'
    session = login(username, password)
    response = session.get('http://jwgl.just.edu.cn:8080/jsxsd/kscj/cjcx_list')
    if re.findall(reg, response.text):
        return response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '用户名或密码错误','')
    else:
        p = point.Point()
        data=get_score(username,password)
        try:
            if len(data['info']) > 1:
                sum_point = p.get_average_point(data['info'])
                each_list = p.get_each_point(data['info'])
                each_list.insert(0, {'year': 'all', 'point': str(sum_point)})
                # 数据库操作
                result = db_util.get_student_jidian(username)
                each_list = response_info.success('绩点查询成功', each_list)
                if result == 0:
                    jidian = ''
                    for item in each_list['info']:
                        jidian += item['year'] + ':' + item['point'] + '&'
                    db_util.add_student_jidian(jidian, username)
                else:
                    jidian = ''
                    for item in each_list['info']:
                        jidian += item['year'] + ':' + item['point'] + '&'
                    db_util.update_student_jidian(jidian, username)
            else:
                each_list = response_info.error(static.JUST_NO_SCORE,'没有成绩')
        except Exception as e:
            each_list = response_info.error(500, '教务系统异常', "")
            raise

        return each_list
def get_student_info(username,password):
    reg = r'<font color="red">请先登录系统</font>'
    session = login(username, password)
    response = session.get('http://jwgl.just.edu.cn:8080/jsxsd/grxx/xsxx?Ves632DSdyV=NEW_XSD_XJCJ')
    data_list=[]
    if re.findall(reg, response.text):
        return  response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '用户名或密码错误','')
    else:
        try:
            soup = BeautifulSoup(response.text, "html.parser")
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
            data_list = response_info.success('个人信息查询成功', data_list)
            result = db_util.get_student_info(username)
            if result == 0:
                db_util.add_student_info(username, md5(password), name, birthday, temp[1], temp[0], temp[3],
                                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                db_util.update_student_info(password, name, birthday, temp[1], temp[0], temp[3], username,
                                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except:
            data_list=response_info.error(500,'教务系统异常',"")
        return data_list
def get_kb(username,password,semester):
    reg = r'<font color="red">请先登录系统</font>'
    session = login(username, password)
    response = session.get('http://jwgl.just.edu.cn:8080/jsxsd/xskb/xskb_list.do')
    data_list = []
    if re.findall(reg, response.text):
        return response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '用户名或密码错误', '')
    else:
        try:
            url = "http://jwgl.just.edu.cn:8080/jsxsd/xskb/xskb_list.do"
            paramrs = {'zc': '1', 'xnxq01id': semester}
            response = session.get(url, params=paramrs)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            isWeiPingJia=False
            weeks = soup.select("#zc option")
            week_list = []
            for week in weeks:
                week_list.append(week.attrs['value'])
            for item in week_list[1:26]:
                data = kebiaoUtil(session, item, semester)

                if data == '未评价':
                    isWeiPingJia = True
                else:
                    data_list.append({semester + '_' + item: data})
            if isWeiPingJia:
                data_list = response_info.error(static.JUST_NO_EVALUATE, '未评价', '')
            else:
                data_list = response_info.success("所有课表查询成功", data_list)
        except:

            data_list=response_info.error(500,'教务系统异常',"")
            raise
        return data_list
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
def kebiaoUtil(session, week, semester):
    data_list = []
    url = "http://jwgl.just.edu.cn:8080/jsxsd/xskb/xskb_list.do"
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
            data_list.append(data)
        temp = xiaoli_util.kb_date(semester, int(week))
        data_list.append({'month': temp['month'], 'date': temp['date']})
    else:
        data_list = '未评价'
    return data_list

def get_xiaoli():
    url='http://jwc.just.edu.cn/'
    data={}
    try:
        # response = requests.get(url, headers=headers, verify=False)
        # soup = BeautifulSoup(response.text, "html.parser")
        #
        # year = "".join(soup.find('p', class_='da').get_text().split())[:11]
        # currentTab = "".join(soup.find('p', class_='da').get_text().split())[11:]
        # index = soup.find('span', class_='shuzi').get_text()

        data['year']="2017-2018-2"
        tab=datetime.datetime.now().isocalendar()[2]

        currentTab=''
        if tab==1:
            currentTab='星期一'
        if tab==2:
            currentTab='星期二'
        if tab==3:
            currentTab='星期三'
        if tab==4:
            currentTab='星期四'
        if tab==5:
            currentTab='星期五'
        if tab==6:
            currentTab='星期六'
        if tab==7:
            currentTab='星期日'
        data['currentTab']=currentTab
        data['index']=(datetime.datetime.now().isocalendar()[1]-8)%25
        data=response_info.success("校历查询成功",data)
    except Exception as e:

        data=response_info.error(500,'教务系统异常',"")
        raise
    return data
def getSport(username,password):
    session=requests.session()
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

        form_list = []
        info = {}
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('p', attrs={'align': 'center'})
        isSportAccountLoginSuccess = title.find('font', attrs={'size': '3'})
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
        else:
            data_list = response_info.error(static.JUST_SPORT_ACCOUNT_ERROR, '体育学院密码错误', '')

    except Exception as e:
        data_list=response_info.error(500,'教务系统异常',"")
        raise
    return data_list
if __name__ == '__main__':
    print(get_xiaoli())

