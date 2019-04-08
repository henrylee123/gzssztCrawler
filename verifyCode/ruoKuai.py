from hashlib import md5
import requests
import retrying
import time
"""
若快，一个验证码识别平台
"""
# 用户名
user_name = "henrylee"
# 密码
pwd  = "zhangheng2"
# 软件号
softid = 70021
# 软件key
softkey = "dcefe229cb9b4e1785b48fbc3525d011"
# 头文件
header = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }
# request引擎
agent = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        ]
# api
ruokuai_api_url = 'http://api.ruokuai.com/create.json'


# 重试异常
class VerifyFailException(Exception):
    pass

# 若快验证码模块
class RuoKuai:

    """
    若快验证码识别模块
    """
    def __init__(self, username=user_name, password=pwd, soft_id=softid,
                 soft_key=softkey, header=header,
                 agent=agent, ruokuai_api_url=ruokuai_api_url):
        """
        初始化验证码识别模块
        :param username: 用户名
        :param password: 密码
        :param soft_id:  内部变量（不变）=        :param soft_key: 内部变量（不变）
        :param path:     保存本地文件路径
        """
        self.username = username
        self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        # 传递参数
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = header
        self.agent = agent
        self.ruokuai_api_url = ruokuai_api_url

    def get_verify_code(self):
        r = requests.post(self.ruokuai_api_url, data=self.params, files=self.files, headers=self.headers)
        respond_json = r.json()
        if 'Result' not in respond_json:
            print("若快识别失败，1秒后更换验证码再次尝试")
            time.sleep(1)
            raise VerifyFailException
        return respond_json['Result']

    def load_img(self, im, im_type=3050, timeout=10):
        """
        im: 图片字节
        im_type: 题目类型,若快网站上查，收费不。4位验证码为2040
        """
        self.params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        self.params.update(self.base_params)
        self.files = {'image': ('a.jpg', im)}


if __name__ =="__main__":
    rk = RuoKuai()
    with open(r"C:\Users\Admin\Desktop\电商网站\唯品会\验证码\ffhm.png", "rb") as f:
        a = f.read()
    rk.load_img(a)
    result = rk.get_verify_code()
    print(result)

