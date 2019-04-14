Desc: <br>
====
    解析secure日志，从不同维度解析
Usage: <br>
==== 
    python check_secure.py --help
    有四种工作模式：time|ip|user|fail
Output: <br>
====
1、time模式下，以时间为维度，按照间隔每60分钟进行过滤，共过滤10行，打印登录信息。 <br>
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/01.png)<br>

2、time模式下，输出用户信息；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/02.png)<br>

3、time模式下，输出ip信息；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/03.png)<br>

4、指定时间段内的登录信息；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/04.png)<br>

5、ip模式下，登录信息统计；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/05.png)<br>

6、ip模式下，指定ip的登录信息；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/06.png)<br>

7、user模式下，登录信息统计；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/07.png)<br>

8、user模式下，指定user的登录信息；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/08.png)<br>

9、fail模式下，输出登录失败的信息；
![image](https://github.com/CaiGuanW/home/blob/master/check_secure/09.png)<br>
