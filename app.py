# -*- coding: utf-8 -*-

bot_title = 'Bitkub-SYY 2.2 (Build 33) by tidLord'

# system setup
botSetup_system_delay = 3
botSetup_ts_threshold = 60 # ค่าระยะห่าง(หน่วยเป็นวินาที) ไว้เช็คเมื่อบอทหยุดทำงาน
botSetup_pid_threshold = 3 # ค่าระยะเวลาตรวจจับ last_active ป้องกันบอทรันซ้อนกัน
botSetup_orders_verbose = True # เก็บรายละเอียดออเดอร์เข้า orders_verbose.txt
botSetup_decimal_thb = 4 # จำนวนทศนิยม THB amount
botSetup_decimal_coin = 8 # จำนวนทศนิยม COIN amount

# system file name
fileName_config = 'config'
fileName_log = 'log'
fileName_orders_verbose = 'orders_verbose'
fileName_stat = 'stat'
fileName_temp = 'temp'
fileName_last_active = 'last_active'
fileName_database = 'Bitkub_SYY'

import os, json, hmac, requests, hashlib, time, sqlite3, termtables, websocket
from datetime import datetime
from numpy import format_float_positional
from pytz import timezone

# สำหรับ Windows OS
if os.name == 'nt':
    from colorama import Back, Fore, Style, init
    init()
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW(bot_title)
else:
    from colorama import Back, Fore, Style
    
# โหลด config (return -> dict / error -> 0 int)
def read_config():
    try:
        fileName_config_json = fileName_config + '.json'
        with open(fileName_config_json, 'r', encoding='utf-8') as config:
            config = json.load(config)
            if config['MAX_ORDER'] > 100:
                config['MAX_ORDER'] = 100
            return config
    except Exception as error_is:
        print('config : ' + str(error_is))
        return 0

# ฟังก์ชั่นเชื่อมต่อกับบิทคับ RESTful : Bitkub-Middleman => https://github.com/tidLord/Bitkub-Middleman
def bitkub(reqType, reqPath, reqBody, reqCredentials):
    def gen_sign(api_secret, payload_string=None):
        return hmac.new(api_secret.encode('utf-8'), payload_string.encode('utf-8'), hashlib.sha256).hexdigest()
    host = 'https://api.bitkub.com'
    ts = requests.get(host + '/api/v3/servertime').text
    url = host + reqPath
    payload = []
    payload.append(ts)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-TIMESTAMP': ts,
        'X-BTK-APIKEY': reqCredentials['apiKey']
    }
    if reqType == 'GET':
        def gen_query_param(url, query_param):
            req = requests.PreparedRequest()
            req.prepare_url(url, query_param)
            return req.url.replace(url, '')
        query_param = gen_query_param(host+reqPath, reqBody)
        payload.append('GET')
        payload.append(reqPath)
        payload.append(query_param)
        sig = gen_sign(reqCredentials['secretKey'], ''.join(payload))
        headers['X-BTK-SIGN'] = sig
        response = requests.request('GET', f'{host}{reqPath}{query_param}', headers=headers, data={}, verify=True)
        return response.json()
    if reqType == 'POST':
        payload.append('POST')
        payload.append(reqPath)
        payload.append(json.dumps(reqBody))
        sig = gen_sign(reqCredentials['secretKey'], ''.join(payload))
        headers['X-BTK-SIGN'] = sig
        response = requests.request('POST', url, headers=headers, data=json.dumps(reqBody), verify=True)
        return response.json()
    
# ฟังก์ชั่นตัดทศนิยมแบบไม่ปัดเศษ(return -> string)
def number_truncate(number, precision):
    return format_float_positional(number, unique=True, precision=precision, trim='0')

# ฟังก์ชั่นเก็บ error ใส่ log file
def log(msg):
    fileName_log_txt = fileName_log + '.txt'
    try:
        with open(fileName_log_txt, 'r', encoding='utf-8') as f:
            f = f.read()
        with open(fileName_log_txt, 'w', encoding='utf-8') as f2:
            f2.write('\n' + str(datetime.now()) + '\n' + str(msg) + '\n' + f)
    except FileNotFoundError:
        with open(fileName_log_txt, 'w', encoding='utf-8') as f:
            f.write('\n' + str(datetime.now()) + '\n'+str(msg) + '\n')
    except Exception as error_is:
        print('log() : ' + str(error_is))
        
# ฟังก์ชั่นเก็บรายละเอียดออเดอร์ ( orders verbose ) ใส่ orders verbose file
def orders_verbose(order_type, order_number, order_detail):
    if botSetup_orders_verbose == True:
        fileName_orders_verbose_txt = fileName_orders_verbose + '.txt'
        try:
            with open(fileName_orders_verbose_txt, 'r', encoding='utf-8') as f:
                f = f.read()
            with open(fileName_orders_verbose_txt, 'w', encoding='utf-8') as f2:
                f2.write('\n' + str(datetime.now()) + '\norder type : ' + order_type + '\norder number : ' + str(order_number) + '\n' + str(order_detail) + '\n............\n' + f)
        except FileNotFoundError:
            with open(fileName_orders_verbose_txt, 'w', encoding='utf-8') as f:
                f.write('\n' + str(datetime.now()) + '\norder type : ' + order_type + '\norder number : ' + str(order_number) + '\n' + str(order_detail) + '\n............\n')
        except Exception as error_is:
            print('orders_verbose() : ' + str(error_is))

# ฟังก์ชั่นเพิ่มจำนวนไม้ที่เทรดใส่ stat file
def stat_add_circle_total():
    fileName_stat_txt = fileName_stat + '.json'
    try:
        with open(fileName_stat_txt, 'r', encoding='utf-8') as stat_json:
            stat_json = json.load(stat_json)
        stat_json['circle_total'] += 1
        with open(fileName_stat_txt, 'w', encoding='utf-8') as update_stat_json:
            json.dump(stat_json, update_stat_json, indent=4)
    except FileNotFoundError:
        stat_json = { 'profit_total': 0.0, 'circle_total': 1 }
        with open(fileName_stat_txt, 'w', encoding='utf-8') as update_stat_json:
            json.dump(stat_json, update_stat_json, indent=4)
    except Exception as error_is:
        log('stat_add_circle_total() : ' + str(error_is))

# ฟังก์ชั่นเพิ่มยอดกำไรขาดทุนใส่ stat file
def stat_add_profit_total(qty):
    fileName_stat_json = fileName_stat + '.json'
    try:
        with open(fileName_stat_json, 'r', encoding='utf-8') as stat_json:
            stat_json = json.load(stat_json)
        stat_json['profit_total'] += qty
        with open(fileName_stat_json, 'w', encoding='utf-8') as update_stat_json:
            json.dump(stat_json, update_stat_json, indent=4)
    except FileNotFoundError:
        stat_json = { 'profit_total': qty, 'circle_total': 1 }
        with open(fileName_stat_json, 'w', encoding='utf-8') as update_stat_json:
            json.dump(stat_json, update_stat_json, indent=4)
    except Exception as error_is:
        log('stat_add_profit_total() : ' + str(error_is))
        
# ฟังก์ชั่นอ่าน stat file (return -> dict)
def stat_read():
    fileName_stat_json = fileName_stat + '.json'
    try:
        with open(fileName_stat_json, 'r', encoding='utf-8') as stat_json:
            stat_json = json.load(stat_json)
            return stat_json
    except FileNotFoundError:
        stat_json = { 'profit_total': 0, 'circle_total': 0 }
        with open(fileName_stat_json, 'w', encoding='utf-8') as update_stat_json:
            json.dump(stat_json, update_stat_json, indent=4)
        with open(fileName_stat_json, 'r', encoding='utf-8') as stat_json:
            stat_json = json.load(stat_json)
            return stat_json
    except Exception as error_is:
        log('stat_read() : ' + error_is)

# ฟังก์ชั่นเขียน hash ใส่ temp file (cmd 1 -> buy first, 2 -> buy DCA, 3 -> sell profit, 4 -> sell DCA, 5 -> sell clear)
def temp_write(hash, cmd, detail):
    fileName_temp_json = fileName_temp + '.json'
    try:
        with open(fileName_temp_json, 'r', encoding='utf-8') as hash_json:
            hash_json = json.load(hash_json)
        hash_json['HASH'] = hash
        hash_json['cmd'] = cmd
        hash_json['detail'] = detail
        with open(fileName_temp_json, 'w', encoding='utf-8') as update_hash_json:
            json.dump(hash_json, update_hash_json, indent=4)
    except FileNotFoundError:
        hash_json = {'HASH': hash, 'cmd': cmd, 'detail': detail}
        with open(fileName_temp_json, 'w', encoding='utf-8') as update_hash_json:
            json.dump(hash_json, update_hash_json, indent=4)
    except Exception as error_is:
        log('temp_write() : ' + str(error_is))

# ฟังก์ชั่นอ่าน temp ใน temp file (return -> dict)
def temp_read():
    fileName_temp_json = fileName_temp + '.json'
    try:
        with open(fileName_temp_json, 'r', encoding='utf-8') as hash_json:
            hash_json = json.load(hash_json)
            return hash_json
    except FileNotFoundError:
        hash_json = {'HASH': '', 'cmd': 0, 'detail': ''}
        with open(fileName_temp_json, 'w', encoding='utf-8') as update_hash_json:
            json.dump(hash_json, update_hash_json, indent=4)
        with open(fileName_temp_json, 'r', encoding='utf-8') as hash_json:
            hash_json = json.load(hash_json)
            return hash_json
    except Exception as error_is:
        log('temp_read() : ' + error_is)

    
# ฟังก์ชั่นเก็บเวลาการทำงานครั้งล่าสุดใส่ last_active file
def last_active_update(datetime_now):
    fileName_last_active_txt = fileName_last_active + '.txt'
    with open(fileName_last_active_txt, 'w', encoding='utf-8') as last_active:
        last_active.write(str(datetime_now))
        
# ฟังก์ชั่นการแจ้งเตือนใน discord ผ่าน webhook
def discord(thisOrder, notifyMsg, order_no, side, price, base_amt, profit, ordercount):
    try:
        if config['DISCORD'] == 1:
            if thisOrder == True:
                if side == 'buy':               
                    msg = '\nออเดอร์ที่ : ' + str(order_no) + '\nซื้อ : ' + config['COIN'] + '\nที่ราคา : ' + str(price) + ' บาท' + '\nจำนวน : ' + number_truncate(base_amt, botSetup_decimal_thb) + ' บาท'
                elif side == 'sell_profit':
                    if profit >= 0:
                        msg = '\nขาย : ' + config['COIN'] + '\nออเดอร์ที่ : ' + str(order_no) + '\nที่ราคา : ' + str(price) + ' บาท' + '\nกำไร : ' + number_truncate(profit, botSetup_decimal_thb) + ' บาท'
                    else:
                        msg = '\nขาย : ' + config['COIN'] + '\nออเดอร์ที่ : ' + str(order_no) + '\nที่ราคา : ' + str(price) + ' บาท' + '\nขาดทุน : ' + number_truncate(profit, botSetup_decimal_thb) + ' บาท'
                elif side == 'sell_dca':
                    if profit >= 0:
                        msg = '\nขาย : ' + config['COIN'] + '\nออเดอร์ที่ : ' + str(order_no) + '\nที่ราคา : ' + str(price) + ' บาท'
                    else:
                        msg = '\nขาย : ' + config['COIN'] + '\nออเดอร์ที่ : ' + str(order_no) + '\nที่ราคา : ' + str(price) + ' บาท'
                elif side == 'sell_clear': 
                    msg = '\nเคลียร์ออเดอร์ : ' + config['COIN'] + '\nจำนวนออเดอร์ : ' + str(ordercount) + '\nที่ราคา : ' + str(price) + ' บาท' + '\nกำไรจากการเคลียร์ : ' + number_truncate(profit, botSetup_decimal_thb)+' บาท'
            else:
                msg = notifyMsg

            data = {
                "content" : msg,
                "username" : "Bitkub-SYY by tidLord",
                "avatar_url" : "https://i.ibb.co/fvcJgbK/076753456789.jpg"
            }
            result = requests.post(config['DISCORD_WEBHOOK_URL'], json = data)
            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as error_is:
                log('discord send error : '+str(error_is))
                print('!!! discord send error !!!')
    except Exception as error_is:
        log('discord function error : '+str(error_is))
        print('!!! discord function error !!!')

# ฟังก์ชั่นเทรด
def buy(credentials, ask, ordersize, cmd): # cmd 1 -> buy first order, 2 -> buy DCA
    reqBody = {
        'sym': config['COIN'].lower() + '_thb',
        'amt': ordersize,
        'rat': ask,
        'typ': 'limit'
    }
    cmd_send = bitkub('POST', '/api/v3/market/place-bid', reqBody, credentials)

    if cmd_send['error'] != 0:
        print('buy() : Bitkub error code = ' + str(cmd_send['error']))
        time.sleep(botSetup_system_delay)
        return 0
    else:
        temp_write(cmd_send['result']['id'], cmd, cmd_send)
        return 1

def sell(credentials, bid, ordersize, cmd): # cmd 3 -> sell profit, 4 -> sell dca, 5 -> sell clear
    reqBody = {
        'sym': config['COIN'].lower() + '_thb',
        'amt': ordersize,
        'rat': bid,
        'typ': 'limit'
    }   
    cmd_send = bitkub('POST', '/api/v3/market/place-ask', reqBody, credentials)
    
    if cmd_send['error'] != 0:
        print('sell() : Bitkub error code = ' + str(cmd_send['error']))
        time.sleep(botSetup_system_delay)
        return 0
    else:
        temp_write(cmd_send['result']['id'], cmd, cmd_send)
        return 1

# ฟังก์ชั่นโชว์ข้อความบน console ในกรณี skip การส่งคำสั่ง
def show_skip_text():
    print('> Skip for safe filling')

#########################
### $$$ Websocket $$$ ###
#########################
pid_signature = None # pid signature ป้องกันการรันบอทซ้อนกัน

def on_close(connect):
    print('Websocket : closed')
def on_message(connect, message):
    global pid_signature
    try:
        # config
        config = read_config()
        if config == 0:
            time.sleep(botSetup_system_delay)
            return
        
        # credentials สำหรับ bitkub()
        credentials = {
            'apiKey': config['KEY'],
            'secretKey': config['SECRET']
        }
        
        # datetime สำหรับ loop บอท
        datetime_now = datetime_now = datetime.now(timezone('Asia/Bangkok')).replace(tzinfo=None)
        
        ###############################
        # *** ป้องกันการรันบอทซ้อนกัน *** #
        ###############################
        try:
            fileName_last_active_txt = fileName_last_active + '.txt'
            with open(fileName_last_active_txt, 'r', encoding='utf-8') as read_last_active_txt:
                read_last_active_txt = read_last_active_txt.read()
                if read_last_active_txt == '':
                    last_active_update(datetime_now)
                    time.sleep(botSetup_pid_threshold)
                    return
                else:
                    ts_last_active_txt = datetime.strptime(read_last_active_txt, '%Y-%m-%d %H:%M:%S.%f').timestamp()
        except FileNotFoundError:
            last_active_update(datetime_now)
            ts_last_active_txt = 0
            time.sleep(botSetup_pid_threshold)
        except:
            ts_last_active_txt = 0

        if pid_signature == None:
            pid_signature = datetime_now.timestamp()
            
        try:
            with open('BOT_PID_FILE', 'r', encoding='utf-8') as pid_file:
                pid_file = float(pid_file.read())
        except FileNotFoundError:
            with open('BOT_PID_FILE', 'w', encoding='utf-8') as pid_file:
                pid_file = pid_file.write(str(pid_signature))
            with open('BOT_PID_FILE', 'r', encoding='utf-8') as pid_file:
                pid_file = float(pid_file.read())

        if pid_signature != pid_file:
            if ts_last_active_txt == 0:
                return
            elif pid_signature - float(ts_last_active_txt) > botSetup_pid_threshold:
                with open('BOT_PID_FILE', 'w', encoding='utf-8') as pid_file:
                    pid_file = pid_file.write(str(pid_signature))
                    return
            else:
                pid_signature = datetime.today().timestamp()
                print('!!! Running bots repeatedly is not allowed. Please Wait... !!!')
                time.sleep(botSetup_pid_threshold)
                return
        last_active_update(datetime_now)
        ###############################
        
        ###############################
        # *** แจ้งเตือนบอทหยุดทำงาน *** #
        ###############################
        try:
            if config['DISCORD'] == 1 and ts_last_active_txt != 0:
                ts_now = datetime_now.timestamp()
                #threshold ถ้าเวลาใน last_active file ต่างกับเวลาปัจจุบันเกินค่าที่ตั้งไว้
                if ts_now - ts_last_active_txt > botSetup_ts_threshold:
                    str_last_active_txt = datetime.fromtimestamp(ts_last_active_txt).strftime('%d/%m/%y %H:%M:%S')
                    str_time_now = datetime.fromtimestamp(ts_now).strftime('%d/%m/%y %H:%M:%S')
                    # ส่งแจ้งเตือน               
                    msg = '\nบอทหยุดทำงาน\nเมื่อ : ' + str_last_active_txt + '\nกลับมาทำงานเมื่อ : ' + str_time_now
                    discord(False, msg, None, None, None, None, None, None)
        except Exception as error_is:
            print('check_bot_stop : '+str(error_is))
            log('check_bot_stop : '+str(error_is))
            time.sleep(botSetup_system_delay)
            return
        ###############################
        
        ##############################
        # *** ระบบฐานข้อมูลของบอท *** #
        ##############################
        try:
            dbcon = sqlite3.connect(fileName_database +'.db')
            dbcursor = dbcon.cursor()
            dbcursor.execute('create table if not exists orders(id integer primary key, rate real, base_amt real, coin_amt real, fee_amt real, pricerange integer, ts integer)')
            dbcursor.execute('create table if not exists sold(id integer primary key, total_profit real)')
        except Exception as error_is:
            log('database : ' + str(error_is))
            print('database : ' + str(error_is))
            time.sleep(botSetup_system_delay)
            return
        ##############################

        # ฟังก์ชั่นเรียกดูจำนวนออเดอร์ เพราะมีการเรียกหลายรอบใน operate()
        def fetch_db_ordercount():
            dbcursor.execute('select * from orders')
            db_res = dbcursor.fetchall()
            return len(db_res)
        db_ordercount = fetch_db_ordercount()
        try:
            if db_ordercount > 0:
                dbcursor.execute('select ts from orders where id=(select min(id) from orders)')
                db_res = dbcursor.fetchone()
                db_firstorder_ts = db_res[0] # timestamp ออเดอร์แรก
                dbcursor.execute('select rate from orders where id=(select max(id) from orders)')
                db_res = dbcursor.fetchone()
                db_lastorder_price = db_res[0] # เรทของออเดอร์ล่าสุด(ราคาที่ต่ำที่สุด)
                dbcursor.execute('select coin_amt from orders where id=(select max(id) from orders)')
                db_res = dbcursor.fetchone()
                db_lastorder_coin_amt = db_res[0] # จำนวนโทเคนของออเดอร์ล่าสุด
                dbcursor.execute('select base_amt from orders where id=(select max(id) from orders)')
                db_res = dbcursor.fetchone()
                db_lastorder_base_amt = db_res[0] # จำนวน base ของออเดอร์ล่าสุด
                dbcursor.execute('select max(pricerange) from orders')
                db_res = dbcursor.fetchone()
                db_pricerange = db_res[0] # pricerange จากออเดอร์แรก
                dbcursor.execute('select base_amt from orders where id=(select min(id) from orders)')
                db_res = dbcursor.fetchone()
                db_firstorder_cost = db_res[0] # cost ออเดอร์แรก
                dbcursor.execute('select sum(base_amt) from orders')
                db_res = dbcursor.fetchone()
                db_total_base = db_res[0] # ผลรวม total base
                dbcursor.execute('select sum(coin_amt) from orders')
                db_res = dbcursor.fetchone()
                db_total_coin = db_res[0] #ผลรวม total coin
                dbcursor.execute('select sum(fee_amt) from orders')
                db_res = dbcursor.fetchone()
                db_total_fee = db_res[0] # ผลรวม total fee
                dbcursor.execute('select sum(total_profit) from sold')
                db_res = dbcursor.fetchone()
                db_sold_total_profit = db_res[0] # ผลรวม total profit จาก sold
                if db_sold_total_profit == None:
                    db_sold_total_profit = 0
                if db_ordercount > 1:
                    dbcursor.execute('select rate from orders where id=(select max(?) from orders)',(db_ordercount - 1,))
                    db_res = dbcursor.fetchone()
                    db_dca_sell_price = db_res[0] # เรทของออเดอร์รองล่าสุด
                else:
                    db_dca_sell_price = 0
            else:
                db_firstorder_ts = 0
                db_lastorder_price = 0
                db_lastorder_coin_amt = 0
                db_lastorder_base_amt = 0
                db_pricerange = 0
                db_firstorder_cost = 0
                db_total_base = 0
                db_total_coin = 0
                db_total_fee = 0
                db_sold_total_profit = 0
                db_dca_sell_price = 0
        except Exception as error_is:
            log('database orders : ' + str(error_is))
            print('database orders : ' + str(error_is))
            return

        # Break-even
        if db_ordercount > 0:
            break_even = (((((db_total_fee / db_total_base) * 100) * 2) / 100) * ((db_total_base - db_sold_total_profit) / db_total_coin)) + ((db_total_base - db_sold_total_profit) / db_total_coin)
        else:
            break_even = None

        # Ask, Bid
        try:
            msg = json.loads(message)
            ask = msg['lowestAsk']
            ask_size_coin = msg['lowestAskSize']
            ask_size_thb = ask_size_coin * ask
            bid = msg['highestBid']
            bid_size_coin = msg['highestBidSize']
        except Exception as error:
            return
        
        # circle period
        try:
            if db_firstorder_ts != 0:
                date_time_first_order = datetime.fromtimestamp(db_firstorder_ts)
                current_timestamp = datetime.timestamp(datetime_now)
                date_time_current = datetime.fromtimestamp(current_timestamp)
                time_diff = date_time_current - date_time_first_order
                years = time_diff.days // 365
                if years > 0:
                    months = time_diff.days % 365 // 30
                else:
                    months = (time_diff.days % 365 // 30) if (time_diff.days % 365 // 30) > 0 else 0
                days = time_diff.days % 365 % 30
                hours = time_diff.seconds // 3600
                minutes = (time_diff.seconds % 3600) // 60
                seconds = time_diff.seconds % 60
                time_components = []
                if years > 0:
                    time_components.append(f'{years} years')
                if months > 0:
                    time_components.append(f'{months} months')
                if days > 0:
                    time_components.append(f'{days} days')
                if hours > 0:
                    time_components.append(f'{hours} hours')
                if minutes > 0:
                    time_components.append(f'{minutes} minutes')
                if seconds > 0:
                    time_components.append(f'{seconds} seconds')
                time_diff_str = ', '.join(time_components)
                circle_period = time_diff_str
            else:
                circle_period = None
        except Exception as error_is:
            log('circle_period : ' + str(error_is))
            print('circle_period : ' + str(error_is))
            return
        
            
        def order_operate():
            temp = temp_read()
            # เพิ่มเงื่อนไข Check OrderSide ()
            if temp_read()['cmd'] == 1 or temp_read()['cmd'] == 2:
                sd = 'buy'
            else:
                sd = 'sell'
            
            if temp['HASH'] == '':
                return 0
            else:
                reqBody = {
                    'sym': config['COIN'].lower() + '_thb',
                    'id': temp['HASH'],
                    'sd': sd
                }
                order_info = bitkub('GET', '/api/v3/market/order-info', reqBody, credentials)['result']
                
                print('Order ' + temp['HASH'] + ' Filling')
                while order_info['status'] not in ['filled', 'cancelled']:
                    order_info = bitkub('GET', '/api/v3/market/order-info', reqBody, credentials)['result']
                
                if order_info['status'] == 'cancelled':
                    temp_write('', 0, '')
                    return 1
                
                if temp['cmd'] == 1:
                    pricerange = ask / config['MAX_ORDER'] # คำนวณ pricerage
                    temp_for_order = temp_read()['detail']['result']
                    dbcursor.execute('insert into orders (rate, base_amt, coin_amt, fee_amt, pricerange, ts)values(?, ?, ?, ?, ?, ?)',(temp_for_order['rat'], temp_for_order['amt'], temp_for_order['rec'], temp_for_order['fee'], pricerange, temp_for_order['ts']))
                    dbcon.commit()
                    print(f'-- BUY first order filled ({temp["HASH"]}) --')
                    temp_write('', 0, '')
                    db_ordercount = fetch_db_ordercount()
                    print(f'> OrderCount ({db_ordercount}/{config["MAX_ORDER"]})')
                    stat_add_circle_total()
                    orders_verbose('buy', db_ordercount, order_info)
                    discord(True, None, db_ordercount, 'buy', order_info['rate'], temp_for_order['amt'], 0, 0)
                elif temp['cmd'] == 2:
                    temp_for_order = temp_read()['detail']['result']
                    dbcursor.execute('insert into orders (rate, base_amt, coin_amt, fee_amt, pricerange, ts)values(?, ?, ?, ?, ?, ?)',(temp_for_order['rat'], temp_for_order['amt'], temp_for_order['rec'], temp_for_order['fee'], 0, temp_for_order['ts']))
                    dbcon.commit()
                    print(f'-- BUY DCA order filled ({temp["HASH"]}) --')
                    temp_write('', 0, '')
                    db_ordercount = fetch_db_ordercount()
                    print(f'> OrderCount ({db_ordercount}/{config["MAX_ORDER"]})')
                    orders_verbose('buy DCA', db_ordercount, order_info)
                    discord(True, None, db_ordercount, 'buy', order_info['rate'], temp_for_order['amt'], 0, 0)
                elif temp['cmd'] == 3:
                    temp_for_order = temp_read()['detail']['result']
                    order_profit = (temp_for_order['rec'] + db_sold_total_profit) - db_total_base
                    db_ordercount = fetch_db_ordercount()
                    dbcursor.execute('delete from sold')
                    dbcursor.execute('delete from orders')
                    dbcon.commit()
                    print(f'-- SELL order filled ({temp["HASH"]}) --')
                    temp_write('', 0, '')
                    db_ordercount = fetch_db_ordercount()
                    stat_add_profit_total(order_profit)
                    # ในกรณีมีการขาย dca แต่ไม่เข้าเงื่อนไข sell clear(5) ที่ต้องมีหลายออเดอร์ จะถือว่าเป็น sell clear profit
                    if db_sold_total_profit == 0:
                        sell_type = 'sell profit'
                    else:
                        sell_type = 'sell clear profit'
                    orders_verbose(sell_type, db_ordercount + 1, order_info)
                    discord(True, None, db_ordercount + 1, 'sell_profit', order_info['rate'], 0, order_profit, 0)
                elif temp['cmd'] == 4:
                    temp_for_order = temp_read()['detail']['result']
                    order_profit = temp_for_order['rec'] - db_lastorder_base_amt
                    db_ordercount = fetch_db_ordercount()
                    dbcursor.execute('delete from orders where id=?',(db_ordercount,))
                    dbcursor.execute('insert into sold (total_profit)values(?)',(order_profit,))
                    dbcon.commit()
                    print(f'-- SELL DCA order filled ({temp["HASH"]}) --')
                    temp_write('', 0, '')
                    db_ordercount = fetch_db_ordercount()
                    print(f'> OrderCount ({db_ordercount}/{config["MAX_ORDER"]})')
                    orders_verbose('sell dca', db_ordercount + 1, order_info)
                    discord(True, None, db_ordercount + 1, 'sell_dca', order_info['rate'], 0, 0, 0)
                elif temp['cmd'] == 5:
                    temp_for_order = temp_read()['detail']['result']
                    order_profit = (temp_for_order['rec'] + db_sold_total_profit) - db_total_base
                    db_ordercount = fetch_db_ordercount()
                    dbcursor.execute('delete from sold')
                    dbcursor.execute('delete from orders')
                    dbcon.commit()
                    print(f'-- SELL Clear order filled ({temp["HASH"]}) --')
                    temp_write('', 0, '')
                    stat_add_profit_total(order_profit)
                    orders_verbose('sell clear', db_ordercount, order_info)
                    discord(True, None, 0, 'sell_clear', order_info['rate'], 0, order_profit, db_ordercount)
                return 1
                
        # $$$$$$$$$$$$$$$$$$$$$$$ #
        # $$$$$$ Condition $$$$$$ #
        # $$$$$$$$$$$$$$$$$$$$$$$ #
        
        # เช็คว่ามี hash ค้างไหม ถ้ามีแล้วถูก operate ให้ return
        if order_operate() == 1:
            return

        if db_ordercount < 1: # ถ้าไม่มีออเดอร์ในหน้าตัก
            # เช็คว่า config อนุญาตไหม (stopnextcircle = 0 หรือเปล่า)
            if config['STOPNEXTCIRCLE'] != 0:
                print('STOPNEXTCIRCLE != 0')
                return
            # คำนวณ order size
            try:
                if config['ALL_IN'] == 0:
                    ordersize = config['ORDER_SIZE']
                else:
                    reqBody = {
                    }
                    balances = bitkub('POST', '/api/v3/market/balances', reqBody, credentials)['result']
                    balance_thb = balances['THB']['available']
                    ordersize = balance_thb / config['MAX_ORDER']
            except Exception as error_is:
                log('ordersize cal : ' + str(error_is))
                print('ordersize cal : ' + str(error_is))
                return
            # ส่งคำสั่งซื้อออเดอร์แรก ถ้าส่งคำสั่งสำเร็จให้ return
            if ask_size_thb > ordersize:
                if buy(credentials, ask, ordersize, 1) == 1:
                    return
            else:
                show_skip_text()
                return
        else: # ถ้ามีออเดอร์ในหน้าตัก
            if ask < db_lastorder_price - db_pricerange: # buy dca
                if db_ordercount < config['MAX_ORDER']:
                    if ask_size_thb > db_firstorder_cost:
                        if buy(credentials, ask, db_firstorder_cost, 2) == 1:
                            return
                    else:
                        show_skip_text()
                        return
            if db_ordercount == 1: # ถ้ามีแค่ 1 ออเดอร์
                if bid > db_lastorder_price + db_pricerange: # sell profit
                    if bid_size_coin > db_total_coin:
                        if sell(credentials, bid, db_total_coin, 3) == 1:
                            return
                    else:
                        show_skip_text()
                        return
            else: # ถ้ามี 2 ออเดอร์ขึ้นไป
                if bid >= break_even: # sell clear
                    if bid_size_coin > db_total_coin:
                        if sell(credentials, bid, db_total_coin, 5) == 1:
                            return
                        else:
                            show_skip_text()
                            return
                elif bid >= db_dca_sell_price: # sell dca
                    if bid_size_coin > db_lastorder_coin_amt:
                        if sell(credentials, bid, db_lastorder_coin_amt, 4) == 1:
                            return
                    else:
                        show_skip_text()
                        return
            
        #$$$$$$$$$$$$$$$$$$$$$$$$$$
        #   โชว์สถิติและข้อมูลออเดอร์   #
        #$$$$$$$$$$$$$$$$$$$$$$$$$$
        
        # price table
        header = [' Symbol ', Back.RED + Fore.WHITE + Style.BRIGHT + ' Ask ' + Style.RESET_ALL, Back.GREEN + Fore.WHITE + Style.BRIGHT + ' Bid ' + Style.RESET_ALL, Back.YELLOW + Style.BRIGHT + ' Break-Even ' + Style.RESET_ALL + Style.RESET_ALL, ' Price Range ']

        # distance last order price
        if bid > db_lastorder_price:
            distance_lastorder = ((bid - db_lastorder_price) / db_lastorder_price) * 100
            distance_lastorder = Style.BRIGHT + 'DistanceLastOrder' + Style.RESET_ALL + ' : ' + number_truncate(distance_lastorder, 4) + ' % ( ' + number_truncate(bid - db_lastorder_price, botSetup_decimal_coin) + ' ฿ )\n'
        elif bid < db_lastorder_price:
            distance_lastorder = ((db_lastorder_price - ask) / db_lastorder_price) * 100
            distance_lastorder = Style.BRIGHT + 'DistanceLastOrder' + Style.RESET_ALL + ' : ' + number_truncate(distance_lastorder * -1, 4) + ' % ( ' + number_truncate((db_lastorder_price - ask) * -1, botSetup_decimal_coin) + ' ฿ )\n'
        else:
            distance_lastorder = ''

        # price range show
        pricerange_show = db_pricerange

        pricerange_show = number_truncate(pricerange_show, botSetup_decimal_coin)

        data = [[config['COIN'] + '/THB', str(ask) + ' ฿', str(bid) + ' ฿', number_truncate(break_even, botSetup_decimal_coin) + ' ฿', pricerange_show + ' ฿']]
        price_table_show = termtables.to_string(
            data,
            header=header,
            style=termtables.styles.rounded_thick
        )
        # orders table
        dbcursor.execute('select * from orders')
        db_res = dbcursor.fetchall()
        
        #ordercount for show
        if db_ordercount < config['MAX_ORDER']:
            order_table_order_count = Style.BRIGHT + 'OrderCount' + Style.RESET_ALL + ' : ' + str(len(db_res)) + '/' + str(config['MAX_ORDER'])
        else:
            order_table_order_count = Style.BRIGHT + 'OrderCount' + Style.RESET_ALL + ' : ' + Back.RED + Fore.WHITE + Style.BRIGHT + ' ' + str(len(db_res)) + '/' + str(config['MAX_ORDER']) + ' ' + Style.RESET_ALL
            
        order_table_circle_period = Style.BRIGHT + 'Circle Period' + Style.RESET_ALL + ' : ' + circle_period

        header = [Back.WHITE + Fore.BLACK + Style.BRIGHT + ' No. ' + Style.RESET_ALL, Back.WHITE + Fore.BLACK + Style.BRIGHT + ' Rate ' + Style.RESET_ALL, Back.WHITE + Fore.BLACK + Style.BRIGHT + ' Cost ' + Style.RESET_ALL, Back.WHITE + Fore.BLACK + Style.BRIGHT + ' Amount ' + Style.RESET_ALL, Back.WHITE + Fore.BLACK + Style.BRIGHT + ' Fee ' + Style.RESET_ALL]
        data = []
        for row in db_res:
            data.append((row[0], str(row[1]) + ' ฿', number_truncate(row[2], botSetup_decimal_thb) + ' ฿', number_truncate(row[3], botSetup_decimal_coin), str(row[4]) + ' ฿'))

        orders_table_show = termtables.to_string(
            data,
            header=header,
            style=termtables.styles.rounded_thick
        )

        header = []
        stats = stat_read()
        if stats['profit_total'] == 0:
            header.append(Back.BLUE+Fore.WHITE + Style.BRIGHT + ' Profit Total ' + Style.RESET_ALL)
        elif stats['profit_total']>0:
            header.append(Back.GREEN+Fore.WHITE + Style.BRIGHT + ' Profit Total ' + Style.RESET_ALL)
        else:
            header.append(Back.RED + Fore.WHITE + Style.BRIGHT + ' Profit Total ' + Style.RESET_ALL)
        header.append(Back.MAGENTA + Fore.WHITE + Style.BRIGHT + ' Circle Total ' + Style.RESET_ALL)

        # check profit total
        if stats['profit_total'] == 0:
            profit_total_show = str(0.0) + ' ฿'
        else:
            profit_total_show = number_truncate(stats['profit_total'], botSetup_decimal_thb) + ' ฿'
            
        data = [[profit_total_show, stats['circle_total']]]
        stats_table_show = termtables.to_string(
            data,
            header=header,
            style=termtables.styles.rounded_thick
        )

        top = '|' + '\n' + '|' + '\n' + '|' + '\n' + '|' + '\n' + '|' + '\n' + '|' + '\n'  
        top += '▀█▀ █ █▀▄ █░░ █▀█ █▀█ █▀▄\n'
        top += '░█░ █ █▄▀ █▄▄ █▄█ █▀▄ █▄▀'
        top += '\n' + Style.BRIGHT + bot_title + Style.RESET_ALL + '\n'
        loop_time = str(datetime_now.strftime('%Y-%m-%d %H:%M:%S'))
        top += '# ' + loop_time + '\n'
        print(top + price_table_show + '\n' + distance_lastorder + order_table_order_count + '\n' + order_table_circle_period + '\n' + orders_table_show + '\n'+stats_table_show + '\n')
        #$$$$$$$$$$$$$$$$$$$$$$$$$$ 
            
    except Exception as error:
        print('Websocket : ' + str(error))
    
if __name__ == '__main__':
    while True:
        try:
            config = read_config()
            if config == 0:
                time.sleep(botSetup_system_delay)
                continue

            credentials = {
                'apiKey': '',
                'secretKey': ''
            }
            bitkub_symbols = bitkub('GET', '/api/market/symbols', {}, credentials)
            found = any(item['symbol'] == 'THB_' + config['COIN'].upper() for item in bitkub_symbols['result'])
            if found:
                socket = 'wss://api.bitkub.com/websocket-api/market.ticker.thb_' + config['COIN'].lower()
                connect = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close)
                connect.run_forever()
            else:
                print('!!! ' + config['COIN'].upper() + ' was not found in Bitkub !!!')
                time.sleep(botSetup_system_delay)
        except Exception as error:
            print('Core : ' + str(error))
            time.sleep(botSetup_system_delay)
