'''
@author: Ethan

@description:

@website:http://www.guohe3.com

@contact: pxc2955317305@gmail.com

@time: 2018/4/20 14:03

'''
from entity.Activity import Activity
from entity.Student import Student
from util import db_util

#根据学号查询学生
def get_student_by_primaryKey(primaryKey):
    db = db_util.get_db()
    cursor = db.cursor()
    sum = cursor.execute("select * from student where username=%s" % primaryKey)
    if sum==0:
        return None
    result=cursor.fetchone()
    student=Student(result[0],result[2],result[3],result[4],result[5],result[6],result[7],result[8])
    return student
#根据学号查删除学生
def delete_student_by_primaryKey(primaryKey):
    db=db_util.get_db()
    cursor=db.cursor()
    sum = cursor.execute("delete from student where username=%s" % primaryKey)
    db.commit()
    if sum==0:
        return None
    return 1






if __name__ == '__main__':
    print(delete_student_by_primaryKey("152210702119"))
