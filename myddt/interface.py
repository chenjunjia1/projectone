import time
import json
import requests
import unittest
import allure
from web3 import Web3
from eth_account import Account
import random
class TestAPIs(unittest.TestCase):

    def setUp(self):
        self.base_url = "https://dev-xplus.trytryc.com"
        self.address = "0x460a6603418b26a9968a0687e2c19dead9c94dd6"
        self.private_key = "361e8eed934170511e8d0fd1ae3d71f1996fc529aceeba202d2ca67e484cc4c4"

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
            allure.attach("Access Token", access_token, allure.attachment_type.TEXT)
            return access_token
        else:
            raise AssertionError(f"登录请求失败: {response.status_code}")

    def get_user_info_headers(self):
        access_token = self.get_access_token()
        return {
            "Appver": "1.0.0",
            "Osver": "1.0.0",
            "Plat": "pc",
            "Content-Type": "application/json",
            "Authorization": access_token
        }

    @allure.feature("API Test")
    @allure.story("获取用户信息")
    def test_get_user_info(self):
        user_info_url = f"{self.base_url}/im/api/user/info"
        user_info_headers = self.get_user_info_headers()

        response = requests.get(user_info_url, headers=user_info_headers)

        if response.status_code == 200:
            user_info_result = response.text
            allure.attach("用户信息响应", user_info_result, allure.attachment_type.TEXT)
            print("用户信息:")
            print(user_info_result)
        else:
            self.fail(f"获取用户信息失败: {response.status_code}")

    @allure.feature("API Test")
    @allure.story("获取社区列表")
    def test_get_community_list(self):
        community_list_url = f"{self.base_url}/im/api/dapp/community/list"
        community_list_headers = self.get_user_info_headers()
        data = {"tag": "", "communityType": 2, "pageNum": 1, "pageSize": 100, "orderBy": 1,
                "prePageLastFollowerNum": "", "prePageLastId": ""}

        response = requests.post(community_list_url, headers=community_list_headers, json=data)

        if response.status_code == 200:
            community_list_result = response.text
            allure.attach("社区列表响应", community_list_result, allure.attachment_type.TEXT)
            print("社区列表:")
            print(community_list_result)
        else:
            self.fail(f"获取社区列表失败: {response.status_code}")

    @allure.feature("API 测试")
    @allure.story("获取账户列表")
    def test_get_account_list(self):
        account_list_url = f"{self.base_url}/asset/api/account/list"
        account_list_headers = self.get_user_info_headers()

        response = requests.get(account_list_url, headers=account_list_headers)

        if response.status_code == 200:
            account_list_result = response.text
            allure.attach("账户列表响应", account_list_result, allure.attachment_type.TEXT)
            print("账户列表:")
            print(account_list_result)
        else:
            self.fail(f"获取账户列表失败: {response.status_code}")

    def publish_feed(self, content_type, text_value=None):
        publish_url = f"{self.base_url}/feed/api/feed/publish"
        publish_headers = self.get_user_info_headers()

        if content_type == 1:
            # 纯文本，生成随机数内容
            if text_value is None:
                text_value = str(random.randint(1, 10))

            params = {
                "communityId": "1703716175583776768",
                "contentType": 1,
                "text": text_value,
                "subscriptionIds": []
            }
        elif content_type == 2:
            # 文本+图片
            if text_value is None:
                text_value = str(random.randint(1, 10))

            params = {
                "communityId": "1703716175583776768",
                "contentType": 2,
                "text": f"{text_value}+图片",
                "images": ["https://xplus-img.trytryc.com/img/2023-09-18/0437bf5c-7c0c-4408-942f-7aca4acca0ed.jpeg"],
                "subscriptionIds": []
            }
        elif content_type == 3:
            # 文本+视频
            if text_value is None:
                text_value = str(random.randint(1, 10))

            params = {"communityId": "1703716175583776768",
                      "contentType": 3,
                      "text": f"{text_value}+视频",
                      "video": "https://xplus-img.trytryc.com/2023-09-19/d5d3a3e3-79da-4398-816e-6f4041f7a78e.mp4",
                      "videoThumbnail": "https://xplus-img.trytryc.com/img/2023-09-19/129e174c-1668-41b9-8816-a10f0d4d6799.png",
                      "subscriptionIds": []}
        else:
            raise ValueError("Invalid contentType value")

        response = requests.post(publish_url, headers=publish_headers, json=params)

        if response.status_code == 200:
            publish_result = response.text
            allure.attach("发布Feed响应", publish_result, allure.attachment_type.TEXT)
            print(f"发布Feed结果(contentType={content_type}, text={text_value}):")
            print(publish_result)
        else:
            self.fail(f"发布Feed失败(contentType={content_type}, text={text_value}): {response.status_code}")

    @allure.feature("API 测试")
    @allure.story("发布Feed - 纯文本")
    def test_publish_feed_text(self):
        self.publish_feed(content_type=1)

    @allure.feature("API 测试")
    @allure.story("发布Feed - 文本+图片")
    def test_publish_feed_text_image(self):
        self.publish_feed(content_type=2)

    @allure.feature("API 测试")
    @allure.story("发布Feed - 文本+视频")
    def test_publish_feed_text_video(self):
        self.publish_feed(content_type=3)


if __name__ == "__main__":
    unittest.main()
