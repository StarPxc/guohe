import logging

import requests
from bs4 import BeautifulSoup
import re

class Proxy():
    def __init__(self):
        self.MAX=5
        self.headers={
            "Host":"www.tduanzi.com",
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

class Duanzi:
    def __init__(self):
        self.data_list=[]

    def getDuanzi(self):
        p=Proxy()
        result=p.getPage("http://www.tduanzi.com/")
        result.encoding="utf-8"
        # print(result.text)
        soup=BeautifulSoup(result.content,"html.parser")

        temp_list=soup.find('div',attrs={'class':'list'}).find('ul').find_all('li')

        for i in temp_list:
            temp_dict={}
            txt=i.find('div',attrs={'class':'right'}).find('a').text
            temp_dict["txt"]=txt
            flag=i.find('div',attrs={'class':'right'}).find('div',attrs={'class':'img'})
            if(flag):
                img_url=i.find('div',attrs={'class':'right'}).find('div',attrs={'class':'img'}).find('a').get('bigimg')
                # print(img_url)
                temp_dict["img_url"]=img_url
            self.data_list.append(temp_dict)

        return self.data_list






if __name__ == '__main__':
   logging.error('湿哒哒')