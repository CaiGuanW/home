#!/usr/bin/python
#coding=utf8

import pprint
import sys
import urllib2
import json

def get_location(ip):

    url = "http://ip.taobao.com/service/getIpInfo.php?ip=%s"%ip
    x = json.load(urllib2.urlopen(url))
    return "%s %s %s %s"%(x['data']['country'],x['data']['region'],x['data']['city'],x['data']['isp'])

def check_secure(checkmonth, checkday, LOGFILE = "/var/log/secure"):

    with open(LOGFILE,'r') as f:
    
        total_success_time = 0
        total_failed_time = 0
        total_login = []
        bad_try = []

        for line in f:

            #解析每行日志得到的信息
            month = line.split()[0]
            day = line.split()[1]
            host = line.split()[3]
            app = line.split()[4]
            info = line.split()[5:]
            
            #result_info = {
            #               'ip':'',
            #               'succ':[{'user':'','count':'','type' :''}],
            #               'fail':[{'user':'','count':'','reason' :''}]
            #               }
           
            user = ""
            ip = ""

            #判断日期
            if month == checkmonth and int(day) == int(checkday):
                
                #判断是否是sshd
                if app.startswith("sshd"):
        
                    #登录成功
                    if info[0] == "Accepted":
                        total_success_time = total_success_time + 1
                        login_type = info[1]
                        user = info[info.index("for") + 1]
                        ip = info[info.index("from") + 1]

                        status = "success"

                    #登录失败
                    elif info[0] == "Failed":
                        total_failed_time = total_failed_time + 1
                        user = info[info.index("for") + 1]
                        ip = info[info.index("from") + 1]

                        if user == "invalid":
                            user = info[info.index("for") + 3]
                            failed_reason = "invaild user"
                        else:
                            failed_reason = "error passwd"
                        status = "fail"
                    
                    #错误协议
                    elif info[0] == "Bad" or info[0] == "Did":
                        ip = info[info.index("from") + 1]
                        bad_try.append(ip)

                    is_find_ip = 0
                    is_find_user = 0

                    if user != "":
                        for single_ip_info in total_login:
                            #检查ip是否在列表中
                            if single_ip_info['ip'] == ip :
                                if status == "success":
                                    for single_succ_info in single_ip_info['succ']:
                                        if single_succ_info['user'] == user and \
                                            single_succ_info['type'] == login_type:
                                            single_succ_info['count'] = single_succ_info['count'] + 1
                                            is_find_user = 1
                                            break
                                    if is_find_user == 0:
                                        x = {}
                                        x['user'] = user
                                        x['type'] = login_type
                                        x['count'] = 1
                                        single_ip_info['succ'].append(x)
                                    
                                elif status == "fail":
                                    for single_fail_info in single_ip_info['fail']:
                                        if single_fail_info['user'] == user and \
                                            single_fail_info['reason'] == failed_reason:
                                            single_fail_info['count'] = single_ip_info['count'] + 1
                                            is_find_user = 1
                                            break
                                    if is_find_user == 0:
                                        x = {}
                                        x['user'] = user
                                        x['reason'] = failed_reason
                                        x['count'] = 1
                                        single_ip_info['fail'].append(x)
                                is_find_ip = 1
                                break
                            
                        if is_find_ip == 0:
                            x = {}
                            x['ip'] = ip
                            x['succ'] = []
                            x['fail'] = []
                            if status == 'success':
                                y = {}
                                y['user'] = user
                                y['count'] = 1
                                y['type'] = login_type
                                x['succ'].append(y)
                            else:
                                y = {}
                                y['user'] = user
                                y['count'] = 1
                                y['reason'] = failed_reason
                                x['fail'].append(y)
                            total_login.append(x)
        return total_login,bad_try

if __name__ == '__main__':

    total_login, bad_try = check_secure(sys.argv[1], sys.argv[2])
    for ip_info in total_login:
        print "ip is %s, 来源:%s"%(ip_info['ip'], get_location(ip_info['ip']).encode("UTF8"))
        
        print "    登录成功的:"
        if ip_info['succ'] != []:
            for user_info in ip_info['succ']:
                print "        用户:%s 登录次数:%s 登录类型:%s"%(user_info['user'], user_info['count'], user_info['type'])
        else:
            print "    无"

        print "    登录失败的:"
        if ip_info['fail'] != []:
            for user_info in ip_info['fail']:
                print "        用户:%s 登录次数:%s 失败原因:%s"%(user_info['user'], user_info['count'], user_info['reason'])
        else:
            print "    无"
    
    if bad_try != []:
        print "错误协议尝试的ip:"
        for ip in bad_try:
            print "    ", ip, get_location(ip).encode("UTF8")
