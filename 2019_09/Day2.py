import execjs
import requests


class FangTX:

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            "Origin": "https://passport.fang.com",
            "Referer": "https://passport.fang.com/"
        }

    def login(self, username, password, auto_login=1):
        '''
        :param username:  账户名
        :param password:  密码
        :param auto_login:  是否自动登录 0为否 1为是
        :return:
        '''
        api = "https://passport.fang.com/login.api"
        password = self._get_encrypt_password(password)
        headers = self.headers.copy()
        data = {
            "uid": username,
            "pwd": password,
            "Service": "soufun-passport-web",
            "AutoLogin": auto_login
        }
        result = self.session.post(url=api, data=data, headers=headers).json()
        print(result)

    def _get_encrypt_password(self, password):
        if not hasattr(self, "ctx"):
            self._get_ctx()

        return self.ctx.call("getPassword", password)

    def _get_ctx(self):
        # ./a.js就是复制下来的js文件
        js_code = ""
        with open("./a.js", "r", encoding="utf-8") as f:
            for line in f:
                js_code += line
        self.ctx = execjs.compile(js_code)

    def test(self):
        self.login("18716758177", "123456")
        pass


if __name__ == '__main__':
    ftx = FangTX()
    ftx.test()
