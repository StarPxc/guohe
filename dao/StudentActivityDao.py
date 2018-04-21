"""
@author: Ethan

@description:

@website:http://www.guohe3.com

@contact: pxc2955317305@gmail.com

@time: 2018/4/20 15:10

"""
#活动报名
import datetime

from util import db_util


def attend_activity(a_id,s_number):
    gmt_create=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db = db_util.get_db()
    cursor = db.cursor()
    sum= cursor.execute("insert into student_activity(a_id,s_number,gmt_create) \
    values('%d','%s','%s')" % \
                   (a_id,s_number,gmt_create))
    db.commit()
    return sum
if __name__ == '__main__':
    print(attend_activity(1,"31232134"))