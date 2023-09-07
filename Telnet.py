"""
/Telnet.py
封装telnetlib, 提供telnet连接、登录、下发命令行、读取回显等操作
"""
import sys
import telnetlib
import logging
import const


class TelnetLib(object):

    def __init__(self):
        self.tn = None
        self.EXIT = b'quit\n'
        self.LOGIN = b'Login'
        self.USERNAME = b'Username:'
        self.PASSWORD = b'Password:'

    @staticmethod
    def format(data):
        return data.encode('UTF-8') + b'\n'

    def link(self, host, port=23, timeout=3):
        # 连接设备
        logging.info("{}:{} Telnet连接中...".format(host, port))
        self.tn = telnetlib.Telnet(host, port, timeout)

    # new login: 登录串口/管理口，并进入诊断视图
    def login(self, username, password):
        logging.info('登录中...')
        self.tn.write(self.format('\r'))
        while True:
            index, match, data = self.tn.expect([self.USERNAME, self.PASSWORD, rb'\[Y/N\]', const.DIGENDS, const.SYSENDS, const.USRENDS], timeout=3)
            if index == 0:
                logging.info(f'Username: {username}')
                self.tn.write(self.format(username))
            elif index == 1:
                logging.info(f'Password: {password}')
                self.tn.write(self.format(password))
            elif index == 2:
                logging.warning(data.decode('UTF-8'))
                logging.warning('执行：N')
                self.tn.write(self.format('N'))
            elif index == 5:
                logging.info('进入用户视图')
                self.tn.write(self.format('system-view'))
            elif index == 4:
                logging.info('进入系统视图')
                self.tn.write(self.format('diagnose'))
            elif index == 3:
                logging.info('进入诊断视图')
                break
            else:
                logging.warning('Telnet目标客户端未响应')
                logging.warning(data.decode('UTF-8'))
                sys.exit()

    def shell_expect(self, command, prompts, timeout=120):
        logging.info('执行: ' + command)
        # 执行命令
        self.tn.write(self.format(command))
        index, match, data = self.tn.expect(prompts, timeout=timeout)
        if index == -1:
            logging.warning('Telnet目标客户端未响应')
        else:
            # 解码后返回数据
            return data.decode('UTF-8')

    def __del__(self):
        # 退出设备
        self.tn.write(self.EXIT)
        # 关闭连接
        self.tn.close()
