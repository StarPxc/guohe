from itertools import groupby
from operator import itemgetter

from craw import student


class Point(object):
    a = 0

    # 传入参数计算绩点
    def get_jidian(self, score):

        if (isinstance(score, float)):
            return score / 10 - 5
        elif score == '优':
            return 4.5
        elif score == '良':
            return 3.5
        elif score == '中':
            return 2.5
        elif score == '及格':
            return 1.5
        elif score == '不及格':
            return 0
        elif score == '通过':
            return 2.5
        elif score == '不通过':
            return 0
        else:
            return 3

    # 判断字符串是否是由数字组成
    def is_number(self, var):
        try:
            float(var)
            return True
        except:
            return False

    # 根据传入的数据计算平均绩点
    def get_average_point(self, data_list):
        xuefen_jidian_all = 0  # 学分绩点之和
        score_sum = 0  # 学分之和
        data_list.sort(key=lambda k: k.get('score'), reverse=True)  # 按成绩降序排序
        data_list2 = []  # 取补考和重修后的数据
        # 去除重修前和补考前的课程成绩
        for item in data_list:
            flag = True
            for c in data_list2:
                if item['course_name'] == c['course_name']:
                    flag = False
            if flag:
                data_list2.append(item)
        # 去除一些不算绩点的科目
        data_list3 = data_list2[:]
        for item in data_list3:
            if item['course_nature'].strip() == '公共任选课':
                data_list2.remove(item)
            elif item['course_attribute'].replace(r'\t', '').replace(r'\n', '').replace(' ', '') == '任选':
                data_list2.remove(item)
            elif '体育' in item['course_name'].replace(r'\t', '').replace(r'\n', '').replace(' ', ''):
                data_list2.remove(item)
        # pd=pandas.DataFrame(data_list2)
        # pd.to_excel(r"e://test%s.xls" % 2)
        for i, item in enumerate(data_list2):
            if self.is_number(data_list2[i]['score']):
                score = float(data_list2[i]['score'].replace(r'\t', '').replace(r'\n', '').replace(' ', ''))
            else:
                score = data_list2[i]['score'].replace(r'\t', '').replace(r'\n', '').replace(' ', '')
            if data_list2[i]['credit']:
                xuefen_jidian_all = xuefen_jidian_all + float(
                    data_list2[i]['credit'].replace(r'\t', '').replace(r'\n', '').replace(' ', '')) * self.get_jidian(
                    score)  # 学分绩点=学分*绩点，这里算的是学分绩点之和
                score_sum = score_sum + float(data_list2[i]['credit'])  # 学分之和
        # 一个学弟这个学期刚开始出来的两门课全是不算学分的，所以score_sum=0
        if score_sum == 0:
            return 0
        else:
            result = round(xuefen_jidian_all / score_sum, 3)
            return result

    # 获得每一个学期的平均绩点
    def get_each_point(self, data_list):
        each_point = []
        datalist = data_list.copy()
        datalist.sort(key=itemgetter('start_semester'))  # 需要先排序，然后才能groupby。datalist排序后自身被改变
        lstg = groupby(datalist, itemgetter('start_semester'))
        for key, group in lstg:
            temp_list = []
            for g in group:  # group是一个迭代器，包含了所有的分组列表
                temp_list.append(g)
            a = {'year': key, 'point': str(self.get_average_point(temp_list))}
            each_point.append(a)
        return each_point


if __name__ == '__main__':
    p = Point()
    print(p.get_average_point(student.get_score('152210702116', 'nhs320426')['info']))
