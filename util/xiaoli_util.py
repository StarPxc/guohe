'''
@author: Ethan

@description: 校历计算

@website:http://www.guohe3.com

@contact: pxc2955317305@gmail.com

@time: 2018/1/15 9:43

'''
import xlrd
def kb_date(semester,zc):
    xs = xlrd.open_workbook(r'D:\\2017-2018.xlsx')
    table = xs.sheets()[0]
    data = {}
    if semester=='2017-2018-1':
        if zc <= 3:
            data['month'] = 9
        elif zc > 3 and zc <= 8:
            data['month'] = 10
        elif zc > 8 and zc <= 12:
            data['month'] = 11
        elif zc > 12 and zc <= 17:
            data['month'] = 12
        elif zc > 17 and zc <= 21:
            data['month'] = 1
        elif zc > 21 and zc <= 25:
            data['month'] = 2
        data['date'] = table.col_values(zc)[2:9]
    else:
        if zc <= 4:
            data['month'] = 3
        elif zc > 4 and zc <= 9:
            data['month'] = 4
        elif zc > 9 and zc <= 13:
            data['month'] = 5
        elif zc > 13 and zc <= 17:
            data['month'] = 6
        elif zc > 17 and zc <= 22:
            data['month'] = 7
        elif zc > 22 and zc <= 27:
            data['month'] = 8
        data['date'] = table.col_values(zc)[14:21]
    return data
if __name__ == '__main__':
    print(kb_date('2017-2018-2',21))

        
    

