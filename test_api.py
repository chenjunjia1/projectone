import time
import unittest
import json
import requests
from web3 import Web3
from eth_account import Account
import allure


class TestAPIs(unittest.TestCase):

    def get_login_headers(self):
        return {
            "Appver": "1.0.0",
            "Osver": "1.0.0",
            "Plat": "pc",
            "Content-Type": "application/json",
            "Authorization": ""
        }

    def get_access_token(self):
        login_url = "https://dev-xplus.trytryc.com/im/api/user/login/address"
        login_headers = self.get_login_headers()

        address = "0x76d9b67e28434de73de066c17c72c648451ecce2"
        timestamp = int(time.time())
        msg = f"Welcome to Xplus Meteor Portal.\nPlease sign this message to login Xplus Meteor Portal.\n\nTimestamp:{timestamp}"
        private_key = "3dd462192a5a84f348300f5c6a0d08853a329ed56d6eb45bd4294abc0ddff9f4"  # Replace with your private key

        w3 = Web3()
        acct = Account().from_key(private_key)

        eth_message = f"\x19Ethereum Signed Message:\n{len(msg)}{msg}"
        message_hash = w3.keccak(text=eth_message)

        signature = w3.eth.account.signHash(message_hash, private_key=acct.key)

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

    def call_second_api(self, access_token):
        if access_token is None:
            return

        detail_url = "https://dev-xplus.trytryc.com/im/api/dapp/community/list"
        detail_headers = self.get_detail_headers(access_token)

        detail_data = {"tag":"","communityType":1,"pageNum":1,"pageSize":100,"orderBy":1,"prePageLastFollowerNum":"","prePageLastId":""}

        detail_response = requests.post(detail_url, headers=detail_headers, json=detail_data)

        if detail_response.status_code == 200:
            detail_result = detail_response.json()
            allure.attach("Detail Response", json.dumps(detail_result), allure.attachment_type.JSON)
            return detail_result
        else:
            allure.attach("Detail Response", detail_response.text, allure.attachment_type.TEXT)
            raise AssertionError(f"Failed to make detail request: {detail_response.status_code}")

    def get_detail_headers(self, access_token):
        return {
            "Appver": "1.0.0",
            "Osver": "1.0.0",
            "Plat": "pc",
            "Content-Type": "application/json",
            "Authorization": access_token
        }

    @allure.feature("API Testing")
    @allure.story("Test API Login and Signature")
    def test_example(self):  # Renamed the test method
        access_token = self.get_access_token()
        self.assertIsNotNone(access_token, "Failed to obtain access token")
        print("Access Token:", access_token)

        with allure.step("Call Second API"):
            response = self.call_second_api(access_token)
            self.assertIsNotNone(response, "Failed to call second API")
            print("Second API Response:", response)
            # 添加一个Allure步骤来记录返回内容
            allure.attach("Second API Response", json.dumps(response), allure.attachment_type.JSON)


if __name__ == "__main__":
    unittest.main()
