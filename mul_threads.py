import threading
from lxml import etree
import time
import re
import json
import SQLconnector
from queue import Queue
import requests
import Ipcreater
from requests.exceptions import ReadTimeout, ConnectionError, RequestException
import csv
from flask import *

work_list=[]
work_length=20

for i in range(work_length):
    work_list.append("https://search.jd.com/Search?keyword=手机&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=手机&cid2=653&cid3=655&page={0}&s=1&click=0".format(str(1+2*i)))
exitFlag=False
ipCreaterLock=threading.Lock()
dataLock=threading.Lock()
workLock=threading.Lock()
ip_creater=Ipcreater.IpCreater()
threads=[]
dataList=[]
workQueue=Queue(work_length)

#填充work队列
for i in work_list:
    workLock.acquire()
    workQueue.put(i)
    workLock.release()

#爬虫线程类
class ThreadCrawl(threading.Thread):
    def __init__(self,thread_id,ip_creater,work_queue):
        #调用父类初始化函数
        super(ThreadCrawl, self).__init__()
        self.my_prox=""
        self.thread_id=thread_id
        self.ip_creater=ip_creater    #ip池对象
        self.request_header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        self.out_time=5
        self.work_queue=work_queue
    def run(self):
        print(str(self.thread_id)+"is running")
        while not exitFlag:
            try:
                self.my_prox=self.get_prox()
                if self.work_queue.empty():
                    time.sleep(2)
                workLock.acquire()
                if self.work_queue.empty():
                    workLock.release()
                    break
                url = self.work_queue.get(block=False)
                workLock.release()

                response = requests.get(url, timeout=self.out_time,proxies=self.my_prox,headers=self.request_header)
                if response.status_code != 200:
                    workLock.acquire()
                    self.work_queue.put(url, block=False)
                    workLock.release()
                    continue
            except ReadTimeout:
                # 超时异常
                workLock.acquire()
                self.work_queue.put(url,block=False)
                workLock.release()

                print('Timeout error')
            except ConnectionError:
                workLock.acquire()
                self.work_queue.put(url, block=False)
                workLock.release()
                # 连接异常
                print('Connection error')
            except RequestException:
                workLock.acquire()
                self.work_queue.put(url, block=False)
                workLock.release()
                # 请求异常
                print('Request error')
            except Exception as e:
                print("*****其他requests异常*****："+str(e))
            else:
                dataLock.acquire()
                dataList.append(response.content.decode("utf-8"))
                dataLock.release()
                #time.sleep(1)
                ipCreaterLock.acquire()
                self.ip_creater.append_ip(self.my_prox)
                ipCreaterLock.release()

        print(str(self.thread_id)+"\tis dead")

    def get_prox(self):
        ipCreaterLock.acquire()
        my_prox=self.ip_creater.get_random_ip()
        ipCreaterLock.release()
        print("线程取得prox ip：\n"+str(my_prox))
        return my_prox

def pares(str):
    return_list=[]
    html = etree.HTML(str)
    ul = html.xpath("//div[@id='J_goodsList']")[0].xpath("./ul")
    li_list = ul[0].xpath("./li")
    for i in li_list:
        f_list = []
        f_list.append(i.xpath("./div/div[@class='p-price']")[0].xpath("./strong/i/text()")[0])
        f_list.append(i.xpath("./div/div[contains(@class,'p-name')]")[0].xpath("./a/em/text()")[0])
        page_url = i.xpath("./div/div[@class='p-img']/a/@href")[0]
        if re.match(r'^https:', page_url) == None:
            page_url = "https:" + page_url
        f_list.append(page_url)
        return_list.append(f_list)
    return return_list

def task_run():
    pass

for i in range(5):
    ThreadCrawl(i,ip_creater,workQueue).start()

# while True:
#     workLock.acquire()
#     state = workQueue.empty()
#     workLock.release()
#     if state==True:
#         break
# exitFlag=True
# print(dataList[0])
while True:
    if len(dataList)==work_length:
        exitFlag=True
        print("线程退出")
        break

pares_list=[]

for i in dataList:
    try:
        m=pares(i)
        print(m)
        pares_list.append(m)
    except Exception as e:
        pass
print(len(pares_list))

data_base_host='127.0.0.1'
user='root'
password='deng13508108659'
data_base='database1'
#mysql连接
sql_connector=SQLconnector.SQLconnector(data_base_host,user,password,data_base)

csv_path='F:\Learn\PyProject\data.csv'
f=open(csv_path,'a')
my_csv_writer=csv.writer(f)
for i in pares_list:
    my_csv_writer.writerows(i)
f.close()

brans_list=[['小米'],['华为','huawei','HUAWEI'],['荣耀','HONER','honer'],['Redmi','红米','redmi'],['一加','OnePlus'],['Apple','苹果'],['联想','Lenove'],['天语','T-touch'],['oppo','OPPO'],['海信','Hisense'],['ROG','华硕'],['vivo','VIVO'],['诺基亚'],['努比亚'],['中兴'],['魅族'],['realme'],['索尼'],['酷派']]
for i in pares_list:
    for j in i:
        str1=j[1]
        for m in brans_list:
            for n in m:
                if str1.find(n)!=(-1):
                    j.append(m[0])
for i in pares_list:
    for j in i:
        if len(j)==3:
            j.append('other')

for i in pares_list:
    for j in i:
        if len(j)==5:
            if j[3]==j[4]:
                del j[4]
            else:
                if j[3]=='华为' or j[3]=='小米':
                    del j[3]
                else:
                    del j[4]
        elif len(j)==6:
            if j[3]=='Redmi' or j[3]== '荣耀':
                del j[5]
                del j[4]
            elif j[4] == 'Redmi' or j[4]=='荣耀':
                del j[5]
                del j[3]
            elif j[5] == 'Redmi' or j[5]=='荣耀':
                del j[4]
                del j[3]

brans_list_one=[]
for i in brans_list:
    brans_list_one.append(i[0])
brans_list_one.append('other')
price_dict_brand={}
for i in brans_list_one:
    price_dict_brand[i]=[]
for i in pares_list:
    for j in i:
        price_dict_brand[j[3]].append(j[0])
print(price_dict_brand)
for i in price_dict_brand:
    sum=0
    for j in price_dict_brand[i]:
        sum+=float(j)
    p_price=sum/len(price_dict_brand[i])
    price_dict_brand[i]=p_price
print(price_dict_brand)
