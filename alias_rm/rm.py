#!/usr/bin/python
import os
import sys
import shutil
import commands
import datetime
import socket


def get_fs_size(mountpoint):

    '''
    get filesystem size
    '''
    fs_info = {}
    try:
        fs_info["total"] = os.statvfs(mountpoint).f_bsize * os.statvfs(mountpoint).f_blocks
        #statvfs get total include Reserved,we should ignore it;
        fs_info["total"] = fs_info["total"] * 0.95
        fs_info["free"] = os.statvfs(mountpoint).f_bsize * os.statvfs(mountpoint).f_bavail
        fs_info["used"] = fs_info["total"] - fs_info["free"]
        if fs_info["used"] < 0:
            fs_info["used"] = 0
    except Exception,e:
        print("statvfs %s failed: %s"%(mountpoint,e))
        sys.exit(GETFSSIZEFAILED)
    return fs_info

def turn_bytes(obj, newtype):

    '''
    trun BYTES to kb,mb,gb
    '''

    obj = float(obj)
    if newtype == "kb":
        newObj = obj / 1024
    elif newtype == "mb":
        newObj = obj / (1024*1024)
    elif newtype == "gb":
        newObj = obj / (1024*1024*1024)
    else:
        newObj = obj
    return newObj

def exec_cmd(cmd):

    '''
    use commands module exec cmd
    '''
    try:
        status, output = commands.getstatusoutput(cmd)
        return status, output
    except Exception, e:
        print "exec %s error:%s"%(cmd, e)
        return -1, 'error'

def get_obj_size(obj):
    
    '''
    get file/dir size
    '''
    try:
        obj_size = os.path.getsize(obj);
    except Exception,e:
        print("get %s size failed: %s"%(obj, e))
        logger('error', 'get %s size failed: %s'%(obj, e))
        sys.exit(GETOBJSIZEFAILED);

    return obj_size

def logger(level, info):
    '''
    logger the process
    '''

    loggerPath = "/var/log/remove_record.log"
    now = datetime.datetime.now()

    with open(loggerPath,'a') as f:
        f.write("%s %s: %s\n"%(now, level, info))
    f.close()

def Usage():

    print "Usage: rm $obj;" 
    print "For example: rm file of rm dir"
    print "You only can delete a file once"

if __name__ == "__main__":

        
    DELETEOK = 0
    DELETEFAILED = 1
    DONOTHING = 2
    FILENOTEXIST = 3
    GETOBJSIZEFAILED = 4
    GETFSSIZEFAILED = 5
    REMOTEDIRNOEXIT = 6
    EXECCMDFAILED = 127
    EXECCMDERROR = 128
    ARGVERROR = 129    
    
    if len(sys.argv) != 2:
        Usage()
        sys.exit(ARGVERROR)

    source_obj = sys.argv[1]
    
    remote_dir = "/tmp"
    retry = 3
    gap = 5000
    max_obj_size = 5000

    # get local ip from route to 192.0.0.1
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("192.0.0.1", 80))          
    ip = s.getsockname()[0]
    local_ip = ip

    status, output = exec_cmd("pwd")
    if status == 0:
        pwd = output
    else:
        pwd = "/root"

    if source_obj.startswith("/"):
        pass
    else:
        source_obj = "%s/%s"%(pwd,source_obj)


    status, output = exec_cmd("hostname")
    if status == 0:
        local_hostname = output
    else:
        local_hostname = "NFJD-PSC"

    status, output = exec_cmd("whoami")
    if status ==0:
        user = output
    else:
        user = "ROOT"

    if os.path.exists(remote_dir):
        remote_user_dir = remote_dir + '/' + user
        if os.path.exists(remote_user_dir):
            pass
        else:
            try:
                os.mkdir(remote_user_dir)
            except:
                remote_user_dir = remote_dir
    else:
        sys.exit(REMOTEDIRNOEXIT)

    logger('Info','User:%s try to delete %s'%(user, source_obj))
    source_obj_size = get_obj_size(source_obj)
    remote_fs_size = get_fs_size(remote_user_dir)
    remote_fs_free = remote_fs_size['free']

    logger('Info','%s :size %s, %s free size: %s'%(source_obj, source_obj_size, remote_user_dir, remote_fs_free))
    
    if source_obj_size > max_obj_size:
        print "*******************************"
        print("* LOCAL IP IS %s "%local_ip)
        print("* LOCAL HOSTNAME IS %s   "%local_hostname)
        print("* YOU ARE IN %s NOW      "%pwd)
        print "* THE SIZE OF '%s' is %s bytes "%(source_obj, source_obj_size);
        print "*******************************"
        makeChoose = raw_input("you really want to delete it YES/NO?\n")
        if makeChoose == 'YES':
            pass
        else:
            logger('Info', 'User Cancel;do no thing,quit')
            sys.exit(DONOTHING)
    
    if turn_bytes((remote_fs_free - source_obj_size),'mb') > gap:
        
        while retry:
            try:
                time_format = str(datetime.datetime.now().strftime('%Y-%b-%d-%y-%H-%M-%S'))
                status, output = exec_cmd("basename %s"%source_obj)
                remote_obj = remote_user_dir + '/' + output + '.' + time_format
                mv_cmd = "/usr/bin/mv -f %s %s"%(source_obj, remote_obj)
                status, output = exec_cmd(mv_cmd)
                if status == 0:
                    print("mv %s ok"%source_obj);
                    logger('Info', '%s move %s success'%(user, source_obj))
                    sys.exit(DELETEOK);
                else:
                    logger('Error', 'mv failed:%s'%output)
            except Exception,e:
                print("mv failed %d: %s"%(retry,e))
                logger('Error', 'move failed: %s'%(user, e))
            retry = retry - 1
        if retry == 0:
            print("mv %s failed"%source_obj)
            logger('Error', 'try mv 3 times.failed')
            sys.exit(DELETEFAILED)
    else:
        print "*******************************"
        print("* %s FREE SPACE IS NOT ENOUGH"%remote_user_dir)
        print("* LOCAL IP IS %s "%local_ip)
        print("* LOCAL HOSTNAME IS %s "%local_hostname)
        print("* YOU ARE IN %s NOW "%pwd)
        print "* THE SIZE OF '%s' is %s bytes "%(source_obj, source_obj_size);
        print "*******************************"
        print("you want to delete '%s'"%source_obj)
        makeChoose = raw_input("ARE YOU SURE? YES/NO\n");
        if makeChoose == 'YES':
            rm_cmd = "sudo /usr/bin/rm -rf %s"%source_obj
            status, output = exec_cmd(rm_cmd)
            if status == 0:
                print("delete %s ok"%source_obj);
                logger('Info', '%s delete %s success'%(user, source_obj))
                sys.exit(DELETEOK)
            else:
                print("delete %s failed:%s"%(source_obj,output));
                logger('Error', '%s delete %s failed'%(user, source_obj))
                sys.exit(DELETEFAILED)
        else:
            logger('Info', 'User cancel;do nothing,quit')
            sys.exit(DONOTHING)

