import sys,os,json,time,requests,pandas as pd,numpy as np,requests as req
from datetime import datetime
import tkinter as tk
#about mail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from Info591 import Info591

def setUI():
    #設定鄉鎮市區
    _sec = section[regionVar.get()]
    for i in range(0,len(chksSectVar)):
        chksSectVar[i].set(False)
        if i < len(section[regionVar.get()]) :
            chksSect[i].config(text=list(_sec.values())[i])
            chksSect[i].grid(sticky="W",row=(i // 9)+5,column=(i % 9))
        else:
            chksSect[i].grid_remove()

    #設定價格
    _rag = priceRange[regionVar.get()]
    for i in range(0,len(chksPriceRangVar)):
        chksPriceRangVar[i].set(False)
        if i < len(priceRange[regionVar.get()]) :
            chksPriceRang[i].config(text=list(_rag.values())[i])
            chksPriceRang[i].grid(sticky="W",row=(i // 3)+11,column=(i % 3)*3)
        else:
            chksPriceRang[i].grid_remove()
            
def getSection(): 
    xx = section[regionVar.get()]
    sOut = []
    for i in range(0,len(xx)):
        if chksSectVar[i].get():
            sOut.append(list(xx.keys())[i])
    return ','.join(sOut)

def getPriceRange():
    xx = priceRange[regionVar.get()]
    sOut = []
    for i in range(0,len(xx)):
        if chksPriceRangVar[i].get():
            sOut.append(list(xx.keys())[i])
    return ','.join(sOut)

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

    # 縣市
    with open(r'json\county.json', encoding='utf-8') as json_data: county = json.load(json_data)[0]
    # 鄉鎮市區
    with open(r'json\section.json', encoding='utf-8') as json_data: section = json.load(json_data)[0]
    # 縣市價格區間
    with open(r'json\priceRange.json', encoding='utf-8') as json_data: priceRange = json.load(json_data)[0]
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

    # 設定檔已有預設值，就直接查詢
    if "county" in cfgData and len(cfgData["county"]) > 0 and "section" in cfgData and len(cfgData["section"]) > 0 and "priceRange" in cfgData and len(cfgData["priceRange"]) > 0 :
        _county = cfgData["county"]
        _section = cfgData["section"]
        _priceRange = cfgData["priceRange"]
        execQry(_county,_section,_priceRange)
    else: # 設定檔無預設值，就跳出畫面讓使用者選取
        #產生視窗
        my_window = tk.Tk()
        #標題
        my_window.title('591租屋網')
        #視窗大小
        my_window.geometry('600x400')

        lb1 = tk.Label(my_window, text='縣市')
        lb1.grid(row=0,column=4)

        #縣市radioButton
        r,c=0,0
        cnt = 0
        regionVar = tk.StringVar()
        for k,v in county.items():
            rdo = tk.Radiobutton(my_window, text=v, variable=regionVar, value=k,command=setUI)
            rdo.grid(row=1 + (cnt // 9),column=cnt % 9)
            cnt += 1

        #設定預設值 1:台北
        regionVar.set('1')
        lb2 = tk.Label(my_window, text='鄉鎮市區')
        lb2.grid(row=4,column=4)

        #初使化鄉鎮市CheckBox ※最多38個
        for i in range(0,38):
            chkValue = tk.BooleanVar()
            chksSect.append(tk.Checkbutton(my_window, text=str(i), var=chkValue))
            chksSectVar.append(chkValue)

        lb1 = tk.Label(my_window, text='價格')
        lb1.grid(row=10,column=4)

        #初使化價格區間 ※最多7個
        for i in range(0,7):
            chkValue = tk.BooleanVar()
            chksPriceRang.append(tk.Checkbutton(my_window, text=str(i), var=chkValue))
            chksPriceRangVar.append(chkValue)

        setUI()

        btnQry = tk.Button(my_window,text='查詢',command=execQry)
        btnQry.grid(row=14,column=4)

        #進入事件迴圈
        my_window.mainloop()

