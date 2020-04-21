# coding=gbk
import requests
from lxml import etree
import logging
from urllib.parse import quote
import json
from urllib.parse import urlencode
import time
import pymysql as pymysql


class JDSpider:
    # 爬虫实现类：传入商品类别（如手机、电脑），构造实例。然后调用getData爬取数据。
    def __init__(self, categlory):
        self.startUrl = "https://search.jd.com/Search?keyword=%s&enc=utf-8" % (quote(categlory))
        self.commentBaseUrl = "https://sclub.jd.com/comment/productPageComments.action?"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
        self.productsId = self.getId()
        self.comtype = {1: "nagetive", 2: "medium", 3: "positive"}
        self.categlory = categlory
        self.iplist = {
            'http': [],
            'https': []
        }

    def getParamUrl(self, productid, page, score):
        params = {
            "productId": "%s" % (productid),
            "score": "%s" % (score),  # 1表示差评，2表示中评，3表示好评
            "sortType": "5",
            "page": "%s" % (page),
            "pageSize": "10",
            "isShadowSku": "0",
            "rid": "0",
            "fold": "1"
        }
        url = self.commentBaseUrl + urlencode(params)
        return params, url

    # def getpid(self):         #被prepare代替
    #     response = requests.get(self.startUrl,headers = self.headers)
    #     html = etree.HTML(response.text.decode("utf-8",errors ='ignore'))
    #     goodsId = html.xpath('//li[@class="gl-item"]/@data-pid')
    #     return goodsId

    def getHeaders(self, productid):
        header = {"Referer": "https://item.jd.com/%s.html" % (productid),
                  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
                  }
        return header

    def getId(self):
        print(self.startUrl)
        response = requests.get(self.startUrl, headers=self.headers)
        if response.status_code != 200:
            logging.warning("状态码错误，爬虫连接异常！")
            #print(response.text)
        html = etree.HTML(response.text)
        return html.xpath('//li[@class="gl-item"]/@data-sku')

    def getData(self, maxPage, score, ):  # maxPage是爬取评论的最大页数，每页10条数据。差评和好评的最大一般页码不相同，一般情况下：好评>>差评>中评
        # maxPage遇到超出的页码会自动跳出，所以设大点也没有关系。
        # score是指那种评价类型，好评3、中评2、差评1。

        comments = []
        scores = []

        for j in range(len(self.productsId)):
            id = self.productsId[j]
            header = self.getHeaders(id)
            for i in range(1, maxPage):
                param, url = self.getParamUrl(id, i, score)
                print(">>>>>>>>>>>>>>>>第：%d 个，第 %d 页" % (j, i))
                try:
                    response = requests.get(url, headers=header, params=param)
                except Exception as e:
                    logging.warning(e)
                    break
                if response.status_code != 200:
                    logging.warning("状态码错误，爬虫连接异常")
                    continue
                time.sleep(2)
                if response.text == '':
                    logging.warning("未爬取到信息")
                    continue
                #print(response.text)
                try:
                    res_json = json.loads(response.text)
                except Exception as e:
                    logging.warning(e)
                    continue
                if len((res_json['comments'])) == 0:
                    logging.warning("页面次数已到：%d,超出范围" % (i))
                    break
                logging.info("正在爬取%s %s 第 %d" % (self.categlory, self.comtype[score], i))
                for cdit in res_json['comments']:
                    comment = cdit['content'].replace("\n", ' ').replace('\r', ' ')
                    comments.append(comment)
                    scores.append(cdit['score'])
        savepath = './' + self.categlory + '_' + self.comtype[score] + '.csv'
        logging.warning("已爬取%d 条 %s 评价信息" % (len(comments), self.comtype[score]))
        with open(savepath, 'a+', encoding='utf8') as f:
            for i in range(len(comments)):
                print(i)
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
                        sql = "insert into jd_comment_copy_401 (`skuid`, `productName`,`commentTime`,`content`,`images_str`) " \
                              "values (%s,%s,%s,%s,%s)"
                        # 执行sql语句
                        cursor.execute(sql, (i, self.categlory, time.time(), comments[i].replace("京东", "车海洋"), scores[i]))

                        # 提交数据库
                        connection.commit()
                finally:
                    connection.close()

                f.write("%d\t%s\t%s\n" % (i, scores[i], comments[i]))
        logging.warning("数据已保存在%s" % (savepath))


if __name__ == "__main__":
    list = ['汽车内饰去污', '全效美容蜡']
    #【内饰清洁 免水洗神器】汽车用品泡沫清洁剂强力去污车用内饰清洗剂多功能泡沫

    #秒速汽车玻璃防雨剂驱水剂汽车玻璃镀晶雨敌后视镜挡风玻璃驱水剂防雨隐形雨刷
    #阿克苏冰糖心苹果
    #汽车后视镜小圆镜 倒车汽车用品 360度高清可调节广角镜反光镜无边框去盲点辅助镜防雨防雾两片装

    #, '汽车无边360度盲点玻璃小圆镜', '玻璃驱水镀膜', '全效美容蜡', '汽车内饰去污'
    for item in list:
        spider = JDSpider(item)
        # spider.getData(300, 3)
        # spider.getData(30, 2)
        # 1 差评  2 中评  3 好评
        spider.getData(30, 3)
