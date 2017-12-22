from urllib import parse
import requests
from bs4 import BeautifulSoup
import urllib.parse
def today_history(page=0,size=0):

    data_list = []
    url = "http://www.todayonhistory.com/"
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Upgrade-Insecure-Requests':'1'
    }
    test=[]
    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", id='container')
    for i,li in enumerate(ul.find_all('li')):
        data={}
        if li.select("div.pic") and i!=0:
            data['time']=li.select("div.pic span")[0].string
            data['title'] = li.select("div.pic a")[0]['title']
            data['detailUrl']=li.select("div.pic a")[0]['href']
            data['imgUrl']=urllib.parse.urljoin("http://www.todayonhistory.com",li.select("div.pic a img")[0]['data-original'])
            data_list.append(data)
    if int(size)!=0:
        return data_list[int(page)*int(size):int(page)*int(size)+5]
    else:
        return data_list

def historyDetail(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    title=soup.find("div",class_='content').find("h1").get_text()
    imgUrl=parse.urljoin("http://www.todayonhistory.com/upic/200905/17/90225133373.jpg",soup.select(".content .body img")[0]['src'])
    strong=''
    if  len(soup.select(".content strong"))!=0:
        strong = soup.select(".content strong")[0].get_text()
    else :
        strong=''
    content = ''
    if len(soup.select(".content .body p"))>0:
        for item in soup.select(".content .body p")[1:]:
            content=content+item.get_text().strip()
    else:
        for item in soup.select(".content .body div")[1:]:
            content=content+item.get_text().strip()
    data={'title':title,'imgUrl':imgUrl,'strong':strong,'content':content}
    return data
