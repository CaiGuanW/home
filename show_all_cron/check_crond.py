#!/usr/bin/python

import os

class cron_task:

    def __init__(self, path_dir, user, cmd, sch_time):
        
        self.path_dir = path_dir
        self.user = user
        self.task_cmd = cmd
        self.sch_time = sch_time

#anacrontab parse
anacrontab_file = "/etc/anacrontab"
#normal parse
sys_cron_dir = "/etc/cron.d"
sys_cron_file = "/etc/crontab"
spool_dir = "/var/spool/cron"
sys_cron_runparts_dir = []
cron_task_list = []


with open(anacrontab_file) as ana_file:

    for line in ana_file.readlines():
        line = line.strip()
        if not line.startswith("#"):
            if len(line) != 0 and "=" not in line:
                sys_cron_runparts_dir.append(line.split()[5])
                sch_time = line.split()[2]
                a = cron_task(anacrontab_file, "root", " ".join(line.split()[4:]), sch_time)
                cron_task_list.append(a)

for root,dirs,files in os.walk(sys_cron_dir):

    for single_file in files:
        with open("%s/%s"%(root,single_file)) as f:
            for line in f.readlines():
                line = line.strip()
                
                if not line.startswith("#") and len(line) !=0 and "=" not in line:
                    if "run-parts" in line:
                        sys_cron_runparts_dir.append(line.split()[7])
                    
                    path_dir = "%s/%s"%(root,single_file)
                    user = "root"
                    cmd = " ".join(line.split()[6:])
                    sch_time = " ".join(line.split()[0:5])
                    a = cron_task(path_dir, user, cmd, sch_time)
                    cron_task_list.append(a)


with open(sys_cron_file) as f:

    for line in f.readlines():

        line = line.strip()
        if not line.startswith("#") and len(line) !=0 and "=" not in line:
            path_dir = sys_cron_file
            cmd = " ".join(line.split()[6:])
            user = line.split()[5]
            sch_time = " ".join(line.split()[0:5])
            a = cron_task(path_dir, user, cmd, sch_time)
            cron_task_list.append(a)

for root,dirs,users in os.walk(spool_dir):

    for single_user in users:
        with open("%s/%s"%(root,single_user)) as f:
        
            for line in f.readlines():
                line = line.strip()
                if not line.startswith("#") and len(line) !=0 and "=" not in line:
                    path_dir = "%s/%s"%(root, single_user)
                    user = single_user
                    cmd = " ".join(line.split()[5:])
                    sch_time = " ".join(line.split()[0:5])
                    a = cron_task(path_dir, user, cmd, sch_time)
                    cron_task_list.append(a)

for single_file in sys_cron_runparts_dir:

    for root, dirs, tasks  in os.walk(single_file):

        for single_task in tasks:
            
            sch_time = root.replace("/etc/", "")
            a = cron_task("%s/%s"%(root, single_task), "root", "%s/%s"%(root, single_task), sch_time)
            cron_task_list.append(a)

print("%-20s %-50s %-20s %-20s"%("Time", "Path", "User", "Task"))
for one in cron_task_list:

    print("%-20s %-50s %-20s %-20s"%(one.sch_time, one.path_dir, one.user, one.task_cmd))
