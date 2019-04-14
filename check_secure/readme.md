Desc: <br>
====
    解析secure日志，从不同维度解析
Usage: <br>
==== 
    python check_secure.py --help
    有四种工作模式：time|ip|user|fail
Output: <br>
====
1、time模式下，按照间隔每60分钟进行过滤，共过滤10行 <br>
![image](https://github.com/CaiGuanW/home/blob/master/get_tomcat_cve/20190407230733.png)<br>

2、time模式下，输出用户信息
![image](https://github.com/CaiGuanW/home/blob/master/get_tomcat_cve/20190407230814.png)<br>

3、time模式下，输出ip信息
