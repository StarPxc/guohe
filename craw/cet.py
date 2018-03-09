'''
@author: Ethan

@description:

@website:http://www.guohe3.com

@contact: pxc2955317305@gmail.com

@time: 2018/2/26 9:46

'''
import pymysql
import requests
from flask import request, json, jsonify

from util import response_info
from util.db_util import db_password


def get_zkzh(ks_xm,ks_sfz,type):
    data=""
    try:
        url = "http://app.cet.edu.cn:7066/baas/app/setuser.do?method=UserVerify"
        ks_data = {
            "ks_xm": ks_xm,
            "ks_sfz": ks_sfz,
            "jb": int(type)
        }
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        post_json = json.dumps(ks_data)
        postdata = {
            "action": "",
            "params": post_json
        }
        r = requests.post(url, data=postdata)
        res = r.content
        res = bytes.decode(res)
        data=json.loads(res)
        if "ks_bh" in data:
            data=response_info.success("success",{'zkzh': json.loads(res)["ks_bh"]})
            db = pymysql.Connect(
                host='localhost',
                port=3306,
                user='root',
                passwd=db_password,
                db='just',
                charset='utf8'
            )
            cursor = db.cursor()
            sql = "insert into cet(xm,sfz,score) values ('%s','%s','%s')" % \
                  (ks_xm, ks_sfz, json.loads(res)["ks_bh"])
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except Exception as e:
                db.rollback()
            finally:
                # 关闭数据库连接
                db.close()
        else:
            data=response_info.error(501, "未获取数据","未获取数据")
    except:

        data=response_info.error(500, "未知错误","未知错误")

    return data
if __name__ == '__main__':

    print(get_zkzh('裴菲菲','320923199612084217',"2"))
