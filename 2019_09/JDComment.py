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
    # ����ʵ���ࣺ������Ʒ������ֻ������ԣ�������ʵ����Ȼ�����getData��ȡ���ݡ�
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
            "score": "%s" % (score),  # 1��ʾ������2��ʾ������3��ʾ����
            "sortType": "5",
            "page": "%s" % (page),
            "pageSize": "10",
            "isShadowSku": "0",
            "rid": "0",
            "fold": "1"
        }
        url = self.commentBaseUrl + urlencode(params)
        return params, url

    # def getpid(self):         #��prepare����
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
            logging.warning("״̬��������������쳣��")
            #print(response.text)
        html = etree.HTML(response.text)
        return html.xpath('//li[@class="gl-item"]/@data-sku')

    def getData(self, maxPage, score, ):  # maxPage����ȡ���۵����ҳ����ÿҳ10�����ݡ������ͺ��������һ��ҳ�벻��ͬ��һ������£�����>>����>����
        # maxPage����������ҳ����Զ���������������Ҳû�й�ϵ��
        # score��ָ�����������ͣ�����3������2������1��

        comments = []
        scores = []

        for j in range(len(self.productsId)):
            id = self.productsId[j]
            header = self.getHeaders(id)
            for i in range(1, maxPage):
                param, url = self.getParamUrl(id, i, score)
                print(">>>>>>>>>>>>>>>>�ڣ�%d ������ %d ҳ" % (j, i))
                try:
                    response = requests.get(url, headers=header, params=param)
                except Exception as e:
                    logging.warning(e)
                    break
                if response.status_code != 200:
                    logging.warning("״̬��������������쳣")
                    continue
                time.sleep(2)
                if response.text == '':
                    logging.warning("δ��ȡ����Ϣ")
                    continue
                #print(response.text)
                try:
                    res_json = json.loads(response.text)
                except Exception as e:
                    logging.warning(e)
                    continue
                if len((res_json['comments'])) == 0:
                    logging.warning("ҳ������ѵ���%d,������Χ" % (i))
                    break
                logging.info("������ȡ%s %s �� %d" % (self.categlory, self.comtype[score], i))
                for cdit in res_json['comments']:
                    comment = cdit['content'].replace("\n", ' ').replace('\r', ' ')
                    comments.append(comment)
                    scores.append(cdit['score'])
        savepath = './' + self.categlory + '_' + self.comtype[score] + '.csv'
        logging.warning("����ȡ%d �� %s ������Ϣ" % (len(comments), self.comtype[score]))
        with open(savepath, 'a+', encoding='utf8') as f:
            for i in range(len(comments)):
                print(i)
                # ���ݿ����
                # ��ȡ���ݿ�����
                connection = pymysql.connect(host="localhost",
                                             user="allon",
                                             passwd="123456",
                                             db="python",
                                             port=3306,
                                             charset="utf8")
                try:
                    # ��ȡ�Ựָ��
                    with connection.cursor() as cursor:
                        # ����sql���
                        sql = "insert into jd_comment_copy_401 (`skuid`, `productName`,`commentTime`,`content`,`images_str`) " \
                              "values (%s,%s,%s,%s,%s)"
                        # ִ��sql���
                        cursor.execute(sql, (i, self.categlory, time.time(), comments[i].replace("����", "������"), scores[i]))

                        # �ύ���ݿ�
                        connection.commit()
                finally:
                    connection.close()

                f.write("%d\t%s\t%s\n" % (i, scores[i], comments[i]))
        logging.warning("�����ѱ�����%s" % (savepath))


if __name__ == "__main__":
    list = ['��������ȥ��', 'ȫЧ������']
    #��������� ��ˮϴ������������Ʒ��ĭ����ǿ��ȥ�۳���������ϴ���๦����ĭ

    #�������������������ˮ�����������ƾ���к��Ӿ����粣����ˮ������������ˢ
    #�����ձ�����ƻ��
    #�������Ӿ�СԲ�� ����������Ʒ 360�ȸ���ɵ��ڹ�Ǿ����⾵�ޱ߿�ȥä�㸨�������������Ƭװ

    #, '�����ޱ�360��ä�㲣��СԲ��', '������ˮ��Ĥ', 'ȫЧ������', '��������ȥ��'
    for item in list:
        spider = JDSpider(item)
        # spider.getData(300, 3)
        # spider.getData(30, 2)
        # 1 ����  2 ����  3 ����
        spider.getData(30, 3)
