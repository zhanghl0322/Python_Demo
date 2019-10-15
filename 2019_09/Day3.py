import pymysql
import requests
from hashlib import md5
import re
import json
import os
import logging

logging.basicConfig(filename="test.log", level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 获取网页源代码
def get_one_page(url):
    # 设置请求头，防止被网站屏蔽
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)\
         AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except requests.HTTPError as e:
        print("由于某种原因获取页面出现错误!" + str(e))


# 爬出目标信息所在的网址
def parse_page1(url, list):
    # 获取网页内容
    html = get_one_page(url)
    # 将正则表达式编译成正则表达式对象
    pattern = re.compile('<h4><a href="(.*?)" target="_blank" data-eid', re.S)
    # 正则表达式1匹配的是目标信息的网址
    contents = re.findall(pattern, html)
    for i in contents:
        list.append(i)  # 向列表添加对象
    return list


# 从网址中爬出目标信息
def parse_page2(url, list):  # 信息
    # 获取网页内容
    url = 'https:' + url  #############要注意爬出的网址是否完整，不完整记得补全，否则会出错
    html = get_one_page(url)
    # 将正则表达式编译成正则表达式对象
    pattern = re.compile('<p class="intro">(.*?)</p>', re.S)
    # 正则表达式2匹配的是目标信息
    contents = re.findall(pattern, html)
    for i in contents:
        list.append(i)  # 向列表添加对象
    return list


def get_logger(self):
    return logging.getLogger(self.__logger_name)

# info_list存的是目标信息的网址
# info_list = []
#
# start_url = 'https://www.qidian.com/all'
# info_list = parse_page1(start_url, info_list)
#
# # range()包头不包尾`
# for i in range(1, 4):  # range(4,1,-1),-1表示顺序递减
#     url = 'https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=' + str(i)
#     info_list = parse_page1(url, info_list)
#
# # 输出目标网址
#
# cnt = 0
# for i in info_list:
#     cnt = cnt + 1
#     i = 'https:' + i
#     print(i)
#
# # 输出网址数量
#
# print("一共有" + str(cnt) + "条数据")
#
# # x_list存的是目标信息，从目标信息所在的网址爬出需要的目标信息
# x_list = []
# for i in info_list:
#     x_list = parse_page2(i, x_list)
#
# # 输出目标信息
# for i in x_list:
#     print(i)
# 如果爬的数量比较多，要等久一会才有输出
ssr_data = get_one_page('https://www.attackmen.com/ssr?page=1&limit=10')
print(json.dumps(ssr_data))
print(json.loads(ssr_data))
ssr_data_obj = json.loads(ssr_data)
print(ssr_data_obj['data'])


# 循环返回的json参数数据
for item in ssr_data_obj['data']:
    logger.info('{0}'
                '{1}'
                '{2}'
                '{3}'.format(item['country'], item['passwd'], item['method'], item['server']))
    pass
