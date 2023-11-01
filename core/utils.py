import hashlib
import random, string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def _pad(s):
    try:
        return pad(s, AES.block_size, style='pkcs7')
    except Exception:
        return None

def _unpad(s):
    try:
        return unpad(s, AES.block_size, style='pkcs7')
    except Exception:
        return None

def AesDecrypt(key, data, mode='ECB'):
    key = hashlib.md5(key).hexdigest()[:16].encode()
    if mode == 'CBC':
        cipher = AES.new(key, AES.MODE_CBC, iv=b'\0'*16, use_aesni=True)
    else:
        cipher = AES.new(key, AES.MODE_ECB, use_aesni=True)
    dec = cipher.decrypt(data)
    return dec

def AesEncrypt(key, data, mode='ECB'):
    key = hashlib.md5(key).hexdigest()[:16].encode()
    if mode == 'CBC':
        cipher = AES.new(key, AES.MODE_CBC, iv=b'\0'*16, use_aesni=True)
    else:
        cipher = AES.new(key, AES.MODE_ECB, use_aesni=True)
    data = _pad(data)
    return cipher.encrypt(data)

def randstr(length, hasdigit=True):
    if hasdigit:
        letters = string.ascii_letters+string.digits
    else:
        letters = string.ascii_letters
    return ''.join(random.choices(letters, k=length))

