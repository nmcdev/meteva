#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: ftpconn.py

'''
Created on Oct 13, 2020

@author: anduin
'''

from ftplib import FTP
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urlencode
import socket

try:
    import ssl
except ImportError:
    _SSLSocket = None
else:
    _SSLSocket = ssl.SSLSocket

from .loglib import *

class FtpConn():
    @staticmethod
    def joinUrl(url, path):
        return urljoin(url, path)
    
    @staticmethod
    def getPath(url):
        try:
            if url.lower().find(r'ftp://') == 0:
                return urlparse(url).path
            else:
                return url
        except Exception as data:
            LogLib.logger.error('getPath except ' + str(data))
            #print(data)
            return None

    def __init__(self, host, port=21):
        """ 初始化 FTP 客户端
        参数:
            host:ip地址
            port:端口号
        """
        # print("__init__()---> host = %s ,port = %s" % (host, port))
        self.host = host
        self.port = port
        self.ftp = FTP()
        # 重新设置下编码方式
        self.ftp.encoding = 'gbk'
        self.file_list = []
        self.default_bufsize = 1024*64

    def login(self, username, password, pasv=False):
        """ 初始化 FTP 客户端
            参数:
                  username: 用户名

                 password: 密码
            """
        try:
            timeout = 60
            socket.setdefaulttimeout(timeout)
            # 0主动模式 1 #被动模式
            LogLib.logger.debug('login set_pasv %s ' % str(pasv))
            self.ftp.set_pasv(pasv)
            # 打开调试级别2，显示详细信息
            # self.ftp.set_debuglevel(2)

            #print('开始尝试连接到 %s' % self.host)
            LogLib.logger.debug('login connect %s  %d' % (self.host, self.port))
            self.ftp.connect(self.host, self.port)
            #print('成功连接到 %s' % self.host)

            #print('开始尝试登录到 %s' % self.host)
            LogLib.logger.debug('login login %s' % (username))
            self.ftp.login(username, password)
            #print('成功登录到 %s' % self.host)

            #print(self.ftp.welcome)
            LogLib.logger.debug('login over %s %s' % (self.host, username))

            return True
        except Exception as data:
            #self.deal_error("FTP 连接或登录失败 ，错误描述为：%s" % data)
            LogLib.logger.error('login except %s %s %s' % (self.host, username, str(data)))
            
            return False
        
    def quit(self):
        try:
            self.ftp.quit()
        except:
            pass

    def get_rfile_size(self, remote_file):
        """获取远程文件大小
           参数:
             remote_file: 远程文件
             如果remote_file是全路径ftp://abc.com/ddd/dd；
             如果remote_file是相对路径，必须是相对于当前路径abc/aa，或者根路径/abc/aa。
             如果remote_file仅仅是文件名，当前路径必须是该文件所在的目录；
        """
        try:
            fpath = FtpConn.getPath(remote_file)
            if fpath is None:
                return -2

            self.ftp.voidcmd('TYPE I')
            return self.ftp.size(fpath)
        except Exception as sdata:
            #print("get_rfile_size() 错误描述为：%s" % sdata)
            LogLib.logger.error('get_rfile_size except %s %s' % (remote_file, str(sdata)))

            return -1

    def is_same_size(self, local_file, remote_file):
        """判断远程文件和本地文件大小是否一致

           参数:
             local_file: 本地文件
             remote_file: 远程文件
        """
        remote_file_size = 0
        local_file_size = 0

        try:
            remote_file_size = self.get_rfile_size(remote_file) if type(remote_file) is str else remote_file
        except Exception as sdata:
            # print("is_same_size() 错误描述为：%s" % sdata)
            LogLib.logger.error('is_same_size except %s %s' % (remote_file, str(sdata)))

            return -1
            #remote_file_size = -1

        try:
            local_file_size = os.path.getsize(local_file) if os.path.exists(local_file) else -1
        except Exception as fdata:
            # print("is_same_size() 错误描述为：%s" % fdata)
            LogLib.logger.error('is_same_size except %s %s' % (local_file, str(sdata)))

            return -2
            #local_file_size = -1

        #print('local_file_size:%d  , remote_file_size:%d' % (local_file_size, remote_file_size))
        if remote_file_size == local_file_size:
            return 1
        else:
            return 0

    def download_file(self, local_file, remote_file):
        """从ftp下载文件
            参数:
                local_file: 本地文件
                remote_file: 远程文件
        """
        #print("download_file()---> local_path = %s ,remote_path = %s" % (local_file, remote_file))
        LogLib.logger.info('download_file start %s %s' % (local_file, remote_file))
        nrst = self.is_same_size(local_file, remote_file)
        if nrst > 0:
            #print('%s 文件大小相同，无需下载' % local_file)
            LogLib.logger.info('download_file 文件大小相同，无需下载 %s %s' % (local_file, remote_file))
            return True
        elif nrst < 0:
            return False
        else:
            try:
                #print('>>>>>>>>>>>>下载文件 %s ... ...' % local_file)
                LogLib.logger.info('download_file downloading %s %s' % (local_file, remote_file))
                buf_size = self.default_bufsize
                with open(local_file, 'wb') as file_handler:
                    self.ftp.retrbinary('RETR %s' % remote_file, file_handler.write, buf_size)
                #file_handler.close()

                LogLib.logger.info('download_file download over %s %s' % (local_file, remote_file))

                return True
            except Exception as data:
                #print('下载文件出错，出现异常：%s ' % err)
                LogLib.logger.error('download_file except %s %s %s' % (local_file, remote_file, str(data)))

                return False
            
    def download_file_to_buf(self, remote_file):
        """从ftp下载文件内容，不保存文件，将数据直接返回，不建议处理大文件
            参数:
                remote_file: 远程文件
        """
        #print("download_file_to_buf()---> remote_path = %s" % (remote_file))
        LogLib.logger.info('download_file_to_buf start %s' % (remote_file))
        fsize = self.get_rfile_size(remote_file)
        if fsize < 0:
            LogLib.logger.error('download_file_to_buf get_rfile_size %s' % (remote_file))
            return False, None
        elif fsize == 0:
            return True, None
        else:
            try:
                #print('>>>>>>>>>>>>下载文件 %s ... ...' % local_file)
                LogLib.logger.info('download_file_to_buf downloading %s' % (remote_file))
                self.ftp.voidcmd('TYPE I')

                down_size = 0
                down_data = None
                with self.ftp.transfercmd('RETR %s' % remote_file, 0) as conn:
                    while down_size < fsize:
                        buf_size = self.default_bufsize
                        if fsize - down_size < buf_size:
                            buf_size = fsize - down_size

                        rdata = conn.recv(buf_size)
                        if rdata:
                            down_size += len(rdata)
                            if down_data is None:
                                down_data = rdata
                            else:
                                down_data += rdata
                        else:
                            break
                        
                    # shutdown ssl layer
                    if _SSLSocket is not None and isinstance(conn, _SSLSocket):
                        conn.unwrap()

                resp = self.ftp.voidresp()

                if fsize != down_size:
                    LogLib.logger.error('download_file_to_buf download over,but size error %s %s' % (remote_file, str(resp)))
                    return False, None
                else:
                    LogLib.logger.info('download_file_to_buf download over %s %s' % (remote_file, str(resp)))
                    return True, down_data
            except Exception as data:
                #print('下载文件出错，出现异常：%s ' % err)
                LogLib.logger.error('download_file_to_buf except %s %s' % (remote_file, str(data)))

                return False, None

    def download_file_tree(self, local_path, remote_path):
        """从远程目录下载多个文件到本地目录
                       参数:
                         local_path: 本地路径

                         remote_path: 远程路径
                """
        print("download_file_tree()--->  local_path = %s ,remote_path = %s" % (local_path, remote_path))
        try:
            self.ftp.cwd(remote_path)
        except Exception as err:
            print('远程目录%s不存在，继续...' % remote_path + " ,具体错误描述为：%s" % err)
            return

        if not os.path.isdir(local_path):
            print('本地目录%s不存在，先创建本地目录' % local_path)
            os.makedirs(local_path)

        print('切换至目录: %s' % self.ftp.pwd())

        self.file_list = []
        # 方法回调
        self.ftp.dir(self.get_file_list)

        remote_names = self.file_list
        print('远程目录 列表: %s' % remote_names)
        for item in remote_names:
            file_type = item[0]
            file_name = item[1]
            local = os.path.join(local_path, file_name)
            if file_type == 'd':
                print("download_file_tree()---> 下载目录： %s" % file_name)
                self.download_file_tree(local, file_name)
            elif file_type == '-':
                print("download_file()---> 下载文件： %s" % file_name)
                self.download_file(local, file_name)
            self.ftp.cwd("..")
            print('返回上层目录 %s' % self.ftp.pwd())
        return True

    def upload_file(self, local_file, remote_file_catalog,record_abspath,remote_file_catalog_r):
        """从本地上传文件到ftp
           参数:
             local_path: 本地文件
             remote_path: 远程文件
        """
        exe_status = {}
        # 创建一个字典表，key是文件时次,values是文件名称。
        if os.path.exists(record_abspath):
            with open(record_abspath, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    #print("line:{}".format(line))
                    shici,filenames_local,wenjian_time,upload_time = line.split(',')
                    exe_status[shici] = filenames_local
        #上传的文件名称
        filenames = local_file.split('/')[-1]
        times = filenames.split(".")[1]
        print(filenames,times)
        #if not os.path.exists(remote_file):
        #    self.ftp.mkd(remote_file)
        remote_file = os.path.join(remote_file_catalog,filenames)
        print(remote_file,local_file)
        if not os.path.isfile(local_file):
            print('%s 不存在' % local_file)
            return
        #需要修改代码，做成是否能够对应上字典表
        # 日志记录中有对应文件执行信息不再执行
        if filenames in exe_status.get(times, ''):
            print("已经存在")
            return
        
        #print("目录文件：{}".format(self.ftp.nlst(remote_file_catalog_r)))
        #print(remote_file_catalog)
        try:
            if remote_file_catalog in self.ftp.nlst(remote_file_catalog_r):
                pass
            else:
                self.ftp.mkd(remote_file_catalog)
        except:
            self.ftp.mkd(remote_file_catalog_r)
        #if not os.path.exists(local_file):
        #    os.makedirs(local_file)
        buf_size = 1024
        #获取文件时间
        t = os.path.getctime(local_file)
        file_time = str(datetime.datetime.fromtimestamp(t)).split('.')[0]
        #print(dir_t,type(dir_t))
        #file_time = time.strptime(dir_t, "%Y-%m-%d %H:%M:%S")
        file_handler = open(local_file, 'rb')
        self.ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
        print("上传成功")
        file_handler.close()
        #上传文件时间
        time_now = time.localtime()
        date_now = str(time.strftime('%Y-%m-%d %H:%M:%S', time_now)).split(".")[0]
        text = times + ',' + filenames + ',' + file_time + ',' + date_now + '\n'
        #将日志信息写进log里边。
        print(record_abspath)
        with open(record_abspath, 'a') as f_w:
            f_w.write(text)
        #print(text)

    def upload_file_tree(self, local_path, remote_path):
        """从本地上传目录下多个文件到ftp
           参数:

             local_path: 本地路径

             remote_path: 远程路径
        """
        if not os.path.isdir(local_path):
            #print('本地目录 %s 不存在' % local_path)
            return
        """
        创建服务器目录
        """
        try:
            self.ftp.cwd(remote_path)  # 切换工作路径
        except Exception as e:
            base_dir, part_path = self.ftp.pwd(), remote_path.split('/')
            part_path.append("00")
            for p in part_path[1:-1]:
                base_dir = base_dir + p + '/'  # 拼接子目录
                #print("拼接子目录")
                print(base_dir)
                try:
                    self.ftp.cwd(base_dir)  # 切换到子目录, 不存在则异常
                except Exception as e:
                    print('INFO:', e)
                    self.ftp.mkd(base_dir)  # 不存在创建当前子目录
                    zi_dir = base_dir + '00'+ '/'
                    self.ftp.mkd(zi_dir)
        #self.ftp.cwd(remote_path)
        print('切换至远程目录: %s' % self.ftp.pwd())

        local_name_list = os.listdir(local_path)
        print('本地目录list: %s' % local_name_list)
        #print('判断是否有服务器目录: %s' % os.path.isdir())

        for local_name in local_name_list:
            src = os.path.join(local_path, local_name)
            print("src路径=========="+src)
            if os.path.isdir(src):
                try:
                    self.ftp.mkd(local_name)
                except Exception as err:
                    print("目录已存在 %s ,具体错误描述为：%s" % (local_name, err))
                print("upload_file_tree()---> 上传目录： %s" % local_name)
                print("upload_file_tree()---> 上传src目录： %s" % src)
                self.upload_file_tree(src, local_name)
            else:
                print("upload_file_tree()---> 上传文件： %s" % local_name)
                self.upload_file(src, local_name)
        self.ftp.cwd("..")

    def close(self):
        """ 退出ftp
        """
        #print("close()---> FTP退出")
        self.ftp.quit()

    def get_file_list(self, line):
        """ 获取文件列表
            参数：
                line：
        """
        file_arr = self.get_file_name(line)
        # 去除  . 和  ..
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)

    def get_file_name(self, line):
        """ 获取文件名
            参数：
                line：
        """
        pos = line.rfind(':')
        while (line[pos] != ' '):
            pos += 1
        while (line[pos] == ' '):
            pos += 1
        file_arr = [line[0], line[pos:]]
        return file_arr
if __name__ == '__main__':
    import os
    workdir = os.path.dirname(__file__)
    workdir = os.path.dirname(workdir)
    logdir = os.path.join(workdir, 'testftpconn')
    if not os.path.exists(logdir):
        os.mkdir(logdir)

    LogLib.init()
    LogLib.addTimedRotatingFileHandler(os.path.join(logdir, 'testftpconn.log'))
    LogLib.logger.setLevel(logging.DEBUG)
    
    ftpobj = FtpConn('ftp.sjtu.edu.cn')
    if ftpobj.login('', ''):
        rst, fdata = ftpobj.download_file_to_buf(r'/pub/software/vmlinuz')
        if rst and fdata is not None:
            with open(r'c:\workdoc\a.test', 'wb') as f:
                f.write(fdata)

    LogLib.uninit()

    print('test done')