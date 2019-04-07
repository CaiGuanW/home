#!/usr/bin/python
#coding=utf8
import urllib2
from bs4 import BeautifulSoup
import pprint
import xlsxwriter
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == '__main__':

    if len(sys.argv) == 2:
        tomcat_version = sys.argv[1]
    else:
        # 默认是7
        tomcat_version = "7"
    
    url = "http://tomcat.apache.org/security-%s.html"%tomcat_version

    result = urllib2.urlopen(url)
    soup = BeautifulSoup(result.read(), "html.parser")
    #print soup.find_all("div")
    c_i = []
    # 每个CVE号都通过h3标签(标题)区分
    for x in soup.find_all('h3'):
        s = {}
        # 并且span标签不为空
        if x.span != None:
            # 获取该标签下所有的值，并解析
            info = x.get_text().split()
            # 值如 'July 2018 Fixed in Apache Tomcat 7.0.90'
            index = info.index("Fixed")
            publish_date = " ".join(info[0:index])
            fixed_version = " ".join(info[index+2:])
            s['publish_date'] = publish_date.strip("released")
            s['fixed_version'] = fixed_version
            # 获取下两个兄弟标签
            cveinfo =  x.next_sibling.next_sibling
            s['cve_info'] = []
            for pp in cveinfo.find_all("p"):
                # 找到strong这个标签
                if pp.strong != None:
                    t = {}
                    cve_level = pp.strong.get_text().split()[0].strip(":")
                    cve_head = " ".join(pp.strong.get_text().split()[1:])
                    cve_num = pp.a.get_text()
                    t['cve_level'] = cve_level
                    t['cve_head'] = cve_head
                    t['cve_num'] = cve_num
                    for y in pp.next_siblings:
                        if y.string != None and "Affects:" in y.string:
                            affects_version = y.string.strip("Affects:").strip()
                    s['cve_info'].append(t)
        if s != {}:
            c_i.append(s)

    #pprint.pprint(c_i)

    # 下面这里是写入excel

    workbook = xlsxwriter.Workbook('tomcat_cve_%s.xlsx'%tomcat_version)
    worksheet = workbook.add_worksheet('tomcat-cve')
    title_format = workbook.add_format({'align': 'center'})
    title_format.set_bold()
    title_format.set_size(20)
    mid_format = workbook.add_format({'align': 'center'})
    worksheet.set_row(0, 25, title_format)
    worksheet.set_column('A:H', 25)
    heads = ['发布日期', "tomcat版本号", "CVE号", "CVE标题", "CVE等级"]
    worksheet.write_row('A1', heads, mid_format)

    rownum = 2
    for h in c_i:
        cve_num = len(h["cve_info"])
        if cve_num > 1:
            worksheet.merge_range('A%s:A%s' % (rownum, cve_num + rownum - 1), str(h["publish_date"]), mid_format)
            worksheet.merge_range('B%s:B%s' % (rownum, cve_num + rownum - 1), str(h['fixed_version']), mid_format)
        else:
            worksheet.write_string('A%s' % rownum, str(h["publish_date"]), mid_format)
            worksheet.write_string('B%s' % rownum, str(h['fixed_version']), mid_format)
        tempnum = rownum
        for d in range(0, cve_num):
            worksheet.write_string('C%s' % tempnum, h['cve_info'][d]['cve_num'], mid_format)
            worksheet.write_string('D%s' % tempnum, h['cve_info'][d]['cve_head'], mid_format)
            worksheet.write_string('E%s' % tempnum, h['cve_info'][d]['cve_level'], mid_format)
            tempnum = tempnum + 1
        rownum = rownum + 1
    workbook.close()

