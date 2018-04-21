import pymysql
from util import public_var
# 打开数据库连接

# 使用cursor()方法获取操作游标
from util import response_info
static=public_var.publicVar()

def add_kb(time,data):
    db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "INSERT INTO kb(monday,tuesday, wednesday, thursday, friday,saturday,sunday,kb_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        tmp=[]
        for index, item in enumerate(data):
            temp_list = []
            for l, v in item.items():
                temp_list.append(v)
            temp_list.append(time)
            tmp.append(tuple(temp_list))
        cursor.executemany(sql,tmp)
        db.commit()
    except:
        db.rollback()
        raise
    db.close()

def update_download_apk_info(download_info):
    db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "insert into apk(appname,serverVersion,serverFlag,lastForce,updateurl,updateinfo) values(%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql,(download_info['appname'],download_info['serverVersion'],download_info['serverFlag'],download_info['lastForce'],'http://106.14.220.63/apk/download/guohe',download_info['updateinfo'],))
        db.commit()

        return response_info.success('更新成功', download_info)
    except:
        db.rollback()

        return response_info.error(802,'更新失败', download_info)

    finally:
        db.close()

def get_download_apk_info():
    db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql="select *   from   apk   order   by   id   desc   limit   1 "
    data = {}
    try:
        cursor.execute(sql)
        result= cursor.fetchone()
        i=0
        for item in cursor.description:
            data[item[0]]=result[i]
            i+=1
        return response_info.success('apk信息查询成功',data)

    except:
        return response_info.error('701','apk信息查询失败', data)
    # 关闭数据库连接
    finally:
        db.close()

def get_data():
    db=db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql="select * from guohe_data "
    data={}
    try:
        cursor.execute(sql)
        result=cursor.fetchone()
        i=0
        for item in cursor.description:
            data[item[0]]=result[i]
            i+=1
        return data
    except:
        return  response_info.error('1001','网站基本数据查询失败',data)
    finally:
        db.close()

def get_pxc_users():
    db = pymysql.Connect(
        host='120.25.88.41',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD,
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    sql="select count(*) from student"
    try:
        cursor.execute(sql)
        numUsers = cursor.fetchone()
        return numUsers
    except:
        raise
        return response_info.error('1006', '用户数查询失败', data)
    finally:
        db.close()


def set_users(numOfusers):
    db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql="update guohe_data set users=%s where id=1"
    try:
        cursor.execute(sql, numOfusers)
        db.commit()
        return response_info.success('用户量更新成功', numOfusers)
    except:
        db.rollback()

        return response_info.error('1002', '用户量更新失败', numOfusers)
    finally:
        db.close()

def set_downloads(numOfdownloads):
    db = db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "update guohe_data set downloads=%s where id=1"
    try:
        cursor.execute(sql, numOfdownloads)
        db.commit()
        return response_info.success('下载量更新成功', numOfdownloads)
    except:
        db.rollback()

        return response_info.error('1003', '下载量更新失败', numOfdownloads)
    finally:
        db.close()



def set_clicks_app(numOfclicks_app):
    db = db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "update guohe_data set clicks_app=%s where id=1"
    try:
        cursor.execute(sql, numOfclicks_app)
        db.commit()
        return response_info.success('App点击量更新成功', numOfclicks_app)
    except:
        db.rollback()

        return response_info.error('1004', 'App点击量更新失败', numOfclicks_app)
    finally:
        db.close()

def set_clicks_web(numOfclicks_web):
    db = db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd=static.DB_PASSWORD2,
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "update guohe_data set clicks_web=%s where id=1"
    try:
        cursor.execute(sql, numOfclicks_web)
        db.commit()
        return response_info.success('Web点击量更新成功', numOfclicks_web)
    except:
        db.rollback()

        return response_info.error('1005', 'Web点击量更新失败', numOfclicks_web)
    finally:
        db.close()






if __name__ == '__main__':
    print(get_download_apk_info())