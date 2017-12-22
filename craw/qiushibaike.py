import re
import requests
import pymysql
pymysql.install_as_MySQLdb()


from bs4 import BeautifulSoup
class craw_qiushibaike(object):
    def start(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }
        name_list = []
        response = requests.get("https://www.qiushibaike.com/", headers=headers)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        divs = soup.find_all('div', class_='content')
        names = soup.find_all('div', class_='author clearfix')

        for name in names:
            name_list.append(name.find('h2').get_text().strip())

        data_list = []
        for i, div in enumerate(divs):
            data = {}
            link = div.find_parent('a', href=re.compile(r"/article/"))
            id = link['href'].split("/")[2]
            data['id'] = id
            if ("查看全文" in div.get_text().strip()):
                data['content'] = self.get_all(id)
            else:
                data['content'] = div.get_text().strip()
            data['article'] = name_list[i]
            data_list.append(data)
        return  data_list


    def get_all(self,id):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Host': 'www.qiushibaike.com',
            'Referer': 'https://www.qiushibaike.com/'
        }
        cookies = {}
        cookieStr = '''
        __cur_art_index=1100; _xsrf=2|ee7f76b0|e8304868fb978602f6823e279dbb4dfd|1507552180; Hm_lvt_2670efbdd59c7e3ed3749b458cafaa37=1507034287,1507340523,1507552184,1507552451; Hm_lpvt_2670efbdd59c7e3ed3749b458cafaa37=1507555464; _ga=GA1.2.1690623501.1506932265; _gid=GA1.2.1089419135.1507552184
        '''
        for item in cookieStr.split(";"):
            x = item.split("=")
            cookies[x[0]] = x[1]
        response = requests.get("https://www.qiushibaike.com/article/%s" % id, headers=headers, cookies=cookies)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        div = soup.find('div', class_='content')
        return div.get_text()
