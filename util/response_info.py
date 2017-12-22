import json
from util import  static_var_util
def success(msg,info):
    result={}
    result['code']=200
    result['msg']=msg
    result['info']=info
    return result

def error(code,msg,info):
    result = {}
    result['code'] = code
    result['msg'] = msg
    result['info'] = info
    return result

if __name__ == '__main__':
    static=static_var_util.StaticVar()
    error(static.JUST_ACCOUNT_LOGIN_ERROR,"账号错误",'null')
