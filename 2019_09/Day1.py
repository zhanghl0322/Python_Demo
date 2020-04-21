import urllib.request
import json
import time
import random
import pymysql as pymysql
from random import choice
import sys


def crawlProductComment(url, skuid):
    # 读取原始数据(注意选择gbk编码方式)
    try:
        html = urllib.request.urlopen(url).read().decode('gbk', 'ignore')
    except Exception:
        return -1

    data = json.loads(html)

    if len(data['comments']) == 0:
        print(time.asctime(time.localtime(time.time())) + "\nSeems no more data to crawl")
        return -1

    for comment in data['comments']:
        product_name = comment['referenceName']
        comment_time = comment['creationTime']
        content = comment['content']
        nickname = comment['nickname']
        # 数据库操作
        # 获取数据库链接
        connection = pymysql.connect(host="localhost",
                                     user="allon",
                                     passwd="123456",
                                     db="python",
                                     port=3306,
                                     charset="utf8")
        try:
            # 获取会话指针
            with connection.cursor() as cursor:
                # 创建sql语句
                sql = "insert into jd_comment (`skuid`, `productName`,`commentTime`,`content`,`images_str`) " \
                      "values (%s,%s,%s,%s,%s)"
                # 执行sql语句
                cursor.execute(sql, (skuid, product_name, comment_time, content, nickname))

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
        if crawlProductComment(url, skuid) == -1:
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
crawl_main(29014664942)