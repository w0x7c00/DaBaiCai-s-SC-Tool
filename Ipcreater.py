from bs4 import BeautifulSoup
import urllib
import random
from selenium import webdriver
import requests
from lxml import etree

class ProxDeadException(Exception):
    def __init__(self):
        self.print_string="this prox website is dead please swich to other prox url"
    def __str__(self):
        return self.print_string

class AllProxDeadException(Exception):
    def __init__(self):
        self.print_string="All Prox  Web Site Dead"

    def __str__(self):
        return self.print_string

class IpCreater:
    def __init__(self):
        self.timeout=5
        self.prox_url_list=[ ['https://www.kuaidaili.com/free/inha/',self.pares_kuaidaili],['http://www.xicidaili.com/nn/',self.pares_xicidaili]]
        self.prox_url_index=0
        self.max_page=100    #最高查询到第100页
        self.browser = webdriver.Chrome()

        self.page_counter=1
        self.target_pares=self.prox_url_list[self.prox_url_index][1]
        self.target_url=self.prox_url_list[self.prox_url_index][0]
        self.ip_list=[]      #ip池

        self.reset_able_url_list()      #初始化ip池

    def exception_catcher(self):
        if self.prox_url_index==(len(self.prox_url_list)-1):
            raise AllProxDeadException
        else:
            self.prox_url_index += 1
            self.page_counter = 1
            self.target_url = self.prox_url_list[self.prox_url_index][0]
            self.target_pares=self.prox_url_list[self.prox_url_index][1]

    def reset_page(self,flags=False,target_page=None):
        if target_page!=None:
            self.page_counter=int(target_page)
        if flags:   #向前一页
            if self.page_counter==1:
                pass
            else:
                self.page_counter-=1
        else:
            if self.page_counter<=self.max_page:
                self.page_counter+=1

    def reset_able_url_list(self):
        url=self.target_url+str(self.page_counter)
        print(url)
        self.browser.get(url)
        try:
            self.target_pares()
        except ProxDeadException:
            self.exception_catcher()
            self.reset_able_url_list()

    def get_random_ip(self):
        if self.ip_list==[]:
            self.reset_page()
            self.reset_able_url_list()
            return self.get_random_ip()
        random_index=random.choice(range(len(self.ip_list)))
        random_ip=self.ip_list[random_index]
        del self.ip_list[random_index]
        return random_ip

    def append_ip(self,prox_ip):
        self.ip_list.append(prox_ip)


    def pares_xicidaili(self):        #默认的代理池解析函数
        soup = BeautifulSoup(self.browser.page_source, 'lxml')
        # self.browser.quit()
        ips = soup.find_all('tr')
        if len(ips)==0:
            raise ProxDeadException
        for i in range(1, len(ips)):
            ip_info = ips[i]
            tds = ip_info.find_all('td')
            ip_before_test = tds[1].text + ':' + tds[2].text
            my_header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
            }
            try:
                proxy_host = "http://" + ip_before_test
                proxy_temp = {"http": proxy_host}
                res = requests.get(self.target_url, timeout=self.timeout, proxies=proxy_temp, headers=my_header)
                self.ip_list.append(proxy_temp)
                print("http_ip合格")
                continue
            except Exception as e:
                print("http_ip不合格\n"+str(e))
                pass
            try:
                proxy_host = "http://" + ip_before_test
                proxy_temp = {"http": proxy_host}
                res = requests.get(self.target_url, timeout=2, proxies=proxy_temp, headers=my_header)
                self.ip_list.append(proxy_temp)
                print("https_ip合格")
                continue
            except Exception as e:
                pass
                # print(str(e))

    def pares_kuaidaili(self):
        etree_obj=etree.HTML(self.browser.page_source)
        tr_list=etree_obj.xpath("//div[@id='list']//tbody/tr")
        if len(tr_list)==0:
            raise ProxDeadException
        for i in tr_list:
            try :
                ip_before=i.xpath("./td[@data-title='IP']/text()")[0]+":"+i.xpath("./td[@data-title='PORT']/text()")[0]
                prox_temp={"http":"http://"+ip_before}
            except:
                pass
            my_header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
            }
            try:
                requests.get(self.target_url,timeout=self.timeout,headers=my_header,proxies=prox_temp)
                print("快代理ip测试通过！")
                self.ip_list.append(prox_temp)
                continue
            except Exception as e:
                print("快代理ip测试失败：\n"+str(e))

    def  __del__(self):
        self.browser.close()

if __name__=='__main__':
    creater=IpCreater()
    try:
        proxies = creater.get_random_ip()
    except Exception as e:
        print(str(e))
    response=requests.get("https://www.jd.com/?cu=true&utm_source=baidu-pinzhuan&utm_medium=cpc&utm_campaign=t_288551095_baidupinzhuan&utm_term=0f3d30c8dba7459bb52f2eb5eba8ac7d_0_e734e04ac1174c1a8f753bcbc2940218", proxies=proxies)
    print(response.text)