# -*- coding:utf-8 -*-
import wx
import time
import json
import serial
import sqlite3
import requests
import threading
import webbrowser
from flask import Flask, request
from pubsub import pub

app = Flask(__name__)
@app.route("/",methods=['POST'])

# 接收LineToken的本地伺服器
def getData():
    if request.method == 'POST':
        client_id = "FKrX1kliCqcJg3ICgigaaM"
        redirect_uri = "http://127.0.0.1:5000"
        client_secret = "aziSIcxwcL1BfTlENprZREzYWyZ0tWTbGViXASfIvNZ"
        code = request.form.get('code')
        token_URL = "https://notify-bot.line.me/oauth/token?grant_type=authorization_code&redirect_uri={}&client_id={}&client_secret={}&code={}".format(redirect_uri, client_id, client_secret, code)
        token_r = requests.post(token_URL)
        if token_r.status_code == requests.codes.ok:
            access_token = json.loads(token_r.text)
            lineToken = access_token['access_token']
            wx.CallAfter(pub.sendMessage,"myRegisterListener",msg1="lineToken",msg2=lineToken)
            return "Connected Successfully"

# 登入介面
class Frame_Login(wx.Frame):
    
    # 介面繪製
    def __init__(self):
        wx.Frame.__init__(self, None, title='重機租借系統-登入', size=(417, 247),name='frame',style=541072384)
        self.qdck = wx.Panel(self)
        self.Centre()
        self.Account_label = wx.StaticText(self.qdck,size=(69, 24),pos=(74, 31),label='帳號：',name='staticText',style=2321)
        Account_label_font = wx.Font(12,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Account_label.SetFont(Account_label_font)
        self.Password_label = wx.StaticText(self.qdck,size=(69, 24),pos=(74, 74),label='密碼：',name='staticText',style=2321)
        Password_label_font = wx.Font(12,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Password_label.SetFont(Password_label_font)
        self.Account_textbox = wx.TextCtrl(self.qdck,size=(140, 26),pos=(147, 31),value='',name='text',style=0)
        Account_textbox_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Account_textbox.SetFont(Account_textbox_font)
        self.Password_textbox = wx.TextCtrl(self.qdck,size=(140, 26),pos=(147, 74),value='',name='text',style=2048)
        Password_textbox_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Password_textbox.SetFont(Password_textbox_font)
        self.Login_btn = wx.Button(self.qdck,size=(180, 32),pos=(107, 120),label='登入',name='button')
        Login_btn_font = wx.Font(12,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Login_btn.SetFont(Login_btn_font)
        self.Login_btn.Bind(wx.EVT_BUTTON,self.Login_btn_anbdj)
        self.NoMember_btn = wx.StaticText(self.qdck,size=(140, 24),pos=(128, 170),label='沒有會員嗎？註冊',name='staticText',style=2321)
        self.NoMember_btn.SetForegroundColour((0, 0, 255, 255))
        self.NoMember_btn.Bind(wx.EVT_LEFT_DOWN,self.NoMember_btn_sbzjax)
        wx.CallAfter(pub.subscribe,self.myListener,"myLoginListener")
        threading.Thread(target=cardListener,args=("1")).start()
        self.Bind(wx.EVT_CLOSE, self.onQuit)

    # 當登入介面關閉時
    def onQuit(self, event):
        pub.unsubscribe(self.myListener, "myLoginListener")
        wx.GetTopLevelParent(self).Destroy()
    
    # 創建一個監聽器，用來監聽其他介面傳輸過來的資料
    # 此為監聽讀卡機，如果有讀取到卡片就進行卡片登入的動作
    def myListener(self, msg):
        cardid = msg[1:-2]
        ret = loginByCard(cardid)
        if ret == -2:
            wx.MessageBox("登入失敗")
            return
        if ret == -1:
            frame = Frame_Register()
            wx.MessageBox("帳號不存在")
        elif ret == 0:
            frame = Frame_Rent()
            account = getAccountByCard(cardid)
            wx.CallAfter(pub.sendMessage,"myRentListener",msg=account)
            wx.MessageBox("登入成功")
        elif ret == 1:
            frame = Frame_Return()
            account = getAccountByCard(cardid)
            wx.CallAfter(pub.sendMessage,"myReturnListener",msg=account)
            wx.MessageBox("登入成功")
        self.Close()
        frame.Show(True)
    
    # 登入按鈕被按下，執行下面的程式碼
    def Login_btn_anbdj(self,event):
        account = self.Account_textbox.GetValue()
        password = self.Password_textbox.GetValue()
        if account != '' and password != '':
            ret = login(account,password)
            if ret == -1:
                wx.MessageBox("帳號不存在")
                return
            elif ret == -2:
                wx.MessageBox("登入失敗")
                return
            elif ret == 0:
                frame = Frame_Rent()
                wx.CallAfter(pub.sendMessage,"myRentListener",msg=account)
                wx.MessageBox("登入成功")
            elif ret == 1:
                frame = Frame_Return()
                wx.CallAfter(pub.sendMessage,"myReturnListener",msg=account)
                wx.MessageBox("登入成功")
            self.Close()
            frame.Show(True)
        else:
            wx.MessageBox('帳號密碼不能為空')

    # 註冊按鈕被按下，開啟註冊介面
    def NoMember_btn_sbzjax(self,event):
        frame = Frame_Register()
        frame.Show(True)

# 註冊介面
class Frame_Register(wx.Frame):

    # 介面繪製
    def __init__(self):
        wx.Frame.__init__(self, None, title='重機租借系統-註冊', size=(407, 300),name='frame',style=541071360)
        self.qdck = wx.Panel(self)
        self.Centre()
        self.Bind(wx.EVT_CLOSE,self.qdck_jbgb)
        self.Account_label = wx.StaticText(self.qdck,size=(69, 24),pos=(74, 31),label='帳號：',name='staticText',style=2321)
        Account_label_font = wx.Font(12,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Account_label.SetFont(Account_label_font)
        self.Password_label = wx.StaticText(self.qdck,size=(69, 24),pos=(74, 74),label='密碼：',name='staticText',style=2321)
        Password_label_font = wx.Font(12,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Password_label.SetFont(Password_label_font)
        self.Account_textbox = wx.TextCtrl(self.qdck,size=(160, 26),pos=(147, 31),value='',name='text',style=0)
        Account_textbox_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Account_textbox.SetFont(Account_textbox_font)
        self.Password_textbox = wx.TextCtrl(self.qdck,size=(160, 26),pos=(147, 74),value='',name='text',style=2048)
        Password_textbox_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Password_textbox.SetFont(Password_textbox_font)
        self.Notify_btn = wx.Button(self.qdck,size=(234, 32),pos=(71, 166),label='連動Line Notify',name='button')
        Notify_btn_font = wx.Font(10,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Notify_btn.SetFont(Notify_btn_font)
        self.Notify_btn.Bind(wx.EVT_BUTTON,self.Notify_btn_anbdj)
        self.Cardid_label = wx.StaticText(self.qdck,size=(80, 24),pos=(63, 118),label='卡片代碼：',name='staticText',style=2321)
        Cardid_label_font = wx.Font(12,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Cardid_label.SetFont(Cardid_label_font)
        self.Cardcode_textbox = wx.TextCtrl(self.qdck,size=(160, 26),pos=(147, 118),value='',name='text',style=16)
        Cardcode_textbox_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Cardcode_textbox.SetFont(Cardcode_textbox_font)
        self.Register_btn = wx.Button(self.qdck,size=(136, 32),pos=(122, 212),label='註冊',name='button')
        self.Register_btn.Bind(wx.EVT_BUTTON,self.Register_btn_anbdj)
        self.LineToken = wx.TextCtrl(self.qdck,size=(155, 22),pos=(132, 318),value='',name='text',style=16)
        self.LineToken.Hide()
        pub.subscribe(self.myListener,"myRegisterListener")
        threading.Thread(target=cardListener,args=("0")).start()

    # 當註冊介面關閉時
    def qdck_jbgb(self,event):
        threading.Thread(target=cardListener,args=("1")).start()
        self.Destroy()

    # 創建一個監聽器，用來監聽其他介面傳輸過來的資料
    # 此為監聽讀卡機及Notify連動，如果有讀取到卡片就把卡片代碼放在框框內；如果Line Notify連動成功就將連動按鈕關閉，使用戶不能再次按下
    def myListener(self, msg1,msg2):
        if msg1 == "lineToken":
            self.LineToken.Value = msg2
            self.Notify_btn.LabelText = "LineNotify連動成功"
            self.Notify_btn.Disable()
        elif msg1 == "cardCode":
            self.Cardcode_textbox.Value = msg2[1:-2]

    # Line Notify連動按鈕被按下
    def Notify_btn_anbdj(self,event):
        client_id = "FKrX1kliCqcJg3ICgigaaM"
        redirect_uri = "http://127.0.0.1:5000"
        threading.Thread(target=self.GetCode,args=(client_id,redirect_uri)).start()

    # 註冊按鈕被按下
    def Register_btn_anbdj(self,event):
        account = self.Account_textbox.GetValue()
        password = self.Password_textbox.GetValue()
        cardid = self.Cardcode_textbox.GetValue()
        lineToken = self.LineToken.GetValue()
        if account == "" or password == "" :
            wx.MessageBox("註冊資料不能為空")
            return

        if lineToken == "" or cardid == "":
            wx.MessageBox("請先連動LineNotify以及刷卡綁定")
            return

        if len(account) < 3 or len(password) < 3:
            wx.MessageBox("帳號或密碼長度不能小於3")
            return


        ret = register(account,password,cardid,lineToken)

        if ret == -1:
            wx.MessageBox("註冊失敗，帳號已存在")
            self.Account_textbox.Value = ""
            self.Password_textbox.Value = ""
            return

        if ret == -2:
            wx.MessageBox("註冊失敗，卡片已存在")
            self.Cardcode_textbox.Value = ""
            return
            
        if ret == 1:
            wx.MessageBox("註冊成功")
            self.Close()

    # 開啟Line Notify連動網頁
    def GetCode(self,client_id,redirect_uri):
        code_URL = 'https://notify-bot.line.me/oauth/authorize?response_type=code&scope=notify&response_mode=form_post&state=f094a459&client_id={}&redirect_uri={}'.format(client_id, redirect_uri) 
        webbrowser.open_new(code_URL)
        return

#租車界面
class Frame_Rent(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='重機租借系統-租車', size=(593, 450),name='frame',style=541071360)
        self.qdck = wx.Panel(self)
        self.Centre()
        self.data_label = wx.StaticText(self.qdck,size=(152, 24),pos=(210, 21),label='請輸入欲查詢資料：',name='staticText',style=2321)
        data_label_font = wx.Font(12,74,90,400,False,'Microsoft JhengHei UI',30)
        self.data_label.SetFont(data_label_font)
        self.Keyword_textbox = wx.TextCtrl(self.qdck,size=(168, 26),pos=(198, 52),value='',name='text',style=0)
        Keyword_textbox_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Keyword_textbox.SetFont(Keyword_textbox_font)
        self.Keyword_textbox.Bind(wx.EVT_TEXT,self.Keyword_textbox_nrbgb)
        self.cjlbk1 = wx.ListCtrl(self.qdck,size=(500, 263),pos=(39, 90),name='listCtrl',style=8227)
        self.cjlbk1.AppendColumn('車款型號', 0,180)
        self.cjlbk1.AppendColumn('排氣量', 0,100)
        self.cjlbk1.AppendColumn('車牌號碼', 0,140)
        self.cjlbk1.AppendColumn('是否可租借', 0,80)
        ret = findKeyword('')
        if len(ret) != 0:
            for i in ret:
                self.cjlbk1.Append(i)
        self.Rent_btn = wx.Button(self.qdck,size=(220, 30),pos=(177, 365),label='租車',name='button')
        self.Rent_btn.Bind(wx.EVT_BUTTON,self.Rent_btn_anbdj)
        self.account_textbox = wx.TextCtrl(self.qdck,size=(0, 0),pos=(198, 450),value='',name='text',style=0)
        self.account_textbox.Hide()
        pub.subscribe(self.myListener,"myRentListener")

    # 創建一個監聽器，用來監聽其他介面傳輸過來的資料
    # 此為監聽登入介面傳輸過來的帳號信息
    def myListener(self, msg):
        self.account_textbox.Value = msg
    
    # 當關鍵字的框框改變了，就利用關鍵字去搜尋資料庫，並顯示在介面上
    def Keyword_textbox_nrbgb(self,event):
        keyword = self.Keyword_textbox.Value
        self.cjlbk1.ClearAll()

        self.cjlbk1.AppendColumn('車款型號', 0,180)
        self.cjlbk1.AppendColumn('排氣量', 0,100)
        self.cjlbk1.AppendColumn('車牌號碼', 0,140)
        self.cjlbk1.AppendColumn('是否可租借', 0,80)

        ret = findKeyword(keyword)

        if len(ret) != 0:
            for i in ret:
                self.cjlbk1.Append(i)

    # 租借按鈕被按下
    def Rent_btn_anbdj(self,event):
        focusedItem = self.cjlbk1.GetFocusedItem()
        if focusedItem != -1:
            type = self.cjlbk1.GetItemText(focusedItem,col=0)
            cc = self.cjlbk1.GetItemText(focusedItem,col=1)
            plate = self.cjlbk1.GetItemText(focusedItem,col=2)
            ret = rentMotorcycle(self.account_textbox.Value,plate,type,cc)
            if ret:
                wx.MessageBox("租借成功")
                self.Destroy()
                frame = Frame_Login()
                frame.Show(True)
            else:
                wx.MessageBox("租借失敗，無法租借")
        else:
            wx.MessageBox("請先選擇要租借的車輛")

# 還車界面
class Frame_Return(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='重機租借系統-還車', size=(441, 285),name='frame',style=541071360)
        self.qdck = wx.Panel(self)
        self.Centre()
        self.account_label = wx.StaticText(self.qdck,size=(360, 24),pos=(50, 30),label='會員帳號：',name='staticText',style=17)
        account_label_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.account_label.SetFont(account_label_font)
        self.type_label = wx.StaticText(self.qdck,size=(360, 24),pos=(50, 70),label='車款型號：',name='staticText',style=17)
        type_label_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.type_label.SetFont(type_label_font)
        self.cc_label = wx.StaticText(self.qdck,size=(360, 24),pos=(50, 110),label='排氣量：',name='staticText',style=17)
        cc_label_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.cc_label.SetFont(cc_label_font)
        self.Return_btn = wx.Button(self.qdck,size=(301, 29),pos=(59, 190),label='還車',name='button')
        Return_btn_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.Return_btn.SetFont(Return_btn_font)
        self.Return_btn.Bind(wx.EVT_BUTTON,self.Return_btn_anbdj)
        self.plate_label = wx.StaticText(self.qdck,size=(360, 24),pos=(50, 150),label='車牌號碼：',name='staticText',style=17)
        plate_label_font = wx.Font(11,74,90,400,False,'Microsoft JhengHei UI',30)
        self.plate_label.SetFont(plate_label_font)
        self.account_textbox = wx.TextCtrl(self.qdck,size=(0, 0),pos=(198, 450),value='',name='text',style=0)
        self.account_textbox.Hide()
        pub.subscribe(self.myListener,"myReturnListener")
        
    # 創建一個監聽器，用來監聽其他介面傳輸過來的資料
    # 此為監聽登入介面傳輸過來的帳號信息
    def myListener(self, msg):
        self.account_label.LabelText = f'會員帳號：{msg}'
        self.account_textbox.Value = msg
        type,cc,plate = getRentDataByAccount(msg)
        self.type_label.LabelText = f"車款型號：{type}"
        self.cc_label.LabelText = f"排氣量：{cc}"
        self.plate_label.LabelText = f"車牌號碼：{plate}"

    # 還車按鈕被按下
    def Return_btn_anbdj(self,event):
        type,cc,plate = getRentDataByAccount(self.account_textbox.Value)
        returnMotorcycle(self.account_textbox.Value,plate,type,cc)
        wx.MessageBox("歸還成功")
        self.Destroy()
        frame = Frame_Login()
        frame.Show(True)

# 初始化界面
class myApp(wx.App):
    def  OnInit(self):
        self.frame = Frame_Login()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

'''
函數名稱:login
參數:帳號,密碼
返回值:-1不存在用戶,-2登入失敗,0登入成功(租車界面),1登入成功(還車界面)

1.利用用戶輸入的帳號，去資料庫中尋找是否存在，如果帳號不存在 返回-1
2.如果帳號存在，再去比對用戶輸入的密碼是否一致，如果密碼錯誤 返回-2
3.如果密碼正確，去資料庫中檢查他是否有租車
有租車 返回1（顯示還車界面）
沒有租車 返回0（顯示租車界面）

'''
def login(account,password):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute('SELECT Account FROM Members;')
    flag = 0
    ret = 0
    for i in db.fetchall():
        if account in i:
            flag=1
            break
    if flag:
        db.execute(f'SELECT Password FROM Members WHERE Account = "{account}";')
        if db.fetchone()[0] == password:
            db.execute(f'SELECT IsRent FROM Members WHERE Account = "{account}";')
            ret =  int(db.fetchone()[0])
            lineToken = getUserNotifyToken(1,account)
            sendLineNotify(lineToken,f'\n登入成功\n會員帳號：{account}\n您登入的時間是：\n{getTime()}')
        else:
            ret = -2
    else:
        ret = -1
    conn.close()
    return ret

'''
函數名稱:getAccountByCard
參數:卡片代碼
返回值:這張卡片的會員帳號

逼卡後會有卡片代碼，利用卡片代碼去資料庫中尋找這張卡片的會員帳號

'''
def getAccountByCard(cardCode):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute(f'SELECT Account FROM Members WHERE CardCode = "{cardCode}" ;')
    ret = db.fetchone()[0]
    conn.close()
    return ret

'''
函數名稱:loginByCard
參數:卡片代碼
返回值:-1用戶不存在 , 1目前有租車(要還車) , 0目前沒有租車(要租車)

1.利用用戶逼卡的卡號，去資料庫中尋找會員是否存在，如果帳號不存在 返回-1
2.如果帳號存在，去資料庫中檢查他是否有租車
有租車 返回1（顯示還車界面）
沒有租車 返回0（顯示租車界面）

'''
def loginByCard(cardCode):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute('SELECT CardCode FROM Members;')
    flag = 0
    ret = 0
    for i in db.fetchall():
        if cardCode in i:
            flag=1
            break
    if flag:
        db.execute(f'SELECT IsRent FROM Members WHERE CardCode = "{cardCode}";')
        ret = int(db.fetchone()[0])
        lineToken = getUserNotifyToken(0,cardCode)
        sendLineNotify(lineToken,f'\n登入成功\n會員帳號：{getAccountByCard(cardCode)}\n您登入的時間是：\n{getTime()}')
    else:
        ret = -1
    conn.close()
    return ret

'''
函數名稱:getUserNotifyToken
參數:模式,帳號(卡號)
返回值:用戶的LineToken，用於發送推播訊息

如果模式 = 1，代表利用帳號去搜尋LineToken
如果模式 = 0，代表利用卡號去搜尋LineToken
資料庫操作，應該看得懂吧，懶得寫注釋了

'''
def getUserNotifyToken(mode,arg):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    if mode:
        db.execute(f'SELECT LineToken FROM Members WHERE Account = "{arg}";')
    else:
        db.execute(f'SELECT LineToken FROM Members WHERE CardCode = "{arg}";')
    token = db.fetchone()[0]
    conn.close()
    return token

'''
函數名稱:register
參數:帳號,密碼,卡號,LineToken
返回值:-1帳號已存在 , -2卡片已註冊 , 1註冊成功

1.先去搜尋帳號是否存在在資料庫中，如果資料庫中有相同帳號，代表已經有人註冊了 返回-1
2.接著搜尋卡片是否存在在資料庫中，如果資料庫中有相同卡號，代表有人已經綁定那張卡片了== 不能重複註冊 返回-2
3.以上都符合資格的話，就將用戶資料寫入資料庫中，用戶資料 = "帳號、密碼、卡號、lineToken、是否租車(預設為0)"

'''
def register(account,password,cardid,lineToken):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute('SELECT * FROM Members;')
    for i in db.fetchall():
        if account == i[0]:
            return -1
        elif cardid == i[2]:
            return -2
    db.execute(f'INSERT INTO Members VALUES ("{account}", "{password}","{cardid}","{lineToken}",0);')
    conn.commit()
    conn.close()
    return 1

'''
函數名稱:findKeyword
參數:關鍵字
返回值:得到的結果

去資料庫中比對每一筆資料，如果該筆資料內有關鍵字存在，就將他保存在ret這個串列內
最後再將ret返回回去

'''
def findKeyword(keyword):
    ret = []
    plate = ''
    type = ''
    cc = ''
    state = ''
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute('SELECT * FROM Rent;')
    rentData = db.fetchall()
    if keyword != "":
        for i in rentData:
            for j in i:
                if j != None:
                    if keyword in j:
                        plate = i[0]
                        type = i[1]
                        cc = i[2]
                        state = "可" if i[3] == '0' else "不可"
                        ret.append([type,cc,plate,state])
                        break
    else:
        for i in rentData:
            plate = i[0]
            type = i[1]
            cc = i[2]
            state = "可" if i[3] == '0' else "不可"
            ret.append([type,cc,plate,state])
    conn.close()
    return ret

'''
函數名稱:rentMotorcycle
參數:帳號,車牌,型號,排氣量
返回值:1租車成功 , 0租車失敗

1.先去確認renter這個欄位是否是空的
2.如果是空的代表沒有人租車，所以可以租借，將renter欄位寫入他的帳號，代表他為租借人，並且發送推播通知，告知租借成功的訊息 返回1
如果不是空的代表有人租走了，所以不能租借 返回0

'''
def rentMotorcycle(account,plate,type,cc):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute(f'SELECT Renter FROM Rent WHERE Plate = "{plate}" AND Type = "{type}" AND CC = "{cc}";')
    renter = db.fetchone()[0]
    if renter == "" or renter == None:
        db.execute(f'UPDATE Rent SET State = "1" WHERE Plate = "{plate}" AND Type = "{type}" AND CC = "{cc}";')
        db.execute(f'UPDATE Rent SET Renter = "{account}" WHERE Plate = "{plate}" AND Type = "{type}" AND CC = "{cc}";')
        db.execute(f'UPDATE Members SET IsRent = "1" WHERE Account = "{account}";')
        conn.commit()
        conn.close()
        lineToken = getUserNotifyToken(1,account)
        sendLineNotify(lineToken,f'\n租借成功\n會員帳號：{account}\n車款型號：{type}\n排氣量：{cc}\n車牌號碼：{plate}\n您租借的時間是：\n{getTime()}')
        return 1
    else:
        return 0

'''
函數名稱:returnMotorcycle
參數:帳號,車牌,型號,排氣量
返回值:沒有返回值

將State欄位改為0，Renter改為空，IsRent改為0，推播還車成功的訊息

'''
def returnMotorcycle(account,plate,type,cc):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute(f'UPDATE Rent SET State = "0" WHERE Plate = "{plate}" AND Type = "{type}" AND CC = "{cc}";')
    db.execute(f'UPDATE Rent SET Renter = "" WHERE Plate = "{plate}" AND Type = "{type}" AND CC = "{cc}";')
    db.execute(f'UPDATE Members SET IsRent = "0" WHERE Account = "{account}";')
    conn.commit()
    conn.close()
    lineToken = getUserNotifyToken(1,account)
    sendLineNotify(lineToken,f'\n歸還成功\n會員帳號：{account}\n車款型號：{type}\n排氣量：{cc}\n車牌號碼：{plate}\n您歸還的時間是：\n{getTime()}')
    return

'''
函數名稱:getRentDataByAccount
參數:帳號
返回值:租車的信息

利用帳號去資料庫尋找Renter這個欄位 = 他的帳號
返回 型號,排氣量,車牌

'''
def getRentDataByAccount(account):
    conn = sqlite3.connect('rent.db')
    db = conn.cursor()
    db.execute(f'SELECT * FROM Rent WHERE Renter = {account};')
    data = list(db.fetchone())
    return data[1],data[2],data[0]

'''
函數名稱:getTime
參數:沒有參數
返回值:現在時間

取得現在的時間，並返回回去，用於租車還車時的時間通知

'''
def getTime():
    return time.strftime("%Y/%m/%d\n%H:%M:%S",time.localtime())


'''
函數名稱:sendLineNotify
參數:LineToken,訊息
返回值:是否成功(200 = 成功)

將要傳的對象及內容發送給Line的伺服器，而Line的伺服器會幫我們傳送給要傳的對象

'''
def sendLineNotify(lineToken,msg):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Authorization' : 'Bearer ' + lineToken
    }
    payload = {'message' : msg}
    r = requests.post(url,headers=headers,params=payload)
    return r.status_code #200 = 成功

'''
函數名稱:cardListener
參數:模式
返回值:沒有返回值

監聽是否有卡片讀取
如果模式 = 0，代表是註冊讀取
如果模式 = 1，代表是登入讀取

'''
def cardListener(arg):
    global ser
    while ser == 0:
        try:
            ser = serial.Serial('COM3', 9600, timeout=None)
        except:
            ser = 0
        time.sleep(1)
    if ser.isOpen():
        ser.close()
        time.sleep(0.5)
        ser.open()
        data = ser.readline()
        data = data.decode('utf-8')
        if data != "":
            if arg == "0":
                wx.CallAfter(pub.sendMessage,"myRegisterListener",msg1="cardCode",msg2=data)
            elif arg == "1":
                wx.CallAfter(pub.sendMessage,"myLoginListener",msg=data)
    return

'''
這裡為此程式開始的位置
首先會先嘗試開啟讀卡機，如果不能開啟就會將ser這個變數設置為0，代表沒有讀卡機
接著開啟接收LineToken的本地伺服器
最後開啟登入介面，然後將畫面做循環繪製

'''
if __name__ == '__main__':
    global ser
    try:
        ser = serial.Serial('COM3', 9600, timeout=None)
    except:
        ser = 0
    threading.Thread(target=app.run).start()
    app = myApp()
    app.MainLoop()