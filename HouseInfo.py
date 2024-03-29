﻿import sys,os,json,time,requests,pandas as pd,numpy as np,requests as req
from datetime import datetime
import tkinter as tk
#about mail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from Info591 import Info591

# 設定使用者介面
def setUI():
    #設定鄉鎮市區
    _sec = [ c for c in county if c['id'] == regionVar.get()][0]['section']
    for i in range(0,len(chksSectVar)):
        chksSectVar[i].set(False)
        if i < len(_sec) :
            chksSect[i].config(text=_sec[i]['name'])
            chksSect[i].grid(sticky="W",row=(i // 9)+5,column=(i % 9))
        else:
            chksSect[i].grid_remove()

    #設定價格
    _rag = [ c for c in county if c['id'] == regionVar.get()][0]['priceRange']
    for i in range(0,len(chksPriceRangVar)):
        chksPriceRangVar[i].set(False)
        if i < len(_rag) :
            chksPriceRang[i].config(text=_rag[i]['name'])
            chksPriceRang[i].grid(sticky="W",columnspan=2,row=(i // 4)+11,column=(i % 4)*2)
        else:
            chksPriceRang[i].grid_remove()

# 取得所選的鄉鎮區
def getSection():
    _sec = [ c for c in county if c['id'] == regionVar.get()][0]['section']
    sOut = []
    for i in range(0,len(_sec)):
        if chksSectVar[i].get():
            sOut.append(_sec[i]['code'])
    return ','.join(sOut)

# 取得所選的價格
def getPriceRange():
    _pr = [ c for c in county if c['id'] == regionVar.get()][0]['priceRange']
    sOut = []
    for i in range(0,len(_pr)):
        if chksPriceRangVar[i].get():
            sOut.append(_pr[i]['code'])
    return ','.join(sOut)

# 寄出查詢結果
def mailInfo(result):
    #收件人用逗號串接
    mail_to = [elem.strip().split(',') for elem in receivers]

    #郵件基本設定
    msg = MIMEMultipart()
    msg['Subject'] = "法拍屋資訊" + datetime.now().strftime('%Y/%m/%d')
    msg['From'] = mail_from
    msg['To'] = ','.join(receivers)
    msg.preamble = 'Multipart massage.\n'

    #加入郵件本文
    part = MIMEText('\n'.join(result) ,'plain', 'utf-8')
    msg.attach(part)

    #連線smtp server
    smtp = smtplib.SMTP(urlSMTP)
    #smtp.set_debuglevel(1) #列印出和SMTP伺服器互動的所有資訊
    smtp.ehlo()
    smtp.starttls()
    smtp.login(mail_from, passwd)
    #寄信
    smtp.sendmail(msg['From'], mail_to , msg.as_string())

# 查詢
def execQry(_county=None,_section=None,_priceRange=None):
    if _county == None : _county = regionVar.get()
    if _section == None : _section = getSection()
    if _priceRange == None : _priceRange = getPriceRange()

    #查詢591資料
    dBgn = datetime.now()
    info = Info591(_county,_section,_priceRange)
    result = info.getInfo591()
    dEnd = datetime.now()
    result.append("所花時間:" + str((dEnd - dBgn).seconds))
    #新增視窗
    newWin = tk.Tk()
    #標題
    newWin.title('查詢結果')
    #視窗大小
    newWin.geometry('800x600')
    #設定捲軸
    ybar = tk.Scrollbar(newWin)
    ybar.pack(fill=tk.Y, side=tk.RIGHT)
    xbar = tk.Scrollbar(newWin,orient=tk.HORIZONTAL)
    xbar.pack(fill=tk.X, side=tk.BOTTOM,)
    #設定TextBox
    txtOut = tk.Text(newWin, height=50, width=120,yscrollcommand=ybar.set,xscrollcommand=xbar.set, wrap='none')
    txtOut.pack(fill=tk.BOTH)
    #設定捲軸的函數，這樣才可以滾動
    ybar.config(command=txtOut.yview)
    xbar.config(command=txtOut.xview)

    for s in result:
        if type(s) is str:
            #去除特殊字元
            s = ''.join([s[j] for j in range(len(s)) if ord(s[j]) in range(65536)])
            txtOut.insert(tk.END,s + '\n')
        else:
            txtOut.insert(tk.END,str(type(s)) + '\n')

    mailInfo(result)

    #進入事件迴圈
    newWin.mainloop()

# 主程式
if __name__ == '__main__':
    #縣市
    county = None
    #鄉鎮市區
    section = None
    #縣市價格區間
    priceRange = None
    #鄉鎮市區CheckBox
    chksSect = []
    #鄉鎮市區CheckBox value
    chksSectVar = []
    #價格區間CheckBox
    chksPriceRang = []
    #價格區間CheckBox value
    chksPriceRangVar = []
    # 縣/鄉鎮/價格
    _county ,_section ,_priceRange = None,None,None

    # 縣市/鄉鎮市區/價格區間
    with open(r'json\county.json', encoding='utf-8') as json_data: county = json.load(json_data)
    # 設定檔
    with open(r'json\config.json', encoding='utf-8') as json_data: cfgData = json.load(json_data)[0]

    # 信箱SMTP url
    urlSMTP = cfgData['urlSMTP']
    # 信箱登入密碼
    passwd = cfgData['passwd']
    # 寄件人信箱
    mail_from = cfgData['mail_from']
    # 收件人信箱
    receivers = cfgData['receivers']

    # 有加參數--auto，就直接查詢
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--auto':
        if "county" not in cfgData or len(cfgData["county"]) == 0: raise Exception("查無縣市設定")
        if "section" not in cfgData or len(cfgData["section"]) == 0: raise Exception("查無鄉真市區設定")
        _section = cfgData["section"]
        _county = cfgData["county"]
        _priceRange = cfgData["priceRange"]
        execQry(_county,_section,_priceRange)
    else: # 設定檔無預設值，就跳出畫面讓使用者選取
        #產生視窗
        my_window = tk.Tk()
        #標題
        my_window.title('591租屋網')
        #視窗大小
        my_window.geometry('600x400')
        # 設定標籤
        lb1 = tk.Label(my_window, text='縣市')
        lb1.grid(row=0,column=4)
        lb1 = tk.Label(my_window, text='鄉鎮市區')
        lb1.grid(row=4,column=4)
        lb1 = tk.Label(my_window, text='價格')
        lb1.grid(row=10,column=4)
        # 設定按鈕
        btnQry = tk.Button(my_window,text='查詢',command=execQry)
        btnQry.grid(row=14,column=4)

        #縣市radioButton
        cnt = 0
        regionVar = tk.StringVar()
        for c in county:
            rdo = tk.Radiobutton(my_window, text=c['name'], variable=regionVar, value=c['id'],command=setUI)
            rdo.grid(row=1 + (cnt // 9),column=cnt % 9)
            cnt += 1
        #設定預設值 1:台北
        regionVar.set('1')

        #初使化鄉鎮市CheckBox ※最多38個
        for i in range(0,38):
            chkValue = tk.BooleanVar()
            chksSect.append(tk.Checkbutton(my_window, text=str(i), var=chkValue))
            chksSectVar.append(chkValue)

        #初使化價格區間 ※最多7個
        for i in range(0,7):
            chkValue = tk.BooleanVar()
            chksPriceRang.append(tk.Checkbutton(my_window, text=str(i), var=chkValue))
            chksPriceRangVar.append(chkValue)

        setUI()

        #進入事件迴圈
        my_window.mainloop()
