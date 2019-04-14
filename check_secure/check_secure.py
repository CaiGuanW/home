#!/usr/bin/python
#coding=utf8

import pprint
import sys
import urllib2
import json
import click
import datetime

month_to_num = {
'Jan':1,
'Feb':2,
'Mar':3,
'Apr':4,
'May':5,
'Jun':6,
'Jul':7,
'Aug':8,
'Sep':9,
'Oct':10,
'Nov':11,
'Dec':12}

def sort_count_list(l):

    # 统计list中的元素个数，并按照个数倒序排序
    count_suc_user = sorted(tuple([(a, l.count(a)) for a in set(l)]), key = lambda x:x[1], reverse=True)
    return count_suc_user

def sort_by_status(all_ip_info, num, printnum):

    # 根据指定列进行排序,并输出TOP NUM;
    
    for status in ['success', 'fail']:

        log_i = sort_count_list([a[num] for a in all_ip_info if a[2] == status])
        print_level_1("Login %s Top %s"%(status, printnum))
    
        if printnum > len(log_i):
            nn = len(log_i)
        else:
            nn = printnum
        for m in range(0, nn):
            print_level_2("No.%s %s %s"%(m+1, log_i[m][0], log_i[m][1]))

def sort_by_spec(all_ip_info, info, fil_num, filters, sort_num):

    # 指定某个字段进行过滤并统计

    print_level_1("%s统计信息"%info)
    if info == 'user':
        sort_info = sort_count_list([a[sort_num] for a in all_ip_info if a[fil_num] == filters])
    else:
        sort_info = sort_count_list([a[sort_num] for a in all_ip_info if filters in a[fil_num]])
    for m in sort_info:
        print_level_2("%s: %s 次数: %s"%(info, m[0], m[1]))

def print_detail(all_ip_info):

    print_level_1("| 日期 | 登录状态 | 失败原因 | 登录方式 | 登录用户 | 源ip ")
    for y in all_ip_info:
        print_level_2("| %s | %s | %s | %s | %s | %s"%(y[0],y[2],y[3],y[4],y[5],y[6]))

def print_type(all_ip_info):

    print_level_1("登录结果统计信息")
    for status in ['success', 'fail']:
        log_i = sort_count_list([a[4] for a in all_ip_info if a[2] == status])
        if log_i != []:
            for s in log_i:
                print_level_2("使用 %s 登录 %s %s 次"%(s[0], status, s[1]))

def print_brief(all_ip_info, num, type = None ):

    if all_ip_info == []:
        print("您输入的条件未能过滤出结果")
        sys.exit(2)
    suc = len([ n for n in all_ip_info if n[2] == 'success' ])
    fail = len([ n for n in all_ip_info if n[2] == 'fail' ])
    print_level_1("%s: %s 总共登录 %s 次，其中成功 %s 次，失败 %s 次"%(type, all_ip_info[0][num], len(all_ip_info), suc, fail))


def get_location(ip):

    url = "http://ip.taobao.com/service/getIpInfo.php?ip=%s"%ip
    x = json.load(urllib2.urlopen(url))
    return "%s %s %s %s"%(x['data']['country'],x['data']['region'],x['data']['city'],x['data']['isp'])


def print_level_1(info):

    print("============================")
    print(">>  %s"%info)

def print_level_2(info):

    print("--  %s"%info)


def check_secure(LOGFILE, from_time, end_time):

    all_ip_info = []

    with open(LOGFILE, 'r') as f:
        for line in f:
            info = ()
            date = None
            status = None
            fail_reason = None
            type = None
            user = None
            peer_ip = None
            peer_port = None
            # 解析每行日志得到的信息
            per_log = line.split()
            app = per_log[4]
            # 判断是否是sshd
            if app.startswith("sshd"):
                # 只过滤完成登录这个操作的连接
                if per_log[5] == 'Accepted' or per_log[5] == 'Failed':
                    year = 2019
                    date = datetime.datetime(int(year), int(month_to_num[per_log[0]]),
                                    int(per_log[1]), int(per_log[2].split(':')[0]), 
                                    int(per_log[2].split(':')[1]), int(per_log[2].split(':')[2]))
                    host = per_log[3]
                    if per_log[5] == 'Accepted':
                        status = 'success'
                    elif per_log[5] == 'Failed':
                        status = 'fail'
                        if 'invalid user' in line:
                            fail_reason = 'invalid user'
                        else:
                            fail_reason = 'error passwd'
                    if per_log[6] == 'password':
                        type = 'passwd'
                    elif per_log[6] == 'publickey':
                        type = 'publickey'
                    user = per_log[per_log.index('from') - 1]
                    peer_ip = per_log[per_log.index('from') + 1]
                    peer_port = per_log[per_log.index('port') + 1]
                    info = (date, host, status, fail_reason, type, user, peer_ip, peer_port)
            if user is not None:
                if from_time != None:
                    from_t = datetime.datetime.strptime(from_time,"%Y-%m-%d-%H:%M:%S")
                    end_t = datetime.datetime.strptime(end_time,"%Y-%m-%d-%H:%M:%S")
                    if info[0] >= from_t and info[0] <= end_t:
                        all_ip_info.append(info)
                else:
                    all_ip_info.append(info)
        return all_ip_info

def sort_by_time(all_ip_info, minutes, printnum, printl):

    # 对传入数据按时间倒序排序
    sort_by_time = sorted(all_ip_info, key = lambda x:x[0], reverse = True)
    
    if sort_by_time == []:
        print("未从日志中过滤到您输入的条件")
        sys.exit(2)

    # head是最近的时间
    head = sort_by_time[0][0]
    # tail是最早的时间
    tail = sort_by_time[-1][0]
    x = head
    # 周期为diff分钟进行一次统计
    diff = datetime.timedelta(minutes = minutes)
    n = []

    while x >= tail:
        success_count = 0
        success_ip = []
        success_user = []
        failed_count = 0
        failed_user = []
        failed_ip = []
        for y in sort_by_time:
            # 判断时间是否在周期时间内
            if y[0] <= x and y[0] > (x - diff):
                if y[2] == 'success':
                    success_count = success_count + 1
                    success_user.append(y[5])
                    success_ip.append(y[6])
                elif y[2] == 'fail':
                    failed_count = failed_count + 1
                    failed_user.append(y[5])
                    failed_ip.append(y[6])
        count_info = ()
        count_info = (x.strftime("%Y-%m-%d-%H:%M:%S"),
                    (x-diff).strftime("%Y-%m-%d-%H:%M:%S"),
                    success_count, failed_count,
                    success_ip, failed_ip, success_user, failed_user)
        n.append(count_info)
        # 变量时间递减
        x = x - diff

    for m in n[0: printnum]:
        # 统计周期时间内的ip情况;
        # 三种打印维度：登录情况（默认），登录ip，登录用户；
        if printl == 'ip':
            count_suc_ip = sort_count_list(m[4])
            count_fai_ip = sort_count_list(m[5])
            if count_suc_ip != []:
                print_level_1("从 %s 到 %s: 登录成功的ip: "%(m[1],m[0]))
                for o in count_suc_ip:
                    print_level_2("%s ip:%s 次数:%s"%(' '*50,o[0], o[1]))
            if count_fai_ip != []:
                print_level_1("从 %s 到 %s: 登录失败的ip: "%(m[1],m[0]))
                for p in count_fai_ip:
                    print_level_2("%s ip:%s 次数:%s"%(' '*50,p[0], p[1]))
        elif printl == 'user':
            count_suc_user = sort_count_list(m[6])
            count_fai_user = sort_count_list(m[7])
            if count_suc_user != []:
                print_level_1("从 %s 到 %s: 登录成功的用户: "%(m[1], m[0]))
                for q in count_suc_user:
                    print_level_2("%s 用户:%s 次数:%s"%(' '*50,q[0], q[1]))
            if count_fai_user != []:
                print_level_1("从 %s 到 %s: 登录失败的用户: "%(m[1], m[0]))
                for r in count_fai_user:
                    print_level_2("%s 用户:%s 次数:%s"%(' '*50, r[0], r[1]))
        else:
            print_level_2("从 %s 到 %s: 共 %s 次登录成功，共 %s 次登录失败"%(m[1],m[0],m[2],m[3]))

def sort_by_input(all_ip_info, printnum, type, filters):

    global USER_NUM
    global IP_NUM

    if type == "user":
        fil_type = 'ip'
        num = USER_NUM
        fil_num = IP_NUM
        tmp = [ m for m in all_ip_info if filters in m[num] ]
    elif type == "ip":
        fil_type = 'user'
        num = IP_NUM
        fil_num = USER_NUM
        tmp = [ m for m in all_ip_info if m[num] == filters ]

    print_brief(tmp, num, type = type)
    print_type(tmp)
    sort_by_spec(tmp, fil_type, num, filters, fil_num)
    print_detail(tmp)

if __name__ == '__main__':

    USER_NUM = 5
    IP_NUM = 6

    @click.command()
    @click.option('--mode', default='time' ,type=click.Choice(['time','ip','user','fail']))
    @click.option('--logdir', default="/var/log/secure", help = "secure log dir")
    @click.option('--min', default=5, help = "Only work in time mode, specify time interval")
    @click.option('--num', default=10, help = "in time mode, specify column num; in user|ip mode, specify TOP N")
    @click.option('--from_time', default=None, help = "specify start time %Y-%m-%d-%H:%M:%S")
    @click.option('--end_time',default=None, help = "specify ending time %Y-%m-%d-%H:%M:%S ")
    @click.option('--printl', default='count', type=click.Choice(['count','ip','user']))
    @click.option('--user', default=None, help = "Only work in user mode, specify user")
    @click.option('--ip', default=None, help = "Only work in ip mode, specify ip")
    def begin(mode, logdir, min, num, from_time, end_time, printl, user, ip):
        all_ip_info = check_secure(logdir, from_time, end_time)
        fail_count = 0 
        success_count = 0 
        for x in all_ip_info:
            if x[2] == "success":
                success_count = success_count + 1 
            elif x[2] == "fail":
                fail_count = fail_count + 1
        print_level_1("总共\033[32m %s \033[0m次登录成功记录 \033[31m %s \033[0m次登录失败记录"%(success_count, fail_count))
        if mode == 'time':
            sort_by_time(all_ip_info, min, num, printl)
        elif mode == 'user':
            if user is not None:
                sort_by_input(all_ip_info, num, 'user', user)
            else:
                sort_by_status(all_ip_info, USER_NUM, num)
        elif mode == 'ip':
            if ip is not None:
                sort_by_input(all_ip_info, num, 'ip', ip)
            else:
                sort_by_status(all_ip_info, IP_NUM, num)
        elif mode == 'fail':
            tmp = [a for a in all_ip_info if a[2] == 'fail']
            print_detail(tmp)
        print("============================")
    begin()
