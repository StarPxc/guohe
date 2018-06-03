import datetime
import hashlib
import logging
import pymysql
from util import response_info,static_var_util,public_var
public=public_var.publicVar()
db_password=public.DB_PASSWORD
static=static_var_util.StaticVar()
def md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()



def get_db():
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    return db
def get_student_jidian(username):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    result=cursor.execute("select * from jidian where username=%s" % username)
    return result

#保存绩点信息
def add_student_jidian(jidian,username):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )

    cursor = db.cursor()
    print("保存绩点数据")
    sql = "insert into jidian(jidian,username) values('%s','%s')" % (jidian, username)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        logging.exception(e)
        db.rollback()
    # 关闭数据库连接
    db.close()
def update_student_jidian(jidian,username):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    print("更新数据")
    sql = "update jidian set jidian='%s' where username='%s'" % (jidian, username)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        logging.exception(e)
        db.rollback()
        return response_info.error(static.JUST_APK_INFO_UPDATE_ERROR, '更新失败', username)
    finally:
        db.close()

#获取学生基本信息
def get_student_info(username):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    result = cursor.execute("select * from student where username=%s" % username)
    return result
#保存反馈信息
def add_feedback(name,content,category,contact):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = db.cursor()
    print("保存反馈信息")
    sql = "insert into feedback(f_name,f_time,f_content,f_category,f_contact) values ('%s','%s','%s','%s','%s')" % \
          (name,dt,content,category,contact)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        return response_info.success('反馈成功',name)
    except Exception as e:
        logging.exception(e)
        db.rollback()
        return response_info.error(static.FEEDBACK_ERROR,'反馈失败', e)
    finally:
        # 关闭数据库连接
        db.close()
#保存学生信息
def add_student_info(username,password,name,birthday,major,academy,class_num,create_time,last_visit_time):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    print("保存数据")
    sql = "insert into student(username,password,s_name,birthday,major,academy,class_num,create_time,last_visit_time) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
          (username, md5(password), name, birthday, major,academy, class_num,create_time,last_visit_time)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        logging.exception(e)
        db.rollback()
    # 关闭数据库连接
    db.close()
#更新学生信息
def update_student_info(password, name, birthday,major,academy,class_num, username,last_visit_time):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    print("数据已存在，执行更新操作")
    sql = "update student set password='%s',s_name='%s',birthday='%s',major='%s',academy='%s',class_num='%s',last_visit_time='%s' where username=%s" % \
          (password, name, birthday,major,academy,class_num,last_visit_time, username)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        db.rollback()
        raise
    # 关闭数据库连接
    db.close()
#增加课表
def add_kb(time,data):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
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
#更新apk信息
def update_download_apk_info(download_info):
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "insert into apk(appname,serverVersion,serverFlag,lastForce,updateurl,updateinfo) values(%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql,(download_info['appname'],download_info['serverVersion'],download_info['serverFlag'],download_info['lastForce'],'http://120.25.88.41/apk/download/guohe',download_info['updateinfo'],))
        db.commit()
        return response_info.success('更新成功', download_info)
    except Exception as e:
        logging.exception(e)
        db.rollback()
        return response_info.error(static.JUST_APK_INFO_UPDATE_ERROR,'更新失败', download_info)

    finally:
        db.close()
#获得apk信息
def get_download_apk_info():
    db = pymysql.Connect(
        host='localhost',
        port=3306,
        user='root',
        passwd=db_password,
        db='just',
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

    except Exception as e:
        logging.exception(e)
        return response_info.error(static.JUST_APK_SELECT_ERROR,'apk信息查询失败', data)
    # 关闭数据库连接
    finally:
        db.close()
def get_toast_info():
    db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd='root',
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "select content   from   guohe_lite_toast   order   by   id   desc   limit   1 "
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        return response_info.success('小程序通知查询成功', result)
    except:
        return response_info.error('2', '小程序通知查询失败', result)
        # 关闭数据库连接
    finally:
        db.close()
def update_toast(toast_update_info):
    db = pymysql.Connect(
        host='106.14.220.63',
        port=3306,
        user='root',
        passwd='root',
        db='guohe_home',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "insert into guohe_lite_toast(content,update_time) values(%s,%s) "
    try:
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(sql,(toast_update_info,dt))
        db.commit()
        return response_info.success('通知更新成功', toast_update_info)
    except:
        db.rollback()
        return response_info.error("2",'更新失败', toast_update_info)
    finally:
        db.close()

def get_carousel_by_quantity(quantity):
    db = pymysql.Connect(
        host='120.25.88.41',
        port=3306,
        user='root',
        passwd='935377012',
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "select title,img,url,describe_txt   from   carousel   order   by   id   desc   limit  %s  " % quantity

    try:
        cursor.execute(sql)
        result=cursor.fetchall()
        datalist=[]
        for tem in result:
            format_t={}
            format_t["title"] = tem[0]
            format_t["img"] = tem[1]
            format_t["url"] = tem[2]
            format_t["describe"] = tem[3]
            datalist.append(format_t)
        return response_info.success("获取轮播图成功",datalist)
    except:
        return response_info.error("2","获取轮播图失败",datalist)

    finally:
        db.close()

def add_carousel(title,img,url,describe_txt):
    db = pymysql.Connect(
        host='120.25.88.41',
        port=3306,
        user='root',
        passwd='935377012',
        db='just',
        charset='utf8'
    )
    cursor=db.cursor()
    sql="insert into carousel (title,img,url,describe_txt) VALUES (%s,%s,%s,%s)"
    try:
        cursor.execute(sql,(title,img,url,describe_txt))
        db.commit()
        return response_info.success("增加轮播图成功",(title,img,url,describe_txt))
    except:
        return response_info.error("2","增加轮播失败",(title,img,url,describe_txt))
    finally:
        db.close()

def add_advertisement(title,img,url,describe_txt):
    db = pymysql.Connect(
        host='120.25.88.41',
        port=3306,
        user='root',
        passwd='935377012',
        db='just',
        charset='utf8'
    )
    cursor=db.cursor()
    sql="insert into advertisement (title,img,url,describe_txt) VALUES (%s,%s,%s,%s)"
    try:
        cursor.execute(sql,(title,img,url,describe_txt))
        db.commit()
        return response_info.success("增加广告图成功",(title,img,url,describe_txt))
    except:
        return response_info.error("2","增加广告失败",(title,img,url,describe_txt))
    finally:
        db.close()


def get_advertisement():
    db = pymysql.Connect(
        host='120.25.88.41',
        port=3306,
        user='root',
        passwd='935377012',
        db='just',
        charset='utf8'
    )
    cursor = db.cursor()
    sql = "select title,img,url,describe_txt   from   advertisement   order   by   id   desc   limit  1  "

    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        format_t = {}
        format_t["title"] = result[0]
        format_t["img"] = result[1]
        format_t["url"] = result[2]
        format_t["describe"] = result[3]

        return response_info.success("获取广告图成功", format_t)
    except:
        return response_info.error("2","获取广告图失败", format_t)

    finally:
        db.close()




if __name__ == '__main__':
    print(add_feedback('asda','asdsa','a','asdsa'))