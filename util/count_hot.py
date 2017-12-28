'''
@author: Ethan

@contact: pxc2955317305@gmail.com

@software: guohe

@file: file_count.py

@time: 2017/12/23 16:13

@website:http://www.guohe3.com
'''
def count_info():
    data_list = ['xiaoli', 'vpnKebiao', 'vpnBookDetail', 'vpnScore', 'vpnBookTop100', 'vpnHotBook', 'vpnJidian',
                 'horoscope', 'vpnClassroom', 'vpnInfo', 'vpnSport', 'vpnRun', 'history', 'oneArticle']
    return_dict=dict(zip(data_list,[0]*len(data_list)))
    with open('/var/www/log/guohe.log', mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            for item in data_list:
                if item in line and return_dict[item] is not None:
                    return_dict[item]=return_dict[item]+1
    return  sorted(return_dict.items(),key=lambda item:item[1],reverse=True)


if __name__ == '__main__':
    data_list=['xiaoli','vpnKebiao','vpnBookDetail','vpnScore','vpnBookTop100','vpnHotBook','vpnJidian',
               'horoscope','vpnClassroom','vpnInfo','vpnSport','vpnRun','history','oneArticle']
    print(count_info())