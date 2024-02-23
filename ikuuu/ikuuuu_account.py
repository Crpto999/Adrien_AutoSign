import sys
import requests
import os
import re
from lxml import html

def main():
    r = 1
    oy = ql_env()
    print(oy)
    messages = []  # Create an empty list to collect messages
    for i in oy:
        print("------------正在执行第" + str(r) + "个账号----------------")
        email = i.split('&')[0]
        passwd = i.split('&')[1]
        result = sign_in(email, passwd)
        print(email,passwd)
        messages.append(f"账户：{email}\n{result}")  # Add the message to the list
        r += 1
    send_to_telegram(messages)  # Pass the list of messages to send_to_telegram

def sign_in(email, passwd):
    try:
        body = {"email": email, "passwd": passwd}
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        with requests.Session() as session:
            session.post(f'https://ikuuu.pw/auth/login', headers=headers, data=body)
        
            homepage_response = session.get('https://ikuuu.pw/user')
            page_content = homepage_response.text
            tree = html.fromstring(page_content)
            # 当月剩余
            left_elements = tree.xpath('/html/body/div[1]/div/div[3]/section/div[3]/div[2]/div/div[2]/div[2]/span')
            for left_element in left_elements:
                left = left_element.text_content().strip()
        
            # 今日已用
            today_use_elements = tree.xpath(
                '/html/body/div[1]/div/div[3]/section/div[3]/div[2]/div/div[2]/div[3]/div/nav/ol/li')
            for today_use_element in today_use_elements:
                today_use = today_use_element.text_content().strip()
                today_use = re.sub(r'\s+', ' ', today_use)
        
            # 会员时长
            member_elements = tree.xpath(
                '/html/body/div[1]/div/div[3]/section/div[3]/div[1]/div/div[2]/div[2]/span')
            if member_elements:
                member_elements = member_elements
                for member_element in member_elements:
                    member = member_element.text_content().strip()
                    member = re.sub(r'\s+', ' ', member)
                    member = f"{member}天"
                expires = tree.xpath(
                    '/html/body/div[1]/div/div[3]/section/div[3]/div[1]/div/div[3]/div/nav/ol/li')
                expires = expires
                for expire in expires:
                    expire = expire.text_content().strip()
                    expire = re.sub(r'\s+', ' ', expire)
            else:
                # 如果没有找到left_elements，使用备用的XPath表达式
                backup_member = tree.xpath(
                    '/html/body/div[1]/div/div[3]/section/div[3]/div[1]/div/div[2]/div[2]')
                member_elements = backup_member
                for member_element in member_elements:
                    member = member_element.text_content().strip()
                    member = re.sub(r'\s+', ' ', member)
                expire ="免费版: 2099-12-30 过期"
        
            ss = session.post(f'https://ikuuu.pw/user/checkin').json()
            if 'msg' in ss:
                sr = ss['msg']
        
            mes = f"{sr}\n\n{expire}\n会员剩余时长: {member}\n当月剩余流量: {left}GB\n{today_use}"
        return mes
    except Exception as e:
        return f'请检查帐号配置是否错误：{str(e)}'

def ql_env():
    if "IKUUU_ACCOUNTS" in os.environ:
        token_list = os.environ['IKUUU_ACCOUNTS'].split('#')
        if len(token_list) > 0:
            return token_list
        else:
            print("IKUUU_ACCOUNTS变量未启用")
            sys.exit(1)
    else:
        print("未添加IKUUU_ACCOUNTS变量")
        sys.exit(0)

def send_to_telegram(messages):
    if "TELEGRAM_BOT_TOKEN" in os.environ and "TELEGRAM_CHAT_ID" in os.environ:
        bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
        text = "\n————————————————\n".join(messages)  # Join the messages with separator
        formatted_message = f"*🚀 [ikuuu] 签到完成*\n\n\n{text}\n"  # 使用Markdown格式
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": formatted_message,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Telegram 消息发送成功")
        else:
            print("Telegram 消息发送失败")
    else:
        print("未配置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")

if __name__ == '__main__':
    main()
