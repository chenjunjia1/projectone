import time
import unittest
import json
import requests
from web3 import Web3
from eth_account import Account
import allure
import logging


class TestAPIs(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # 创建一个文件日志处理程序
        file_handler = logging.FileHandler('test_log.log')
        file_handler.setLevel(logging.INFO)

        # 创建一个控制台日志处理程序
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建一个日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理程序到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_login_headers(self):
        return {
            "Appver": "1.0.0",
            "Osver": "1.0.0",
            "Plat": "pc",
            "Content-Type": "application/json",
            "Authorization": ""
        }

    def generate_random_wallet(self):
        w3 = Web3()
        acct = w3.eth.account.create()

        return acct.address, acct.key.hex()

    def get_access_token(self):
        login_url = "https://dev-xplus.trytryc.com/im/api/user/login/address"
        login_headers = self.get_login_headers()

        address, private_key = self.generate_random_wallet()

        timestamp = int(time.time())
        msg = f"Welcome to Xplus Meteor Portal.\nPlease sign this message to login Xplus Meteor Portal.\n\nTimestamp:{timestamp}"

        w3 = Web3()

        eth_message = f"\x19Ethereum Signed Message:\n{len(msg)}{msg}"
        message_hash = w3.keccak(text=eth_message)

        signature = w3.eth.account.signHash(message_hash, private_key=private_key)

        data = {
            "address": address,
            "msg": msg,
            "signature": signature.signature.hex(),
        }

        response = requests.post(login_url, headers=login_headers, json=data)

        if response.status_code == 200:
            login_result = response.json()
            allure.attach("Login Response", json.dumps(login_result), allure.attachment_type.JSON)
            access_token = login_result.get("data", {}).get("bearerToken", "")
            return access_token
        else:
            allure.attach("Login Response", response.text, allure.attachment_type.TEXT)
            raise AssertionError(f"Failed to make login request: {response.status_code}")

    @allure.feature("API Testing")
    @allure.story("Test API Login and Signature")
    def test_get_access_token(self):
        self.logger.info("Starting the test_get_access_token test.")
        access_token = self.get_access_token()
        self.assertIsNotNone(access_token, "Failed to obtain access token")
        self.logger.info("Access token obtained: %s", access_token)


if __name__ == "__main__":
    unittest.main()
