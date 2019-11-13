# -*- coding: utf-8 -*-

from pywifi import *
import time
import chardet

#检查目前是否连接网络
def Check_state():
    wifi = PyWiFi()                    #创建一个无线对象
    itface = wifi.interfaces()[0]       #获取第一个无线网卡
    #print(itface.status())              #无线网卡有五种状态
    if itface.status() == 4:                                    #0: disconnected
        print('Your computer has connected to wifi')            #1: scanning
    else:                                                       #2: inactive 闲置
        print("Your computer hasn't connected to wifi yet")     #3: connecting
                                                                #5: connected
AKMS = ['AKM_TYPE_NONE',
        'AKM_TYPE_WPA',
        'AKM_TYPE_WPAPSK',
        'AKM_TYPE_WPA2',
        'AKM_TYPE_WPA2PSK']

#输出扫描到附近的无线信号以及相应信息
def scan_wifi():
    wifi = PyWiFi()
    itface = wifi.interfaces()[0]
    itface.scan()
    time.sleep(10)
    wifi_sources = itface.scan_results()
    #print(wifi_sources)
    for data in wifi_sources:
        # print(dir(data))
        name = data.ssid.encode('raw_unicode_escape', 'strict').decode()
        #print('Wifi名字:', data.ssid)
        print(name)
        print('BSSID:', data.bssid)
        # print(data.akm)
        print('加密类型:', AKMS[data.akm[0]])
        print('信号强度:', data.signal)
        print('------------------------------------------')

#Check_state()
scan_wifi()