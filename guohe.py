import base64
import os
import logging

import datetime
from flask import Flask, jsonify, request, make_response, Response, send_from_directory, url_for
import json
from werkzeug.utils import secure_filename, redirect
import craw.horoscope
import redis
from craw import historyToday, one, duanzi, quwen, vpn, vpnlibrary, run
from util import  db_util, response_info
from functools import wraps

app = Flask(__name__)
UPLOAD_FOLDER='/var/www/apk'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['apk'])

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/var/www/log/guohe.log',
                filemode='a')
# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst

    return wrapper_fun


r = redis.Redis(host='127.0.0.1', port=6379, db=0)


def has_key(keyName):
    for key in r.keys():
        if keyName == key.decode('utf-8'):
            return True
    return False


@app.route("/")
def index():
    return redirect("http://106.14.220.63")
@app.route('/horoscope/<select>', methods=['get'])
@allow_cross_domain
def horoscope(select):
    return jsonify(craw.horoscope.craw_horoscope(select))
@app.route('/history', methods=['post'])
@allow_cross_domain
def history():
    return jsonify(historyToday.today_history(request.form['page'], request.form['size']))


@app.route('/historyDetail', methods=['post'])
@allow_cross_domain
def historyDetail():
    return jsonify(historyToday.historyDetail(request.form['url']))


@app.route('/oneArticle', methods=['post', 'get'])
@allow_cross_domain
def oneArticle():
    if has_key("article_data"):
        return jsonify(eval(r.get('article_data').decode("utf-8")))
    else:
        data = one.get_article()
        r.set('article_data', data)
        r.expire('article_data', 60 * 60 * 12)
        return jsonify(data)


@app.route('/oneQuestion', methods=['post', 'get'])
@allow_cross_domain
def oneQuestion():
    if has_key("question_data"):
        return jsonify(eval(r.get('question_data').decode("utf-8")))
    else:
        data = one.get_question()
        r.set('question_data', data)
        r.expire('question_data', 60 * 60 * 12)
        return jsonify(data)


@app.route('/duanzi', methods=['post', 'get'])
@allow_cross_domain
def duanziTest():
    if has_key("duanzi"):
        return Response(json.dumps(eval(r.get('duanzi').decode("utf-8"))), mimetype='application/json')
    else:
        d = duanzi.Duanzi()
        data = d.getDuanzi()
        r.set('duanzi', data)
        r.expire('duanzi', 60 * 60 * 12)
        return Response(json.dumps(data), mimetype='application/json')


@app.route('/quwen', methods=['post', 'get'])
@allow_cross_domain
def quwenTest():
    if has_key("quwen"):
        return Response(json.dumps(eval(r.get('quwen').decode("utf-8"))), mimetype='application/json')
    else:
        q = quwen.Quwen()
        data = q.getQuwen()
        r.set('quwen', data)
        r.expire('quwen', 60 * 60 * 12)
        return Response(json.dumps(data), mimetype='application/json')
@app.route('/vpnScore', methods=['post'])
@allow_cross_domain
def vpnScore():
    data, vpn_account = vpn.vpnScore(request.form['username'], request.form['password'])
    r.rpush("vpn_account", vpn_account)
    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(vpn_account['username'],' vpnScore ',now)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnJidian', methods=['post'])
@allow_cross_domain
def vpnJidian():
    data, vpn_account = vpn.vpnJidian(request.form['username'], request.form['password'])
    r.rpush("vpn_account", vpn_account)
    if data['msg']=='vpn账号被占用':
        logging.error('vpn_account'+vpn_account['username'])
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnKebiao', methods=['post'])
@allow_cross_domain
def vpnKebiao():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if has_key(request.form['username'] + '_kebiao_' + request.form['semester']):
        r_data = eval(r.get(request.form['username'] + '_kebiao_' + request.form['semester']))
        if r_data['msg']!='vpn账号被占用' and r_data['msg']!='教务系统账号错误':
            print("从缓存中读取",' vpnKebiao ',now)
            return Response(
                json.dumps(eval(r.get(request.form['username'] + '_kebiao_' + request.form["semester"]).decode("utf-8"))),
                mimetype='application/json')
        else:
            print("设置缓存",' vpnKebiao ',now)
            data, vpn_account = vpn.vpnKebiao(request.form['username'], request.form['password'],
                                              request.form['semester'])
            r.rpush("vpn_account", vpn_account)
            print(vpn_account['username'])
            r.set(request.form['username'] + '_kebiao_' + request.form['semester'], data)
            r.expire(request.form['username'] + '_kebiao_' + request.form['semester'], 60 * 60 * 12)
            return Response(json.dumps(data), mimetype='application/json')
    else:
        print("设置缓存",' vpnKebiao ',now)
        data, vpn_account = vpn.vpnKebiao(request.form['username'], request.form['password'], request.form['semester'])
        r.rpush("vpn_account", vpn_account)
        print(vpn_account['username'])
        r.set(request.form['username'] + '_kebiao_' + request.form['semester'], data)
        r.expire(request.form['username'] + '_kebiao_' + request.form['semester'], 60 * 60 * 12)
        return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnInfo', methods=['post'])
@allow_cross_domain
def vpnInfo():
    data, vpn_account = vpn.vpnInfo(request.form['username'], request.form['password'])
    r.rpush("vpn_account", vpn_account)
    if data['msg']=='vpn账号被占用':
        logging.error('vpn_account'+vpn_account['username'])
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/xiaoli', methods=['post'])
@allow_cross_domain
def current_xiaoli():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data, vpn_account = vpn.xiaoli(request.form['username'], request.form['password'])
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'],' xiaoli ',now)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/kebiaoBySemesterAndWeek', methods=['post'])
@allow_cross_domain
def get_kebiaoBySemesterAndWeek():

    data, vpn_account = vpn.kebiaoBysemesterAndWeek(request.form['username'], request.form['password'],
                                                    request.form['semester'], request.form['week'])
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'])
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/currentKebiao', methods=['post'])
@allow_cross_domain
def current_kebiao():
    data, vpn_account = vpn.vpnCurrentKebiao(request.form['username'], request.form['password'])
    if len(vpn_account) >= 2:
        r.rpush("vpn_account", vpn_account)
        print(vpn_account['username'])
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnSport', methods=['post'])
@allow_cross_domain
def get_vpnSport():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data, vpn_account = vpn.VpnGetSport(request.form['username'], request.form['password'])
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'] + " vpnSport ",now)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnRun', methods=['post'])
@allow_cross_domain
def get_vpnRun():
    data, vpn_account =run.getSport(request.form['username'], request.form['password'])
    r.rpush("vpn_account", vpn_account)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnClassroom', methods=['post'])
@allow_cross_domain
def get_vpnClassroom():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data, vpn_account = vpn.vpnGetClassrooms(request.form['username'], request.form['password'],
                                             request.form['school_year'], request.form['area_id'],
                                             request.form['building_id'], request.form['zc1'])
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'] + "vpnClassroom "+now)
    return Response(json.dumps(data), mimetype='application/json')



@app.route('/vpnHotBook', methods=['post', 'get'])
@allow_cross_domain
def get_vpnHotBook():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    h = vpnlibrary.HotBook()
    data, vpn_account = h.getHotBook()
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'] + " vpnHotBook "+now)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnBookList', methods=['post'])
@allow_cross_domain
def get_vpnBookList():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bl = vpnlibrary.Book_list()
    data, vpn_account = bl.getList(request.form['bookName'])
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'] + " vpnBookList "+now)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnBookDetail', methods=['post'])
@allow_cross_domain
def get_vpnBookDetail():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bl = vpnlibrary.BookItem()
    data, vpn_account = bl.getBook(request.form['bookUrl'])
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'] + " vpnBookDetail "+now)
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/vpnBookTop100', methods=['post','get'])
@allow_cross_domain
def get_vpnBookTop100():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    d = vpnlibrary.RecommendBook()
    data, vpn_account = d.get_top_100()
    r.rpush("vpn_account", vpn_account)
    print(vpn_account['username'] + " vpnBookTop100 "+now)
    return Response(json.dumps(data), mimetype='application/json')
@app.route("/apk/getApkInfo", methods=['GET'])
@allow_cross_domain
def download_apk_info():
    data=db_util.get_download_apk_info()
    return jsonify(data)
@app.route("/apk/download/<filename>", methods=['GET'])
@allow_cross_domain
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = r'/var/www/apk'
    data = db_util.get_download_apk_info()
    serverVersion=data['info']['serverVersion']
    new_fileName=filename+serverVersion+r'.apk'
    return send_from_directory(directory, new_fileName, as_attachment=True)
@app.route('/apk/upload',methods=['POST'],strict_slashes=False)
@allow_cross_domain
def upload():
    f = request.files['file']
    fname=secure_filename(f.filename)
    if allowed_file(fname):
        upload_path = os.path.join(r'/var/www/apk',secure_filename(f.filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        print(secure_filename(f.filename))
        token = base64.b64encode(secure_filename(f.filename).encode('utf-8'))
        return jsonify(response_info.success('上传成功',str(token)))
    else:
        return jsonify(response_info.error('801','文件类型不符合要求',''))
@app.route('/apk/updateInfo',methods=['POST'])
@allow_cross_domain
def app_download_info_update():
    download_info = request.get_json()
    data=db_util.update_download_apk_info(download_info)
    return jsonify(data)
if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
