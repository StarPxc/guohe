import hashlib

import pymysql
from util import response_info,static_var_util

db_password='935377012'
static=static_var_util.StaticVar()

def md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()
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
#保存学生信息
def add_student_info(username,password,name,birthday,major,academy,class_num):
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
    sql = "insert into student(username,password,s_name,birthday,major,academy,class_num) values ('%s','%s','%s','%s','%s','%s','%s')" % \
          (username, md5(password), name, birthday, major,academy, class_num)
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
#更新学生信息
def update_student_info(password, name, birthday,major,academy,class_num, username):
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
    sql = "update student set password='%s',s_name='%s',birthday='%s',major='%s',academy='%s',class_num='%s' where username=%s" % \
          (password, name, birthday,major,academy,class_num, username)
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
    except:
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

    except:
        return response_info.error(static.JUST_APK_SELECT_ERROR,'apk信息查询失败', data)
    # 关闭数据库连接
    finally:
        db.close()
if __name__ == '__main__':
    print(get_download_apk_info())