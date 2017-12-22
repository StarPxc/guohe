import requests
from bs4 import BeautifulSoup
class Proxy():
    def __init__(self):
        self.MAX=5
        self.headers={
            "Host":"jandan.net",
            # "Referer":"http://www.anyv.net/index.php/account-2533",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
            "Proxy-Connection":"keep-alive",
            "Upgrade-Insecure-Requests":'1'
        }

    def getPage(self,url):
        FAILTIME=0
        try:
            result=requests.get(url,headers=self.headers)
            result.encoding="utf-8"
            return result
        except:
            FAILTIME+=1
            if FAILTIME==self.MAX:
                print("发生错误")
                return ''

class Quwen():
    def __init__(self):
        self.data_list=[]

    def getQuwen(self):
        p=Proxy()
        result=p.getPage("http://jandan.net/")
        # print(result.text)
        soup=BeautifulSoup(result.content,"html.parser")
        temp_list=soup.find('div',attrs={'id':'content'}).find_all('div',attrs={'class':'post f list-post'})[0:4]
        for i in temp_list:
            temp_dict={}
            title=i.find('div',attrs={'class':'indexs'}).find('h2').text
            classify=i.find('div',attrs={'class':'indexs'}).find('div',attrs={'class':'time_s'}).find('strong').text
            url=i.find('div',attrs={'class':'indexs'}).find('h2').find('a').get('href')
            img_url=i.find('div',attrs={'class':'thumbs_b'}).find('img').get('src')
            # print(img_url)
            # print(type(img_url))
            temp_dict['title']=title
            temp_dict['classify']=classify
            temp_dict['img_url']=img_url

            result1=p.getPage(url)
            soup1=BeautifulSoup(result1.content,"html.parser")
            list_p=soup1.find('div',attrs={'class':'post f'}).find_all('p')
            temp_content = []
            for j in list_p:
                if 'img' in str(j):
                    temp_content.append(j.find('img').get('data-original'))
                    # print(j.find('img').get('data-original'))
                    # print(type(j.find('img').get('data-original')))
                else:
                    temp_content.append(j.text)
            temp_dict['content']=temp_content
            self.data_list.append(temp_dict)

        return self.data_list





if __name__ == '__main__':
    q=Quwen()
    print(q.getQuwen())