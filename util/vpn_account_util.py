'''
@author: Ethan

@description:vpn账号工具文件

@website:http://www.guohe3.com

@contact: pxc2955317305@gmail.com

@time: 2017/12/23 22:23

'''
import threading

import  redis
import time
lock = threading.Lock()
from util import  static_var_util,response_info
static=static_var_util.StaticVar()
def get_vpn_account():
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    lock.acquire()
    vpn_account={}
    try:
        flag = True
        while flag:
            time.sleep(0.5)
            if r.lrange('vpn_account2', 0, -1):#若缓存中没有账号则等待
                flag = False
                vpn_account=eval(r.lpop('vpn_account2'))
                return response_info.success('获取vpn账号成功', vpn_account)
    finally:
        r.rpush("vpn_account2", vpn_account)
        # 改完了一定要释放锁:
        lock.release()
def add_vpn_info(username,password):
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    vpn_list=r.lrange('vpn_account2', 0, -1)
    flag=True
    try:
        for i, item in enumerate(vpn_list):
            data = eval(item)
            if data['username'] == username:
                flag = False
        if flag:
            r.rpush('vpn_account2', {'username': username, 'password': password})
            return response_info.success('vpn账号添加成功', username)
        else:
            return response_info.error(static.JUST_HAS_VPN_ACCOUNT, 'vpn账号已经存在', '')
    except:
        raise
if __name__ == '__main__':
    print(add_vpn_info('asdasdadasdsadasdsa','asdas'))