#by DaBaiCai
#v1.0
#2019.10.12
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import csv
import time
import os
#import SQLconnector
from queue import Queue
import requests
import Ipcreater
from requests.exceptions import ReadTimeout, ConnectionError, RequestException
import json
import threading

class SubmitException(Exception):
    def __init__(self):
        pass

class App:
    def __init__(self,master):
        self.gui_inf_pack={
            "input_type":None,
            "input_str":None,
            "threads":None,
            "use_prox":None,
            "output_str":None
        }
        self.max_threads=20
        self.master=master
        self.init_for_test()
        self.init_master("DaBaiCai`s SC Tool",1,"600x400")
        self.init_widgets()
    def runHelper_dir(self):
        mytime = time.localtime()
        timestr = str(mytime.tm_year) +"_"+ str(mytime.tm_mon)+"_" + str(mytime.tm_mday) +"_"+ str(mytime.tm_hour) +"_"+ str(mytime.tm_min)+"_"+str(mytime.tm_sec)
        return timestr
    def runHelper_replace_char(self,str):
        r_str=str
        r_str_len=len(r_str)
        for i in range(r_str_len):
            if r_str[i]=='\\':
                r_str=r_str[0:i]+'/'+r_str[i+1:r_str_len]
        return r_str
    def run(self):
        self.gui_inf_pack["input_type"]=self.value_choice_input.get()
        if self.gui_inf_pack["input_type"]==2:
            self.gui_inf_pack["input_str"]=self.runHelper_replace_char(self.input_entry_value.get())
        else:
            self.gui_inf_pack["input_str"]=self.input_entry_value.get()
        thread_number=int(self.thread_conf_int_value.get())
        if (thread_number==self.thread_conf_int_value.get()) and thread_number>=1 and thread_number<=self.max_threads:
            self.gui_inf_pack["threads"]=thread_number
        else:
            messagebox.showwarning('erro', 'threads number must drop in 1~'+str(self.max_threads))
        self.gui_inf_pack["use_prox"]=self.choice_prox_value.get()
        output_str=self.runHelper_replace_char(str(self.output_entry_value.get()))
        if output_str=="":
            messagebox.showwarning('erro', 'illegal output format')
        if output_str[-1]=='/':
            output_str=output_str+self.runHelper_dir()
        else:
            output_str = output_str +"/"+ self.runHelper_dir()
        self.gui_inf_pack["output_str"]=output_str
        for i in self.gui_inf_pack:
            print(i+":"+str(self.gui_inf_pack[i]))
        #***************************************
        #屏蔽run事件
        self.run_btn.pack_forget()
        #entry
        entry(self.gui_inf_pack)
        #初始化threads

        #开启run事件
        self.run_btn.pack(side=TOP)
        #***************************************
    def init_for_test(self):#测试网络连通并且获取本机ip
        pass
    def choice_path_input(self):
        #need:打开选择窗口 master失去焦点
        local_get_path = ""
        local_get_path = askdirectory()
        self.input_entry_value.set(local_get_path)

    def command_choice_output(self):
        # need:打开选择窗口 master失去焦点
        local_get_path = ""
        local_get_path = askdirectory()
        self.output_entry_value.set(local_get_path)

    def command_choice_input(self):
        if self.value_choice_input.get()==2:
            self.choice_path_input()
        else:
            self.input_entry_value.set("")

    def init_widgets(self):
        self.init_frame_input()
        self.init_frame_conf()
        self.init_frame_output()
        self.init_wgs_run_btn()
    def init_master(self,title_str,title_ico,geometry_str):
        self.master.title(title_str)
        #self.master.iconbitmap(title_ico)
        self.master.geometry(geometry_str)
    def init_wgs_run_btn(self):
        self.run_btn=ttk.Button(self.master,
                                text="Run!",
                                command=self.run
                                )
        self.run_btn.pack(side=TOP)
    def init_frame_input(self):
        frame_input=ttk.LabelFrame(self.master,width=100,height=100,text="choice input")
        frame_input.pack(side=TOP,fill=X,padx=20)
        frame_innerInput=ttk.Label(frame_input)
        frame_innerInput.pack(side=TOP)
        self.value_choice_input=IntVar()
        self.value_choice_input.set(0)
        ttk.Radiobutton(frame_innerInput,
                        variable=self.value_choice_input,
                        value=0,
                        text="URL",
                        command=self.command_choice_input
                        ).pack(side=LEFT,padx=30,pady=10)
        ttk.Radiobutton(frame_innerInput,
                        variable=self.value_choice_input,
                        value=1,
                        text="PythonCode",
                        command=self.command_choice_input
                        ).pack(side=LEFT, padx=30, pady=10)
        ttk.Radiobutton(frame_innerInput,
                        variable=self.value_choice_input,
                        value=2,
                        text="CSV",
                        command=self.command_choice_input
                        ).pack(side=LEFT, padx=30, pady=10)
        ttk.Radiobutton(frame_innerInput,
                        variable=self.value_choice_input,
                        value=3,
                        text="JsonFile",
                        command=self.command_choice_input
                        ).pack(side=LEFT, padx=30, pady=10)
        # Text(frame_input,text="input").pack(side=TOP,
        #                                          anchor=W,
        #                                          font=('StSong', 20)
        #                                          )
        self.input_entry_value=StringVar()
        self.input_entry_value.set("")
        self.input_entry=ttk.Entry(frame_input,
                  width=30,
                textvariable=self.input_entry_value,
                  font=('StSong', 14),
                  foreground='blue'
                  )
        self.input_entry.pack(fill=BOTH,side=TOP,pady=20,padx=30)

    #配置选项/choice confige(like Theads number)
    def init_frame_conf(self):
        self.frame_conf=ttk.LabelFrame(self.master,text="configure")
        self.frame_conf.pack(
            fill=X,
            padx=20,
            side=TOP,
            pady=10,
        )
        ttk.Label(self.frame_conf,text="Theads:").pack(side=LEFT,padx=10,pady=20)
        self.thread_conf_int_value = IntVar()
        self.thread_conf_int_value.set(4)
        # 创建Combobox组件
        self.frame_conf_thread_box = ttk.Combobox(self.frame_conf,
                               textvariable=self.thread_conf_int_value,  # 绑定到self.strVar变量
                               values=[1,2,3,4,5,6,7,8,9,10],
                                width=10
                               )  # 当用户单击下拉箭头时触发self.choose方法
        self.frame_conf_thread_box.pack(side=LEFT,
                                        padx=10)
        ttk.Label(self.frame_conf,text="Use Prox:").pack(
            side=LEFT,padx=30)
        self.choice_prox_value=IntVar()
        ttk.Radiobutton(self.frame_conf,
                        variable=self.choice_prox_value,
                        value=0,
                        text="Yes",
                        ).pack(side=LEFT)

        #使用获取本机访问ip填充
        ttk.Radiobutton(self.frame_conf,
                        variable=self.choice_prox_value,
                        value=1,
                        text="No(Use own ip)",
                        command=self.command_choice_input
                        ).pack(side=LEFT, padx=30)
    def init_frame_output(self):
        self.frame_output=ttk.LabelFrame(self.master,text="output")
        self.frame_output.pack(
            fill=X,
            padx=20,
            side=TOP,
            pady=10,
        )
        self.output_entry_value=StringVar()
        self.output_entry=ttk.Entry(
            self.frame_output,
            textvariable=self.output_entry_value,
            font=('StSong', 14),
            foreground='blue',
            width=35
        )
        self.output_entry.pack(
            side=LEFT,
            padx=20,
            pady=20,
            fill=X
        )
        ttk.Button(self.frame_output,
                   text="choice path",
                   command=self.command_choice_output
                   ).pack(side=LEFT,padx=20)

#爬虫线程类
class ThreadCrawl(threading.Thread):
    def __init__(self,thread_id,threads_list,ip_creater,work_queue,threadLock,workLock,ipCreaterLock,output_dir,use_prox=True):
        #调用父类初始化函数
        super(ThreadCrawl, self).__init__()
        self.my_prox=""
        self.thread_id=thread_id
        self.ip_creater=ip_creater    #ip池对象
        self.request_header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        self.out_time=5
        self.work_queue=work_queue
        self.use_prox=use_prox
        self.ipCreaterLock=ipCreaterLock
        self.workLock=workLock
        self.output_dir=output_dir
        self.threadLock=threadLock
        self.threads_list=threads_list
    def run(self):
        print(str(self.thread_id)+"is running")
        while True:
            try:
                if self.use_prox:
                    self.my_prox=self.get_prox()
                else:
                    pass
                if self.work_queue.empty():
                    time.sleep(2)
                if self.work_queue.empty():
                    print("空队列 线程退出")
                    break
                self.workLock.acquire()
                work_item = self.work_queue.get(block=False)
                self.workLock.release()
                url=work_item[1]
                work_index=work_item[0]
                print("get!!!")
                print(work_item)
                if self.use_prox:
                    response = requests.get(url, timeout=self.out_time,proxies=self.my_prox,headers=self.request_header)
                else:
                    response = requests.get(url, timeout=self.out_time,headers=self.request_header)
                if response.status_code != 200:
                    self.workLock.acquire()
                    self.work_queue.put(url, block=False)
                    self.workLock.release()
                    continue
            except ReadTimeout:
                # 超时异常
                self.workLock.acquire()
                self.work_queue.put(work_item,block=False)
                self.workLock.release()
                print('Timeout error')
            except ConnectionError:
                self.workLock.acquire()
                self.work_queue.put(work_item, block=False)
                self.workLock.release()
                # 连接异常
                print('Connection error')
            except RequestException:
                # self.workLock.acquire()
                # self.work_queue.put(work_item, block=False)
                # self.workLock.release()
                # 请求异常
                print('Request error')
            else:

                os.mkdir(self.output_dir)
                with open(self.output_dir+"\\"+str(work_index)+".html","w",encoding='utf-8',errors='ignore') as f:
                    f.write(response.content.decode("utf-8"))
                # except:
                #     print("输出文件"+str(work_index)+"失败")
                #time.sleep(1)
                if self.use_prox:
                    self.ipCreaterLock.acquire()
                    self.ip_creater.append_ip(self.my_prox)
                    self.ipCreaterLock.release()
                else:
                    pass
        self.threadLock.acquire()
        #排出此threads
        self.threads_list[self.thread_id]=None
        self.threadLock.release()
        print("thread"+str(self.thread_id)+" is dead")

    def get_prox(self):
        self.ipCreaterLock.acquire()
        my_prox=self.ip_creater.get_random_ip()
        self.ipCreaterLock.release()
        print("线程取得prox ip：\n"+str(my_prox))
        return my_prox

def entry(inf_pack):
    #填充work_list
    work_list = []
    if inf_pack["input_type"]==0:   #url
        work_list.append([0,inf_pack["input_str"]])
    elif inf_pack["input_type"]==1:  #python code
        try:
            exec(inf_pack["input_str"])
        except:
            messagebox.showerror("erro","can`t run the input python code")
            return 0
        try:
            test_val=url_list
        except:
            messagebox.showerror("erro", "python code must return a list named url_list")
            return 0
        if type(url_list)=="list":
            if len(url_list)>=1:
                pass
            else:
                messagebox.showerror("erro", "url_list is empty!cheak your code")
                return 0
        else:
            messagebox.showerror("erro", "python code must return a list named url_list")
            return 0
        for i in range(len(url_list)):
            work_list.append([i,url_list[i]])
    elif inf_pack["input_type"] == 2:  #csv
        try:
            f_read=open(inf_pack["input_str"],'r')
            csv_reader=csv.reader(f_read)
            counter=0
            for i in csv_reader:
                work_list.append([counter,i[0]])
                counter+=1
        except:
            messagebox.showerror("erro", "can`t open this csv file or no such file")
            return 0
        #扩展解决超大量csv的url问题
        #生成work_list填充线程
        #主线程退出自旋的条件
    work_length = len(work_list)

    #thread_id,ip_creater,work_queue,data_list,workLock,dataLock,ipCreaterLock,use_prox=True
    #线程传入参数配置
    #ip_creater = Ipcreater.IpCreater()
    work_queue = Queue(work_length)
    ipCreaterLock = threading.Lock()
    threadLock= threading.Lock()
    workLock = threading.Lock()
    threads = []
    for i in work_list:
        workLock.acquire()
        work_queue.put(i)
        workLock.release()
        #thread_id,threads_list,ip_creater,work_queue,threadLock,workLock,ipCreaterLock,output_dir,use_prox=True
    for i in range(int(inf_pack["threads"])):
        thread_loc_val=ThreadCrawl(
            i,
            threads,
            Ipcreater.IpCreater(),
            work_queue,
            threadLock,
            workLock,
            ipCreaterLock,
            inf_pack["output_str"],
        )
        threads.append(thread_loc_val)
        thread_loc_val.run()
    while True:
        outFlag=True
        for i in threads:
            if i!=None:
                outFlag=False
        if outFlag:
            break
if __name__=="__main__":
    baseWindow=Tk()
    App(baseWindow)
    baseWindow.mainloop()