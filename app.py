#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import websocket, json, datetime, sqlite3, hashlib, hmac, requests, random, datetime
def savelog(msg):
    try:
        f = open("log.txt", "r", encoding='utf-8')
        d = f.read()
        f.close()
        f = open("log.txt", "w", encoding='utf-8')
        f.write('\n'+str(datetime.datetime.now())+'\n'+str(msg)+'\n'+d)
        f.close()
    except:
        f = open("log.txt", "w", encoding='utf-8')
        f.write('\n'+str(datetime.datetime.now())+'\n'+str(msg)+'\n')
        f.close()
def on_close(connect):
    savelog('core : การเชื่อมต่อได้หยุดลง')
def temp(hash):
    try:
        fopen = open('temp.json','r', encoding="utf-8")
        f = json.load(fopen)
        fopen.close()
        f['HASH']=hash
        fopen = open('temp.json','w', encoding="utf-8")
        json.dump(f,fopen,indent=4)
        fopen.close()
    except Exception as error_is:
        print('temp.json error : '+str(error_is))
def temp_clear():
    try:
        fopen = open('temp.json','r', encoding="utf-8")
        f = json.load(fopen)
        fopen.close()
        f['HASH']=""
        f['CLEAR']=0
        fopen = open('temp.json','w', encoding="utf-8")
        json.dump(f,fopen,indent=4)
        fopen.close()
    except Exception as error_is:
        print('temp.json clear error : '+str(error_is))
def send_buy_order(rate, ordersize):
    with open('config.json','r') as openfile:
        config = json.load(openfile)
    API_HOST = 'https://api.bitkub.com'
    API_KEY = config['KEY']
    API_SECRET = bytes(config['SECRET'], encoding= 'utf-8')
    def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)
    def sign(data):
        j = json_encode(data)
        h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()
    response = requests.get(API_HOST + '/api/servertime')
    servertime = int(response.text)
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': API_KEY
    }
    data = {
        'sym': 'THB_'+config['COIN'],
        'amt': ordersize,
        'rat': rate,
        'typ': 'limit',
        'ts': servertime
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(API_HOST + '/api/market/place-bid', headers=header, data=json_encode(data))
    ex_response=json.loads(response.text)
    if ex_response['error']==0:
        temp(ex_response['result']['hash'])
        return 1
    else:
        savelog('Send buy order error : '+str(ex_response['error']))
        return 0
def send_sell_order(rate,amt):
    with open('config.json','r') as openfile:
        config = json.load(openfile)
    API_HOST = 'https://api.bitkub.com'
    API_KEY = config['KEY']
    API_SECRET = bytes(config['SECRET'], encoding= 'utf-8')
    def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)
    def sign(data):
        j = json_encode(data)
        h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()
    response = requests.get(API_HOST + '/api/servertime')
    servertime = int(response.text)
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': API_KEY
    }
    data = {
        'sym': 'THB_'+config['COIN'],
        'amt': amt,
        'rat': rate,
        'typ': 'limit',
        'ts': servertime
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(API_HOST + '/api/market/place-ask', headers=header, data=json_encode(data))
    ex_response=json.loads(response.text)
    if ex_response['error']==0:
        temp(ex_response['result']['hash'])
        return 1
    else:
        savelog('Send sell order error : '+str(ex_response['error']))
        return 0
def send_sell_order_clear(rate,amt):
    with open('config.json','r') as openfile:
        config = json.load(openfile)
    API_HOST = 'https://api.bitkub.com'
    API_KEY = config['KEY']
    API_SECRET = bytes(config['SECRET'], encoding= 'utf-8')
    def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)
    def sign(data):
        j = json_encode(data)
        h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()
    response = requests.get(API_HOST + '/api/servertime')
    servertime = int(response.text)
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': API_KEY
    }
    data = {
        'sym': 'THB_'+config['COIN'],
        'amt': amt,
        'rat': rate,
        'typ': 'limit',
        'ts': servertime
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(API_HOST + '/api/market/place-ask', headers=header, data=json_encode(data))
    ex_response=json.loads(response.text)
    if ex_response['error']==0:
        temp(ex_response['result']['hash'])
        try:
            fopen = open('temp.json','r', encoding="utf-8")
            f = json.load(fopen)
            fopen.close()
            f['CLEAR']=1
            fopen = open('temp.json','w', encoding="utf-8")
            json.dump(f,fopen,indent=4)
            fopen.close()
        except Exception as error_is:
            print('temp.json sell clear error : '+str(error_is))
        return 1
    else:
        savelog('Send sell order clear error : '+str(ex_response['error']))
        return 0
def order_info():
    with open('config.json','r') as openfile:
        config = json.load(openfile)
    with open('temp.json','r') as openfile:
        rtemp = json.load(openfile)
    API_HOST = 'https://api.bitkub.com'
    API_KEY = config['KEY']
    API_SECRET = bytes(config['SECRET'], encoding= 'utf-8')
    def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)
    def sign(data):
        j = json_encode(data)
        h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()
    response = requests.get(API_HOST + '/api/servertime')
    servertime = int(response.text)
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': API_KEY
    }
    data = {
        'hash': rtemp['HASH'],
        'ts': servertime
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(API_HOST + '/api/market/order-info', headers=header, data=json_encode(data))
    order_info_res=json.loads(response.text)
    if order_info_res['error']!=0:
        savelog('Order info error : '+str(order_info_res['error']))
    return order_info_res
def my_history_by_taker(takercount):
    with open('config.json','r') as openfile:
        config = json.load(openfile)
    API_HOST = 'https://api.bitkub.com'
    API_KEY = config['KEY']
    API_SECRET = bytes(config['SECRET'], encoding= 'utf-8')
    def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)
    def sign(data):
        j = json_encode(data)
        h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()
    response = requests.get(API_HOST + '/api/servertime')
    servertime = int(response.text)
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': API_KEY
    }
    data = {
        'sym': 'THB_'+config['COIN'],
        'lmt': takercount,
        'ts': servertime
    }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(API_HOST + '/api/market/my-order-history', headers=header, data=json_encode(data))
    new_order_history=json.loads(response.text)
    if new_order_history['error']!=0:
        savelog('My history by taker error : '+str(new_order_history['error']))
    return new_order_history
def cancel_order():
    with open('config.json','r') as openfile:
        config = json.load(openfile)
    API_HOST = 'https://api.bitkub.com'
    API_KEY = config['KEY']
    API_SECRET = bytes(config['SECRET'], encoding= 'utf-8')
    def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)
    def sign(data):
        j = json_encode(data)
        h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()
    response = requests.get(API_HOST + '/api/servertime')
    servertime = int(response.text)
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-APIKEY': API_KEY
    }
    with open('temp.json','r', encoding="utf-8") as openfile:
        rtemp = json.load(openfile)
    data = {
    'hash': rtemp['HASH'],
    'ts': servertime
            }
    signature = sign(data)
    data['sig'] = signature
    response = requests.post(API_HOST + '/api/market/cancel-order', headers=header, data=json_encode(data))
    ex_response=json.loads(response.text)
    if ex_response['error']==0:
        temp('')
        return 1
    else:
        savelog('Cancel order error : '+str(ex_response['error']))
        return 0
def line(order_no,side,price,thb_amt,profit):
    try:
        if config['LINE']==1:  
            if side=="buy":
                stickers_open = ['17839','17849','17852','17851','17860','17861','17866','17878']
                linesticker = random.choice(stickers_open)
                headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+config['LINETOKEN']}                
                msg = '\nออเดอร์ที่ : '+str(order_no)+'\nซื้อ : '+config['COIN']+'\nที่ราคา : '+str(price)+' บาท\nจำนวน : '+str(thb_amt)+' บาท'
                s = requests.post('https://notify-api.line.me/api/notify', headers=headers, data = {"message":msg,"stickerPackageId":"1070","stickerId":linesticker})
                if s.status_code != 200:
                    savelog("line send error")
                    return 0
                else:
                    return 1
            else:
                stickers_profit = ['17840','17842','17844','17847','17854']
                stickers_loss = ['17855','17856','17857','17858','17859','17868','17870','17873']
                if profit>=0:
                    msg = '\nขาย : '+config['COIN']+'\nออเดอร์ที่ : '+str(order_no)+'\nที่ราคา : '+str(price)+' บาท\nกำไร : '+str(abs(int(profit*10000)/10000))+' บาท'
                    linesticker = random.choice(stickers_profit)
                else:
                    msg = '\nขาย : '+config['COIN']+'\nออเดอร์ที่ : '+str(order_no)+'\nที่ราคา : '+str(price)+' บาท\nขาดทุน : '+str(abs(int(profit*10000)/10000))+' บาท'
                    linesticker = random.choice(stickers_loss)
                headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+config['LINETOKEN']}
                s= requests.post('https://notify-api.line.me/api/notify', headers=headers, data = {"message":msg,"stickerPackageId":"1070","stickerId":linesticker}) 
                if s.status_code != 200:
                    savelog("line send error")  
                    return 0 
                else:
                    return 1 
        else:
            return 1
    except Exception as error_is:
        savelog('line function : '+str(error_is))
        return 0
def line_clear(ordercount, price):
    try:
        if config['LINE']==1:  
            stickers_profit = ['17840','17842','17844','17847','17854']
            msg = '\nเคลียร์ออเดอร์ : '+config['COIN']+'\nจำนวนออเดอร์ : '+str(ordercount)+'\nที่ราคา : '+str(price)+' บาท'
            linesticker = random.choice(stickers_profit)
            headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+config['LINETOKEN']}
            s= requests.post('https://notify-api.line.me/api/notify', headers=headers, data = {"message":msg,"stickerPackageId":"1070","stickerId":linesticker}) 
            if s.status_code != 200:
                savelog("line send error")
                return 0 
            else:
                return 1 
        else:
            return 1
    except Exception as error_is:
        savelog('line clear function : '+str(error_is))
        return 0
def on_message(connect, message):
    try:
        msg = json.loads(message)
        ask = msg['lowestAsk']
        bid = msg['highestBid']
        askbid_print = 'Ask : '+str(ask)+'\nBid : '+str(bid)
        bid_better = ((50/100)*(ask-bid))+bid
    except:
        raise
    try:
        try:
            fopen = open('last_active.txt', 'w', encoding='utf-8')
            fopen.write(str(datetime.datetime.today()))
            fopen.close()
        except Exception as error_is:
            savelog('บันทึกวันเวลาที่ใช้งานบอทล่าสุดใส่ last_active.txt ไม่ได้')
        with open('config.json','r') as openfile:
            config = json.load(openfile)
        with open('temp.json','r') as openfile:
            rtemp = json.load(openfile)
        dbcon = sqlite3.connect('Bitkub-SYY.db')
        dbcursor = dbcon.cursor()
        dbcursor.execute("create table if not exists orders(id integer primary key, hash text, rate float, thb_amt float, coin_amt float, fee_amt float)")
        dbcursor.execute("create table if not exists sold(id integer primary key, rate_buy float, rate_sell float, total_profit float)")
        dbcursor.execute('select * from orders')
        db_res = dbcursor.fetchall()
        db_ordercount = len(db_res)
        db_show = ""
        if db_ordercount > 0:
            coin_total = 0
            thb_total = 0
            fee_total = 0
            db_show += '\n'
            for x in db_res:
                db_show += str(x[0])+' -- '+str(x[2])+' -- '+str(x[1])+'\n'
                coin_total += x[4]
                thb_total += x[3]
                fee_total += x[5]
            dbcursor.execute('select * from sold')
            db_sold_res = dbcursor.fetchall()
            db__sold_ordercount = len(db_sold_res)
            sold_profit_total = 0
            if db__sold_ordercount > 0:
                for x in db_sold_res:
                    sold_profit_total += x[3]
            break_even = (((((fee_total/thb_total)*100)*2)/100)*((thb_total-sold_profit_total)/coin_total))+((thb_total-sold_profit_total)/coin_total)
            db_show += 'Break-even : '+str(break_even)
            db_show += '\n\n'
        else:
            db_show += '\n'
            db_show += '-- No Order --'
            db_show += '\n\n'
        condition_print = ""
        if rtemp['HASH'] == "":
            if db_ordercount == 0:
                if config['STOPNEXTCIRCLE'] != 0:
                    condition_print += "zZZ"
                else:
                    cmd = send_buy_order(bid_better, config['ORDERSIZE'])
                    if cmd == 1:
                        condition_print += "buy order sent :-)"
                    else:
                        condition_print += "buy order error T_T"
            else:
                if ask-((ask-bid)/2)>break_even and config['CLEAR_EVERY_BE']==1 and db_ordercount>=config['CLEAR_ORDER_COUNT']:
                    dbcursor.execute('select * from orders')
                    db_all_order = dbcursor.fetchall()
                    db_sum_coin_amt = 0
                    for x in db_all_order:
                        db_sum_coin_amt += x[4]
                    cmd = send_sell_order_clear(ask-((ask-bid)/2), db_sum_coin_amt)
                    if cmd == 1:
                        condition_print += "clear sell order sent :-)"
                    else:
                        condition_print += "clear sell order error T_T"
                else:
                    dbcursor.execute('select * from orders where id=?',(db_ordercount,))
                    db_last_order = dbcursor.fetchall()
                    minimum_price_to_sell = (((((db_last_order[0][5]/db_last_order[0][3])*100)*2)/100)*db_last_order[0][2])+db_last_order[0][2]
                    if db_last_order[0][2]+config['PRICERANGE']<minimum_price_to_sell:
                        if db_ordercount == 1:
                            price_to_sell = break_even
                        else:
                            price_to_sell = minimum_price_to_sell
                    else:
                        price_to_sell = db_last_order[0][2]+config['PRICERANGE']
                    if bid<=db_last_order[0][2]-config['PRICERANGE']:
                        if db_ordercount<config['MAX_ORDER']:
                            cmd = send_buy_order(bid, db_last_order[0][3])
                            if cmd == 1:
                                condition_print += "DCA buy order sent :-)"
                            else:
                                condition_print += "DCA buy order error T_T"
                        else:
                            if ask>db_last_order[0][2]:
                                condition_print += 'wait price to '+str(price_to_sell)
                            elif bid<db_last_order[0][2]:
                                if config['MAX_ORDER']>1:
                                    condition_print += 'DCA wait price to '+str(db_last_order[0][2]-config['PRICERANGE'])
                                else:
                                    condition_print += 'wait price to '+str(price_to_sell)
                            else:
                                condition_print += "wait! wait! wait!"
                            condition_print += ", OrderCount ("+str(db_ordercount)+"/"+str(config['MAX_ORDER'])+")"
                    elif ask>price_to_sell:
                        cmd = send_sell_order(ask, db_last_order[0][4])
                        if cmd == 1:
                            if db_ordercount == 1:
                                condition_print += "sell order sent :-)"
                            else:
                                condition_print += "DCA sell order sent :-)"
                        else:
                            if db_ordercount == 1:
                                condition_print += "sell order error T_T"
                            else:
                                condition_print += "DCA sell order error T_T"
                    else:
                        if ask>db_last_order[0][2]:
                            if break_even<=price_to_sell and config['CLEAR_EVERY_BE']==1 and db_ordercount>=config['CLEAR_ORDER_COUNT']:
                                condition_print += 'wait price to '+str(break_even)+', to clear'
                            else:
                                condition_print += 'wait price to '+str(price_to_sell)
                        elif bid<db_last_order[0][2]:
                            if db_ordercount<config['MAX_ORDER']:
                                condition_print += 'DCA wait price to '+str(db_last_order[0][2]-config['PRICERANGE'])
                        else:
                            condition_print += "wait! wait! wait!"               
        else:
            info_order = order_info()
            if info_order['result']['side'] == 'buy':
                if info_order['result']['status'] == 'filled':
                    order_history_count = len(info_order['result']['history'])
                    history_by_taker = my_history_by_taker(order_history_count)
                    order_thb_amount = 0
                    order_coin_amount = 0
                    order_fee_amount = 0
                    for x in info_order['result']['history']:
                        order_thb_amount += x['amount']
                    for x in history_by_taker['result']:
                        order_coin_amount += x['amount']
                    for x in info_order['result']['history']:
                        order_fee_amount += x['fee']
                    dbcursor.execute('insert into orders (hash,rate,thb_amt,coin_amt,fee_amt)values(?,?,?,?,?)',(rtemp['HASH'],info_order['result']['rate'],order_thb_amount,order_coin_amount,order_fee_amount))
                    dbcon.commit()
                    condition_print += 'Buy Filled'
                    temp('')
                    line(db_ordercount+1,"buy",info_order['result']['rate'],order_thb_amount,0)
                elif info_order['result']['status'] == 'cancelled':
                    temp_clear()
                    condition_print += 'buy order cancelled by user (*_*)'
                else:
                    if bid > info_order['result']['rate']:
                        cmd = cancel_order()
                        if cmd == 1:
                            condition_print += 'buy order cancelled!'
                        else:
                            condition_print += 'cancel buy order error (O_O\')'
                    else:
                        condition_print += 'buy limit at '+str(info_order['result']['rate'])+', '
                        condition_print += 'wait for fill buy (O_O)'
            else:
                info_order = order_info()
                if rtemp['CLEAR'] == 1:
                    dbcursor.execute('select * from orders')
                    db_all_order = dbcursor.fetchall()
                    thb_all_amt = 0
                    for x in db_all_order:
                        thb_all_amt += x[3]
                    if info_order['result']['status'] == 'filled':
                        order_history_count = len(info_order['result']['history'])
                        history_by_taker = my_history_by_taker(order_history_count)
                        order_coin_amount = 0
                        order_fee_amount = 0
                        for x in history_by_taker['result']:
                            order_coin_amount += x['amount']
                        for x in info_order['result']['history']:
                            order_fee_amount += x['fee']
                        thb_amt_pay = thb_all_amt
                        thb_amt_rec = order_coin_amount*info_order['result']['rate']
                        profit_with_fee = (thb_amt_rec-thb_amt_pay)-order_fee_amount
                        dbcursor.execute('delete from sold')
                        dbcon.commit()
                        dbcursor.execute('delete from orders')
                        dbcon.commit()
                        temp_clear()
                        line_clear(db_ordercount,info_order['result']['rate'])
                    elif ask < info_order['result']['rate']:
                            cmd = cancel_order()
                            if cmd == 1:
                                condition_print += 'clear sell order cancelled!'
                            else:
                                condition_print += 'cancel clear sell order error (O_O\')'
                    elif info_order['result']['status'] == 'cancelled':
                        temp_clear()
                        condition_print += 'sell order cancelled by user (*_*)'
                    else:
                        condition_print += 'sell litmit at '+str(info_order['result']['rate'])+', '
                        condition_print += 'wait for fill sell (clear)'
                else:
                    dbcursor.execute('select * from orders where id=?',(db_ordercount,))
                    db_last_order = dbcursor.fetchall()
                    if info_order['result']['status'] == 'filled':
                        order_history_count = len(info_order['result']['history'])
                        history_by_taker = my_history_by_taker(order_history_count)
                        order_coin_amount = 0
                        order_fee_amount = 0
                        for x in history_by_taker['result']:
                            order_coin_amount += x['amount']
                        for x in info_order['result']['history']:
                            order_fee_amount += x['fee']
                        thb_amt_pay = db_last_order[0][3]
                        thb_amt_rec = order_coin_amount*info_order['result']['rate']
                        profit_with_fee = (thb_amt_rec-thb_amt_pay)-order_fee_amount
                        dbcursor.execute('insert into sold (rate_buy,rate_sell,total_profit)values(?,?,?)',(db_last_order[0][2],info_order['result']['rate'],profit_with_fee))
                        dbcon.commit()
                        line(db_ordercount,"sell",info_order['result']['rate'],0,profit_with_fee)
                        dbcursor.execute('delete from orders where id=?',(db_ordercount,))
                        dbcon.commit()
                        condition_print += 'sell order filled'
                        temp('')
                        if db_ordercount == 1:
                            dbcursor.execute('delete from sold')
                            dbcon.commit()
                    elif info_order['result']['status'] == 'cancelled':
                        temp_clear()
                    else:
                        if ask < info_order['result']['rate']:
                            cmd = cancel_order()
                            if cmd == 1:
                                condition_print += 'sell order cancelled!'
                            else:
                                condition_print += 'cancel sell order error (O_O\')'
                        else:
                            condition_print += 'sell litmit at '+str(info_order['result']['rate'])+', '
                            condition_print += 'wait for fill sell'
        top = '#################################\n'
        top += ' BOTTAR SYY at Bitkub(Websocket)\n'
        top += '#################################'
        print('\n|\n|\n'+str(datetime.datetime.now())+'\n'+top+'\n'+db_show+'>> '+config['COIN'].upper()+' <<\n'+askbid_print+'\n\n'+'Bot Status : '+condition_print+'\n')
    except Exception as error_is:
        savelog('ข้อผิดพลาด processing : '+str(error_is))
if __name__ == "__main__":
    while True:
        try:
            dbcon = sqlite3.connect('Bitkub-SYY.db')
            dbcursor = dbcon.cursor()
            dbcursor.execute("create table if not exists orders(id integer primary key, hash text, rate float, thb_amt float, coin_amt float, fee_amt float)")
            dbcursor.execute("create table if not exists sold(id integer primary key, rate_buy float, rate_sell float, total_profit float)")
            dbcon.close()
            with open('config.json','r') as openfile:
                config = json.load(openfile)
            socket = "wss://api.bitkub.com/websocket-api/market.ticker.thb_"+config['COIN'].lower()
            connect = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close)
            connect.run_forever()
        except Exception as error_is:
            savelog('ข้อผิดพลาด core : '+str(error_is))