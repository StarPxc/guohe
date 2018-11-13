import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from util.public_var import publicVar


p=publicVar()
receiver_list = ['2955317305@qq.com', 'yueyong1030@outlook.com','764412552@qq.com']  # 收件人邮箱账号，


def send_mail(comment):
    try:
        msg = MIMEText(comment, 'plain', 'utf-8')
        msg['From'] = formataddr(["果核反馈信息", p.MY_SENDER])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["收件人", ",".join(receiver_list)])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "果核反馈信息"  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
        server.login(p.MY_SENDER, p.MY_PASS)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(p.MY_SENDER, receiver_list, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print("邮件发送成功")
    except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(e)
        print("邮件发送失败")


if __name__ == '__main__':
    send_mail("测试")
