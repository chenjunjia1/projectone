import time
import json
import requests
import unittest
import allure
from web3 import Web3
from eth_account import Account
import warnings
import webbrowser  # 导入webbrowser库

warnings.filterwarnings("ignore", category=DeprecationWarning, module="eth_utils")


class TestAPIs(unittest.TestCase):

    def setUp(self):
        self.base_url = "https://dev-xplus.trytryc.com"
        self.address = "0x460a6603418b26a9968a0687e2c19dead9c94dd6"
        self.private_key = "361e8eed934170511e8d0fd1ae3d71f1996fc529aceeba202d2ca67e484cc4c4"  # 请替换成您的私钥

    def get_login_headers(self):
        return {
            "Appver": "1.0.0",
            "Osver": "1.0.0",
            "Plat": "pc",
            "Content-Type": "application/json",
            "Authorization": ""
        }

    def get_access_token(self):
        login_url = f"{self.base_url}/im/api/user/login/address"
        login_headers = self.get_login_headers()

        timestamp = int(time.time())
        msg = f"Welcome to Xplus Meteor Portal.\nPlease sign this message to login Xplus Meteor Portal.\n\nTimestamp:{timestamp}"

        w3 = Web3()
        acct = Account().from_key(self.private_key)

        eth_message = f"\x19Ethereum Signed Message:\n{len(msg)}{msg}"
        message_hash = w3.keccak(text=eth_message)

        signature = w3.eth.account.signHash(message_hash, private_key=acct.key)

        data = {
            "address": self.address,
            "msg": msg,
            "signature": signature.signature.hex(),
        }

        response = requests.post(login_url, headers=login_headers, json=data)

        if response.status_code == 200:
            login_result = response.json()
            access_token = login_result.get("data", {}).get("bearerToken", "")
            allure.attach("Access Token", access_token, allure.attachment_type.TEXT)  # 添加 Allure 报告附件
            return access_token
        else:
            raise AssertionError(f"Failed to make login request: {response.status_code}")

    def get_user_info_headers(self):
        access_token = self.get_access_token()
        return {
            "Appver": "1.0.0",
            "Osver": "1.0.0",
            "Plat": "pc",
            "Content-Type": "application/json",
            "Authorization": access_token
        }

    @allure.feature("API Testing")
    @allure.story("Test API User Info")
    def test_get_user_info(self):
        user_info_url = f"{self.base_url}/im/api/user/info"
        user_info_headers = self.get_user_info_headers()

        response = requests.get(user_info_url, headers=user_info_headers)

        if response.status_code == 200:
            user_info_result = response.text
            allure.attach("User Info Response", user_info_result, allure.attachment_type.TEXT)  # 添加 Allure 报告附件
            print("User Info:")
            print(user_info_result)
        else:
            self.fail(f"Failed to get user info: {response.status_code}")

    def open_allure_report(self):
        report_url = "http://192.168.2.127:5252/"
        webbrowser.open(report_url)


if __name__ == "__main__":
    unittest.main()

