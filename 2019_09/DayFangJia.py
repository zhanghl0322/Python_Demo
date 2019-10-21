import urllib.request
import json
import time
import random
import pymysql as pymysql
from random import choice
import requests
from bs4 import BeautifulSoup  # 在写爬虫的时候发现BeautifulSoup的html.parser解析器有个坑，导致正文抽取失败
import sys

# 请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'select_city=110000; all-lj=eae2e4b99b3cdec6662e8d55df89179a; lianjia_uuid=b83e20e3-5014-43f7-9222-a070cecb0bd6; _jzqckmp=1; UM_distinctid=15fc04200552d1-085f1f610b4ed6-173f6d56-fa000-15fc042005672f; CNZZDATA1253477573=1325989915-1510755840-%7C1510755840; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1510759071; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1510759225; _smt_uid=5a0c5a9f.96d81b6; CNZZDATA1254525948=639576567-1510755385-%7C1510755385; CNZZDATA1255633284=1004832870-1510755976-%7C1510755976; CNZZDATA1255604082=201482554-1510755445-%7C1510755445; _qzja=1.2048199199.1510759071957.1510759071957.1510759071958.1510759071958.1510759225748.0.0.0.2.1; _qzjb=1.1510759071958.2.0.0.0; _qzjc=1; _qzjto=2.1.0; _jzqa=1.1897032758930753000.1510759072.1510759072.1510759072.1; _jzqc=1; _jzqb=1.2.10.1510759072.1; _ga=GA1.2.130004765.1510759074; _gid=GA1.2.860216797.1510759074; lianjia_ssid=6a5df244-1c9c-4a81-b3eb-eddd2d2952d8',
    'Host': 'bj.lianjia.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}
URL = 'https://bj.lianjia.com/ershoufang/pg'


# 下载网页响应内容 2019年10月21日10:52:11
def download(url):
    num_try = 2
    while num_try > 0:
        num_try -= 1
        try:
            content = requests.get(url, headers=headers)
            # print(content.text)
            return content.text
        except urllib.URLError as e:
            print
            'Download error', e.reason

    return None


def getHouseInfo(url):
    # 读取原始数据(注意选择gbk编码方式)
    try:
        html = download(url)  # 下载html
        soup = BeautifulSoup(html, 'html.parser')
    except Exception:
        return -1

    house_info_div = soup.find_all('div', attrs={'class': 'info clear'})  # 获取整个标题块

    # 数据分割 解析html正文 2019年10月21日16:52:27
    house_list = []
    for info_item in house_info_div[0]:
        print('*************', info_item.get_text())
        house_list.append(info_item.get_text())  # 将信息加入集合
        pass
    print(house_list)

    # 验证集合是否存在数据
    if len(house_list) == 0:
        print(time.asctime(time.localtime(time.time())) + "\n暂无数据来源......")
        return -1

    # 数据库操作
    # 获取数据库链接
    connection = pymysql.connect(host="localhost",
                                 user="******",
                                 passwd="******",
                                 db="python",
                                 port=3306,
                                 charset="utf8")
    print('执行数据库操作')
    try:
        # 获取会话指针
        with connection.cursor() as cursor:
            # 创建sql语句
            sql = "insert into lianjia_house (`id`, `positionInfo`,`houseInfo`,`priceInfo`," \
                  "`followInfo`,`tag`,`titleinfo`) " \
                  "values (%s,%s,%s,%s,%s,%s,%s)"
            # 执行sql语句
            cursor.execute(sql, (
            0, house_list[1], house_list[2], house_list[5], house_list[3], house_list[5], house_list[0]))
            print(house_list[1])
            # 提交数据库
            connection.commit()
    finally:
        connection.close()
    return 1



def crawl_main(skuid):
    i = 0
    retry_times = 6
    domains = ["http://chehaiyang.com", "https://club.jd.com", "http://chehaiyang.cn"]
    while True:
        # 喷雾评论链接,通过更改page参数的值来循环读取多页评论信息
        url = choice(domains) + '/comment/productPageComments.action' \
                                '?productId=' + str(skuid) + \
              '&score=0' \
              '&sortType=6' \
              '&page=' + str(i) + \
              '&pageSize=10' \
              '&isShadowSku=0' \
              '&fold=1'
        i = i + 1
        if getHouseInfo(url, skuid) == -1:
            retry_times = retry_times - 1
            if retry_times < 0:
                print(time.asctime(time.localtime(time.time())) + ": All comments are crawled.", end="\n")
                break
            i = i - 1
            # 随机15~30秒请求范围 防止过度频繁请求
            randint = random.randint(15, 30)
            while randint > 0:
                print("\r", "{}th 正在重试中,请勿关闭窗口,程序执行完毕自动结束... in {} 秒...".format(6 - retry_times, randint),
                      end='', flush=True)
                # print(retry_times)
                time.sleep(1)
                randint -= 1
        else:
            retry_times = 6
            print("\r", "{}th page has been saved.".format(i), end='', flush=True)


"""
传递Sku编号ID进行调用
"""
if __name__ == '__main__':
    print(__name__)
    t = time.time()
    print(t)

    for num in range(1, 101):
        url = URL + str(num)
        print(url)

        getHouseInfo(url)
        time.sleep(1)
    t1 = time.time()
    print
    'Total time:'
    print(t1 - t - 100)
