#!/bin/bash

time=5
sleep=1
mode="speed"

while getopts 'n:t:u:m:' OPT
do
    case $OPT in 
    m) mode="$OPTARG";;
    n) time="$OPTARG";;
    t) sleep="$OPTARG";;
    u) url="$OPTARG";;
    esac
done

declare -a array

if [[ ! -z $url ]]
then
    for x in $url
    do
       array+=("$x")
    done
else
    array+=("https://www.baidu.com")
    array+=("http://www.baidu.com")
fi

function url_test(){

url=$1
times=$2
sleep=$3
while (($times))
do
   date=$(date +"%m-%d-%H:%M:%S")
   output=$(curl -o /dev/null --max-time 280 -s -w %{time_namelookup}:%{time_connect}:%{time_appconnect}:%{time_redirect}:%{time_pretransfer}:%{time_starttransfer}:%{time_total}:%{http_code} $url)
   dns_time=$(echo $output|awk -F\: '{print $1}')
   connect_time=$(echo $output|awk -F\: '{print $2}')
   appconnect_time=$(echo $output|awk -F\: '{print $3}')
   redict_time=$(echo $output|awk -F\: '{print $4}')
   pretransfer_time=$(echo $output|awk -F\: '{print $5}')
   starttransfer_time=$(echo $output|awk -F\: '{print $6}')
   total_time=$(echo $output|awk -F\: '{print $7}')
   code=$(echo $output|awk -F\: '{print $8}')
   #--NAMELOOKUP
   #--|--CONNECT(NAMELOOKUP+TCP)
   #--|--|--APPCONNECT(NAMELOOKUP+TCP+HTTPS)
   #--|--|--|--PRETRANSFER(NAMELOOKUP+TCP+HTTPS+do_ready)
   #--|--|--|--|--STARTTRANSFER(NAMELOOKUP+TCP+HTTPS+do_ready+server_do)
   #--|--|--|--|--|--TOTAL(NAMELOOKUP+TCP+HTTPS+do_ready+server_do+send)
   #-----------------total------------------------                                              
   times=$(echo $times-1|bc)
   #dns_time
   tcp_time=$(echo $connect_time-$dns_time|bc)
   if [[ $appconnect_time == "0.000" ]]
   then
       ssl_time="0.000"
       do_ready=$(echo $pretransfer_time-$connect_time|bc)
   else
       ssl_time=$(echo $appconnect_time-$connect_time|bc)
       do_ready=$(echo $pretransfer_time-$appconnect_time|bc)
   fi
   server_do=$(echo $starttransfer_time-$pretransfer_time|bc)
   send=$(echo $total_time-$starttransfer_time|bc)
   echo "| $date | $url | $code | $dns_time | $tcp_time | $ssl_time | $do_ready | $server_do| $send | $total_time |"

done
}

function url_size(){

url=$1
times=$2
sleep=$3
while (($times))
do
    info=$(curl -o /dev/null --max-time 280 -s -w %{size_download}:%{size_header}:%{size_request}:%{size_upload}:%{speed_download}:%{speed_upload} $url )
    size_d=$(echo $info|awk -F\: '{print $1}')
    size_h=$(echo $info|awk -F\: '{print $2}')
    size_r=$(echo $info|awk -F\: '{print $3}')
    size_u=$(echo $info|awk -F\: '{print $4}')
    sp_d=$(echo $info|awk -F\: '{print $5}')
    sp_u=$(echo $info|awk -F\: '{print $6}')
    echo "| $size_d | $size_h | $size_r | $size_u | $sp_d | $sp_u |"
    sleep $sleep
    times=$(echo $times-1|bc)
done

}

echo "--------------------------------------------------------------------------------------------------"
if [[ $mode == "speed" ]]
then 
    echo "|日期|URL|返回状态码|DNS解析时间|TCP连接时间|SSL传输时间|客户端准备传输时间|服务器处理时间|传输时间|总时间|"
    for x in ${array[*]}
    do
       url_test $x $time $sleep
    done
elif [[ $mode == "size" ]]
then
    echo "|下载大小|下载头大小|请求大小|上传大小|下载速度(B/s)|上传速度(B/s)"
    for x in ${array[*]}
    do
         url_size $x $time $sleep
    done
fi
echo "--------------------------------------------------------------------------------------------------"
