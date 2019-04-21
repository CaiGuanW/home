Desc: <br>
====
    解析secure日志，从不同维度解析
Usage: <br>
==== 
    python check_secure.py --help
    --mode指定工作模式，有四种工作模式：time|ip|user|fail，默认是time模式；
    --logdir用于指定secure日志路径，默认是var-log-secure；
    --from_time和--end_time在四种工作模式下都可以使用，用于指定特定时间；
    --min、--num、--printl仅在time模式下指定，分别用于统计周期、输出行数、和指定信息；
    --user仅在user模式下，用于指定特定用户；
    --ip仅在ip模式下，用于指定特定ip；
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
