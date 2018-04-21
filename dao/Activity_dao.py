'''
@author: Ethan

@description:

@website:http://www.guohe3.com

@contact: pxc2955317305@gmail.com

@time: 2018/4/20 14:48

'''

from entity.Activity import Activity
from util import db_util

#根据id查询活动
def get_activity_by_primaryKey(primaryKey):
    db = db_util.get_db()
    cursor = db.cursor()
    sum = cursor.execute("select * from activity where id=%s" % primaryKey)
    if sum==0:
        return None
    result=cursor.fetchone()
    activity=Activity(result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7],result[8],result[9],result[10]),
    return activity

#根据id删除活动
def delete_activity_by_primaryKey(primaryKey):
    db=db_util.get_db()
    cursor=db.cursor()
    sum = cursor.execute("delete from activity where id=%s" % primaryKey)
    db.commit()
    if sum==0:
        return None
    return 1


