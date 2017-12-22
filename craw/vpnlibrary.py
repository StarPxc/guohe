import redis
import requests
from bs4 import BeautifulSoup
from util import point, response_info, static_var_util, db_util
import time
import threading
import random
static=static_var_util.StaticVar()

lock = threading.Lock()
r = redis.Redis(host='127.0.0.1', port=6379, db=0)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    , 'Origin': 'https://vpn.just.edu.cn',
    'Upgrade-Insecure-Requests': '1'
}


class Proxy():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Origin': 'https://vpn.just.edu.cn',
            'Upgrade-Insecure-Requests': '1'
        }

    def login(self):
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

        except:
            r.rpush("vpn_account", vpn_account)
        finally:
            # 改完了一定要释放锁:
            lock.release()
        return session, vpn_account


class HotBook():
    def __init__(self):
        self.data_list = []
        self.hot_borrow_list = []
        self.hot_books_list = []

    def getHotBook(self):
        p = Proxy()
        session,vpn_account = p.login()
        try:
            result = session.get('https://vpn.just.edu.cn/opac/,DanaInfo=lib.just.edu.cn,Port=8080+top100.php',
                                 headers={
                                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                                     'Origin': 'https://vpn.just.edu.cn',
                                     'Upgrade-Insecure-Requests': '1'
                                 }, verify=False)
            result.encoding = 'utf-8'
            #print (result.text)
            soup = BeautifulSoup(result.content, 'html.parser')
            isVpnLoginSuccess = soup.find('span', class_='cssLarge')
            isAccountLoginSuccess = soup.find('div', class_='dlti')
            hot_borrow_li = soup.find_all('td')
            hot_borrow_name = []
            hot_borrow_url = []
            hot_books_name = []
            hot_books_url = []
            if not isVpnLoginSuccess:
                if not isAccountLoginSuccess:
                    for li in hot_borrow_li[0:10]:
                        hot_borrow_name.append(li.text)
                    self.data_list.append(hot_borrow_name)
                    self.data_list=response_info.success("热门搜索词查询成功",self.data_list)
                else:
                    self.data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号错误', '')
            else:
                self.data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)
        except:
            r.rpush("vpn_account", vpn_account)
            raise
        finally:
            session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Origin': 'https://vpn.just.edu.cn',
                'Upgrade-Insecure-Requests': '1'
            }, verify=False)
        return self.data_list, vpn_account


class BookItem():
    def __init__(self):
        self.book_dt = []
        self.book_dd = []
        self.book_name = ''
        self.book_author = ''
        self.book_press = ''
        self.book_isbn = ''
        self.book_type = ''
        self.book_outline = ''
        self.book_info_content = {}
        self.book_borrow_content = {}

    def getBook(self, url):
        p = Proxy()
        session, vpn_account = p.login()
        try:
            result = session.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Origin': 'https://vpn.just.edu.cn',
                'Upgrade-Insecure-Requests': '1'
            }, verify=False)
            result.encoding = "utf-8"
            soup = BeautifulSoup(result.content, 'html.parser')
            isVpnLoginSuccess = soup.find('span', class_='cssLarge')
            isAccountLoginSuccess = soup.find('div', class_='dlti')
            if not isVpnLoginSuccess:
                if not isAccountLoginSuccess:
                    book_content = soup.find_all('dl', attrs={"class": 'booklist'})
                    for book_info in book_content:
                        self.book_dt.append(book_info.find("dt").text)
                        self.book_dd.append(book_info.find("dd").text)
                    if "题名/责任者:" in self.book_dt:
                        index1 = self.book_dt.index("题名/责任者:")
                        self.book_name = self.book_dd[index1]
                    if "个人责任者:" in self.book_dt:
                        index2 = self.book_dt.index("个人责任者:")
                        self.book_author = self.book_dd[index2]
                    if "出版发行项:" in self.book_dt:
                        index3 = self.book_dt.index("出版发行项:")
                        self.book_press = self.book_dd[index3]
                    if "ISBN及定价:" in self.book_dt:
                        index4 = self.book_dt.index("ISBN及定价:")
                        self.book_isbn = self.book_dd[index4]
                    if "学科主题:" in self.book_dt:
                        index5 = self.book_dt.index("学科主题:")
                        self.book_type = self.book_dd[index5]
                    if "提要文摘附注:" in self.book_dt:
                        index6 = self.book_dt.index("提要文摘附注:")
                        self.book_outline = self.book_dd[index6]
                    self.book_info_content = {"book_name": self.book_name,
                                              "book_author": self.book_author,
                                              "book_press": self.book_press,
                                              "book_isbn": self.book_isbn,
                                              "book_type": self.book_type,
                                              "book_outline": self.book_outline}
                    # print (self.book_info_content)
                    table = soup.find("table", id="item")
                    trs = table.find_all("tr")
                    borrow_title = soup.find('tr', attrs={"class": "greytext1"}).find_all("td")[0:4]
                    borrow_title_text = []  # tr的文字集合
                    for i in borrow_title:
                        borrow_title_text.append(i.text)
                    borrow_info = []
                    borrow_info_text = []  # td的文字集合

                    borrow_info = soup.find_all('tr', attrs={"class": "whitetext"})
                    for i in borrow_info:
                        for j in i.find_all('td'):
                            borrow_info_text.append(j)
                    data_list = []
                    data = {}
                    # print(len(borrow_info_text))
                    # print(borrow_info_text)

                    for j, k in enumerate(borrow_info_text):
                        if j % 4 == 0:
                            data['call_number'] = k.text
                        elif j % 4 == 1:
                            data['barcode'] = k.text
                        elif j % 4 == 2:
                            data['period'] = k.text
                        elif j % 4 == 3:
                            data['place'] = k.text
                            if len(data) == 4:
                                data_list.append(data)
                                data = {}

                    data_list.append(self.book_info_content)
                    data_list = response_info.success("目标图书链接查询成功", data_list)
                else:
                    data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号错误', '')
            else:
                data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)

        except:
            r.rpush("vpn_account", vpn_account)
            raise
        finally:
            session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Origin': 'https://vpn.just.edu.cn',
                'Upgrade-Insecure-Requests': '1'
            }, verify=False)
        return data_list, vpn_account


class Book_list():
    def __init__(self):
        self.data_json = []

    def getList(self, bookname):
        p = Proxy()
        session, vpn_account = p.login()
        if (bookname == 'c++' or bookname == 'C++'):
            search_url = 'https://vpn.just.edu.cn/opac/,DanaInfo=lib.just.edu.cn,Port=8080+openlink.php?strSearchType=title&match_flag=forward&historyCount=1&strText=c%2B%2B&doctype=ALL&displaypg=20&showmode=list&sort=CATA_DATE&orderby=desc&location=ALL'
        else:
            search_url = "https://vpn.just.edu.cn/opac/,DanaInfo=lib.just.edu.cn,Port=8080+openlink.php?title=" + bookname + "&with_ebook=on"
        try:
            # search_url = "https://vpn.just.edu.cn/opac/,DanaInfo=lib.just.edu.cn,Port=8080+openlink.php?title=" + bookname + "&with_ebook=on"
            result = session.get(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Origin': 'https://vpn.just.edu.cn',
                'Upgrade-Insecure-Requests': '1'
            }, verify=False)
            result.encoding = 'utf-8'
            # print(result.text)
            soup = BeautifulSoup(result.text, "html.parser")
            isVpnLoginSuccess = soup.find('span', class_='cssLarge')
            isAccountLoginSuccess = soup.find('div', class_='dlti')
            isFindBookListSuccess=soup.find('p',attrs={'style':'font-size:14px; margin:5px 0 20px 10px;'})
            if not isVpnLoginSuccess:
                if not isAccountLoginSuccess:
                    if not isFindBookListSuccess:
                        book_search_list = []
                        book_search_list = soup.find('ol', attrs={"id": "search_book_list"}).find_all('li', attrs={
                            'class': 'book_list_info'})
                        # print(book_search_list)
                        book_item = {}
                        data_list = []
                        for i in book_search_list:
                            book_item = {}
                            book_url = "https://vpn.just.edu.cn/opac/" + i.find('h3').find('a').get('href')
                            book_title = i.find('h3').find('a').text
                            book_tip = i.find('p').text.replace('\r', '').replace('\n', '').replace(' ', '')

                            book_item["book_title"] = book_title
                            book_item["book_url"] = book_url
                            book_item["book_can_borrow"] = book_tip[0:13]
                            book_item["book_author_press"] = book_tip[13:-5:1]
                            data_list.append(book_item)
                        data_list = response_info.success("搜索图书列表查询成功", data_list)
                    else:
                        data_list = response_info.error(static.JUST_LIB_SEARCH_ERROR, '找不到搜索的图书列表', '')
                else:
                    data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号错误', '')
            else:
                data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)

        except:
            r.rpush("vpn_account", vpn_account)
            raise
        finally:
            session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Origin': 'https://vpn.just.edu.cn',
                'Upgrade-Insecure-Requests': '1'
            }, verify=False)

        return data_list, vpn_account


class RecommendBook():
    def __init__(self):
        self.data_list = []

    def get_top_100(self):
        p = Proxy()
        session, vpn_account = p.login()
        try:
            top_url = 'https://vpn.just.edu.cn/top/,DanaInfo=lib.just.edu.cn,Port=8080+top_lend.php'
            result = session.get(top_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Origin': 'https://vpn.just.edu.cn',
                'Upgrade-Insecure-Requests': '1'
            }, verify=False)
            result.encoding = 'utf-8'
            soup = BeautifulSoup(result.text, 'html.parser')
            isVpnLoginSuccess = soup.find('span', class_='cssLarge')
            isAccountLoginSuccess = soup.find('div', class_='dlti')
            if not isVpnLoginSuccess:
                if not isAccountLoginSuccess:
                    isVpnLoginSuccess = soup.find('span', class_='cssLarge')
                    if not isVpnLoginSuccess:
                        table = soup.find('table', attrs={'class': 'table_line'})
                        trs = table.find_all('tr')
                        for tr in trs[1:]:
                            data = {}
                            tds = tr.find_all('td')
                            data['number'] = tds[0].text
                            data['url'] = 'https://vpn.just.edu.cn' + tds[1].find('a').get('href')[2:]
                            data['name'] = tds[1].text
                            data['author'] = tds[2].text
                            data['press'] = tds[3].text
                            data['bookcode'] = tds[4].text
                            data['collection'] = tds[5].text
                            data['borrow_times'] = tds[6].text
                            data['borrow_rate'] = tds[7].text
                            self.data_list.append(data)
                        self.data_list = random.sample(self.data_list, 50)
                        self.data_list = response_info.success("TOP100查询成功", self.data_list)

                    else:
                        self.data_list = 'vpn账号错误'
                else:
                    self.data_list = response_info.error(static.JUST_ACCOUNT_LOGIN_ERROR, '教务系统账号错误', '')
            else:
                self.data_list = response_info.error(static.JUST_VPN_LOGIN_ERROR, 'vpn账号被占用', vpn_account)

        except:
            r.rpush("vpn_account", vpn_account)
            raise
        finally:
            session.post('https://vpn.just.edu.cn/dana-na/auth/logout.cgi', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Origin': 'https://vpn.just.edu.cn',
                'Upgrade-Insecure-Requests': '1'
            }, verify=False)
        return self.data_list, vpn_account


def main():
    # 返回前10大热门搜索词
    h = RecommendBook()
    hot_book = h.get_top_100()
    print(hot_book)

if __name__ == '__main__':
    main()