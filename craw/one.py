import requests
from bs4 import BeautifulSoup


def one_article_detail(url):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Host':'wufazhuce.com'
    }
    result=requests.get(url,headers=headers)
    result.encoding='utf-8'
    return result

def get_question():
    one_url = 'http://wufazhuce.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Host': 'wufazhuce.com'
    }
    result = requests.get(one_url, headers=headers)
    soup = BeautifulSoup(result.content, 'html.parser')
    one_article = soup.find('p', attrs={'class': 'one-articulo-titulo'})


    question = []
    question_dict = {}  # 返回的问题json



    one_question_title = soup.find('p', attrs={'class': 'one-cuestion-titulo'})
    one_question_url = soup.find('p', attrs={'class': 'one-cuestion-titulo'}).find('a').get('href')
    one_question_html = one_article_detail(one_question_url)
    soup2 = BeautifulSoup(one_question_html.content, "html.parser")
    one_question_content = soup2.find('div', attrs={'class': 'cuestion-contenido'}).text
    question.append(['title', one_question_title.text])
    question.append(['question', one_question_content])
    one_answer_content = soup2.find_all('div', attrs={'class': 'cuestion-contenido'})[1].find_all('p')
    num = 0
    for i in one_answer_content:
        num += 1
        question.append(["content"+str(num),i.text])

    question_dict = dict(question)
    # print(question_dict)

    # print(one_article_title.text) #文章标题
    # print(one_article_url)  #文章链接
    # article_details=one_article_detail(one_article_url) #文章详情


    # print(one_question_title.text)  #问题标题
    # print(one_question_url)   #问题链接
    question_details = one_article_detail(one_question_url)  # 问题详情
    return  question_dict

def get_article():
    one_url = 'http://wufazhuce.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Host': 'wufazhuce.com'
    }
    result = requests.get(one_url, headers=headers)
    soup = BeautifulSoup(result.content, 'html.parser')
    one_article = soup.find('p', attrs={'class': 'one-articulo-titulo'})

    article = []
    article_dict = {}  # 返回的文章json

    one_article_title = soup.find('p', attrs={'class': 'one-articulo-titulo'})
    article.append(['title', one_article_title.text])
    one_article_url = soup.find('p', attrs={'class': 'one-articulo-titulo'}).find('a').get('href')
    one_article_html = one_article_detail(one_article_url)
    soup1 = BeautifulSoup(one_article_html.content, "html.parser")
    one_article_content = soup1.find('div',attrs={"class":"articulo-contenido"}).find_all('p')
    num = 0
    for c in one_article_content:
        num += 1
        article.append(["content"+str(num), c.text])
    for i in article:
        article_dict[i[0]] = i[1]

    # print(article_dict)
    return article_dict



if __name__ == '__main__':
    print(get_article())
    print(get_question())
