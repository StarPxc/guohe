import requests
from bs4 import BeautifulSoup


def craw_horoscope(select):
    #horoscope_name=['白羊座','金牛座','双子座','巨蟹座','狮子座','处女座','天秤座','天蝎座','射手座','摩羯座','水瓶座','双鱼座']
    horoscope_english=['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricornus','aquarius','pisces']
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.xzw.com/fortune',
        'Host': 'www.xzw.com'
    }
    response = requests.get("http://www.xzw.com/fortune/%s" % select)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        spans = soup.find("div", class_='c_cont').find_all("span")
        data_list = [{'imgUrl':'http://120.25.88.41/constellation/%s.jpg' % select}]
        name_list = ['综合运势', '爱情运势', '事业学业', '财富运势', '健康运势']
        for i, span in enumerate(spans):
            data = {}
            data[name_list[i]] = span.get_text()
            data_list.append(data)
        return data_list
    except:
        return {'error':'未找到'}
if __name__ == '__main__':
    print(craw_horoscope("aries"))
