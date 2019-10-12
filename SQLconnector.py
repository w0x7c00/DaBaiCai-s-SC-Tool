import mysql.connector
class SQLconnector():
    def __init__(self,data_base_host,user,password,data_base,port=3306,rank='user'):
        self.rank=rank
        self._init_list={
            'mul_select_num':5
        }
        self.DataBaseConfig = {
            'host': data_base_host,
            'user': user,
            'password': password,
            'port': port,
            'database':data_base,
            'charset': 'utf8'
        }
        if self.rank=='manager':
            self.DataBaseConfig['user']='manager'
            self.DataBaseConfig['password']='deng13508108659'
    def _new_connector(self):#生成连接器
        try:
            self.connector = mysql.connector.connect(**self.DataBaseConfig)
            self.connector_cursor = self.connector.cursor()
            return True
        except Exception as e:
            print(self.rank+'的数据库启动失败！\n'+ str(e)) #for test
            return False
    def get_data(self,sqlstr):#执行sql语句 并且关闭数据库  返回结果
        self.sqlstr = sqlstr
        if self.sqlstr == '':
            print("run stop because of string is not input")
            return None   #返回None
        else:
            self._new_connector()
            try:
                self.connector_cursor.execute(self.sqlstr)
                result = self.connector_cursor.fetchall()
            except mysql.connector.Error as e:
                print('连接失败!{}'.format(e))
                result = None
            finally:
                self.connector.commit()
                self._close()
            if result == []:
                return None
            else:
                return result
    def set_data(self,sqlstr):#插入数据函数 成功返回True 反之为False
        self.sqlstr=sqlstr
        if self.sqlstr=='':
            print("run stop because of string is not input")
            return False
        else:
            self._new_connector()
            try:
                self.connector_cursor.execute(self.sqlstr)
                self.connector.commit()
                self._close()
                return True
            except mysql.connector.Error as e:
                print('connect fails!{}'.format(e))
                self.connector.commit()
                self._close()
                return False
    def _close(self):
        self.connector_cursor.close()
        self.connector.close()

if __name__=="__main__":
    data_base_host = '127.0.0.1'
    user = 'root'
    password = ''
    data_base = ''
    # mysql连接
    sql_connector = SQLconnector(data_base_host, user, password, data_base,rank='manager')
    sql_str='''create table if not exit 'basic_data_inf' (
           'id' int unsigned  auto_ increment
           'price'  varchar(10) ,
            'str' varchar(100)  ,
            'link'   varchar(100) ,
            primary key('id') 
    ) '''
    sql_connector.set_data(sql_str)