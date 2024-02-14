# Bitkub-SYY 2.0
บอทเทรดสำหรับกระดานเทรดบิทคับ กลยุทธ์ซอยยิกยิก รับข้อมูลราคาสำหรับการคำนวณเพื่อซื้อขายจากเซิร์ฟเวอร์ของบิทคับผ่าน websocket และการส่งคำสั่งซื้อขายแบบ limit order ทำให้บอททำงานด้วยข้อมูลที่ realtime และส่งคำสั่งซื้อขายได้อย่างแม่นยำ

## กลยุทธ์ซอยยิกยิก
มีพื้นฐานมาจากระบบ grid  ในกรณีที่ราคาร่วงลงต่ำกว่าจุดที่เข้าซื้อ จะใช้วิธีการสะสมออเดอร์(DCA) แก้ทางตลาด และมีการประยุกต์ทำให้ออเดอร์ที่ซื้อสะสมสามารถซื้อขายทำกำไรเพื่อดึงจุดคุ้มทุนให้ต่ำลงได้
![](https://user-images.githubusercontent.com/96503948/183243023-dfa9ea3b-79a9-484e-a084-b195729b1f75.png)
**สิ่งที่ต้องรู้**

 1. PRICERANGE คือ ระยะห่างราคาของแต่ละออเดอร์(grid) ถ้าตามรูปด้านบนก็คือเส้นตารางสีฟ้า
 2. Break-even คือ จุดคุ้มทุน ที่จะสามารถขายทุกออเดอร์ได้แบบไม่ขาดทุน
 3. Circle คือ รอบการเทรด โดยจะนับจากออเดอร์ที่ 1 เสมอ  ดังตัวอย่างในรูปด้านบน มีการเริ่มนับออเดอร์ที่ 1 จำนวนสองครั้ง ก็หมายถึงว่ามีการเทรด 2 circle

**เงื่อนไขของบอทมีดังนี้**
- ในกรณีที่ไม่มีออเดอร์ บอทจะทำการซื้อทันที โดยไม่สนใจแนวโน้มตลาดใดๆ
- ในกรณีที่มีออเดอร์ในหน้าตักแค่ 1 ออเดอร์ และราคาพุ่งขึ้นถึงระยะราคาที่กำหนด(PRICERANGE) บอทจะทำการขายเอากำไรทันที
- ถ้าหากราคาร่วงลงต่ำกว่าระยะราคาที่กำหนด(PRICERANGE) บอทจะทำการซื้อเพิ่ม(DCA)
- ถ้าหากมีออเดอร์ในหน้าตักมากกว่า 1 ออเดอร์ และราคาพุ่งขึ้นถึงราคาออเดอร์ก่อนหน้า บอทจะทำการขายเพื่อเก็บกำไร ซึ่งการขายเพื่อเก็บกำไรนี้จะทำให้จุดคุ้มทุนต่ำลงมาเรื่อยๆ
- ถ้าหากมีออเดอร์ในหน้าตักตั้งแต่ 2 ออเดอร์ขึ้นไป และราคาพุ่งขึ้นถึงจุดคุ้มทุน บอทจะทำการขายทุกออเดอร์ทันที

ดังนั้นไม่ว่าสภาวะตลาดจะเป็นตลาดกระทิง ตลาดหมี หรืออยู่ในสภาวะ sideway กลยุทธ์ซอยยิกยิกจะสามารถซื้อขายและทำกำไรได้ในทุกสภาวะตลาด
 
## หน้า console
![](https://github.com/tidLord/Bitkub-SYY/assets/96503948/f945a747-ae49-485a-b361-85fe13843062)
  
บอทจะทำงานในลักษณะ loop โดยแต่ละ loop จะมีข้อมูลดังนี้

- วันเวลาของ loop นั้นๆ
- ชื่อบอท และ Build version
- เหรียญที่เทรด, Ask, Bid, จุดคุ้มทุน, PRICERANGE
- DistanceLastOrder คือ ระยะห่างของราคาปัจจุบันกับออเดอร์ที่ซื้อล่าสุด โดยหน่วยจะเป็นเปอร์เซ็นต์ ส่วนในวงเล็บจะเป็นหน่วยราคา(บาท)
- OrderCount จะเป็นจำนวนออเดอร์ปัจจุบันกับจำนวนออเดอร์สูงสุดที่อนุญาตให้บอทเทรด
- CirclePeriod คือ ระยะเวลานับตั้งแต่การซื้อออเดอร์แรกของ circle ปัจจุบัน
- ในกรณีที่มีออเดอร์ในหน้าตักก็จะโชว์ข้อมูลออเดอร์ ลำดับ, ราคาที่ซื้อ, ขนาดออเดอร์, จำนวนเหรียญที่ได้, ค่าธรรมเนียม
- สถิติการเทรด จะมีกำไรที่หักค่าธรรมเนียมแล้วและจำนวน circle

ถ้าบอทมีการดำเนินการต่างๆ เช่น การซื้อขาย การส่งคำสั่ง บอทจะโชว์สถานะบนหน้า console นี้เช่นกัน

## LINE Notify
ถ้าตั้งค่าและเปิดใช้งาน บอทจะส่งไลน์แจ้งเตือนข้อมูลที่สำคัญๆทุกการซื้อขาย รวมถึงแจ้งเตือนระยะเวลาที่บอทได้หยุดการทำงานจนถึงตอนที่บอทได้เริ่มทำงานอีกครั้ง(สำหรับคนที่บ้านไฟดับบ่อยๆ อินเตอร์เน็ตหลุดบ่อยๆ น่าจะเป็นประโยชน์ครับ)
![](https://github.com/tidLord/Bitkub-SYY/assets/96503948/1df526f3-1e18-464d-8b5b-7070295f5f8b)


## ไฟล์ต่างๆของบอท

ไฟล์เริ่มต้น
-  **app.py** ไฟล์ python ไฟล์หลักของบอท(ถ้าใช้ executable จะเป็น .exe)
-  **config.json** ไฟล์ config

ไฟล์ที่หลังจากรันบอทแล้วจะถูกสร้างขึ้นมาโดยอัตโนมัติ(ไฟล์ระบบ)
-  **Bitkub-SYY.db** ไฟล์ฐานข้อมูลของบอท
-  **state.json** ไฟล์เก็บข้อมูลสถิติการเทรด
-  **temp.json** ไฟล์เก็บข้อมูลชั่วคราวของบอท
-  **last_active.txt** ไฟล์ text เก็บข้อมูลวันเวลาที่บอททำงานครั้งล่าสุด
- **order_verbose.txt** ไฟล์เก็บข้อมูลออเดอร์ที่บอททำการซื้อขายอย่างละเอียด
-  **BOT_PID_FILE** ไฟล์เก็บข้อมูล signature ของบอท
-  **log.txt** ไฟล์ text บอกรายละเอียดการทำงานในทางเทคนิคของบอท รวมถึงข้อผิดพลาดต่างๆ (จะถูกสร้างขึ้นมาอัตโนมัติเมื่อมีเหตุการณ์สำคัญเกิดขึ้น) สามารถลบทิ้งได้แม้ในขณะที่บอททำงานอยู่ ไม่มีผลกับการทำงานของบอท
  
## config.json

ในไฟล์ config จะมี parameter ต่างๆดังนี้

-  **KEY** คือ API Key ที่ได้จากบิทคับ
-  **SECRET** คือ Secret Key ที่ได้จากบิทคับ
-  **LINETOKEN** คือ token ที่ได้จาก LINE Notify
-  **LINE** คือ เปิดหรือปิดใช้งาน LINE Notify (1=เปิด, 0=ปิด)
-  **COIN** คือ เหรียญหรือโทเคนที่จะเทรด เช่น KUB, ETH, DOGE เป็นต้น
-  **ALL_IN** คือ การลงทุนโดยใช้เงินบาทที่มีอยู่ทั้งหมดในบัญชี (1=เปิด, 0=ปิด)
-  **ORDER_SIZE** คือ ปริมาณที่จะซื้อแต่ละออเดอร์ มีหน่วยเป็นบาท
-  **MAX_ORDER** คือ จำนวนออเดอร์สูงสุดที่จะให้บอทสะสม ถ้าหากบอทซื้อสะสมและมีออเดอร์จำนวนเท่ากับค่านี้ บอทจะไม่ทำการซื้อออเดอร์ใหม่เพิ่ม  (ตั้งได้สูงสุด 100  ไม่อนุญาตให้เกินนี้ ถึงจะตั้งมาเกิน ระบบก็จะปรับให้เป็น 100)
-  **STOPNEXTCIRCLE** คือ หยุดบอทในการเปิดออเดอร์ใหม่ในกรณีที่ไม่มีออเดอร์ในหน้าตัก แต่ถ้าหากมีออเดอร์อยู่ในหน้าตัก บอทจะยังทำการซื้อขายจนกว่าออเดอร์จะหมดหน้าตัก (1=หยุด, 0=ไม่หยุด)

ALL_IN จะทำงานประสานกันกับ ORDER_SIZE  ถ้าเราปิด ALL_IN  ขนาดออเดอร์ที่จะเทรดจะถูกใช้ตาม ORDER_SIZE  แต่ถ้าเราเปิด ALL_IN ขนาดออเดอร์จะถูกคำนวณโดย MAX_ORDER และยอดเงินบาทในบัญชีเราทั้งหมด และ ORDER_SIZE จะไม่ถูกใช้งาน ไม่ว่าเราจะตั้งค่าเป็นจำนวนเท่าใดก็ตาม

> ยอดเงินในบัญชีทั้งหมด / MAX_ORDER

เช่น ยอดเงินในบัญชีเรามี 3,000 บาท เราตั้ง MAX_ORDER ไว้ที่ 100
3,000 / 100 = 30
หมายความว่าแต่ละออเดอร์จะมีขนาด 30 บาท

** ในกรณีที่เปิดใช้ ALL_IN กรุณาคำนวณด้วยตัวเองก่อนตั้งค่าให้บอท ป้องกันขนาดไม่ถึงขั้นต่ำที่บิทคับกำหนด

ประโยชน์ของ ALL_IN คือ เมื่อจบ circle ได้กำไร ขนาดออเดอร์เราจะสามารถเพิ่มขึ้นได้เรื่อยๆไม่ตายตัวเหมือนกับการปิด ALL_IN แล้วตั้งค่า ORDER_SIZE   เพราะบอทจะทำการเอาจำนวนเงินบาทในบัญชีทั้งหมดมาหารด้วย MAX_ORDER ให้เราก่อนเริ่ม circle เสมอ

**ขนาดของออเดอร์ DCA หรือออเดอร์สะสม จะมีขนาดเท่ากับออเดอร์ที่ 1 เสมอ**

## ความเสี่ยงและความอยู่ยงคงกระพัน
กลยุทธ์ซอยยิกยิก เป็นกลยุทธ์ที่ใช้กลไกราคาในการเอาตัวรอดในตลาด ยิ่งราคาขยับขึ้นๆลงๆบ่อยๆ โอกาสในการทำกำไรของกุลยุทธ์นี้ก็จะยิ่งมาก ขอเพียงแค่ราคามีการขยับ ซึ่งกลยุทธ์ลักษณะนี้จะไม่สามารถเอา backtest มาอ้างอิงหรือเพื่อวิเคราะห์แนวโน้มใดๆได้ เพราะมันไม่ได้พึ่งอัตราการชนะ(win rate)  แค่เริ่มต้นรันบอทและเริ่มต้น circle ต่างเวลาต่างราคากัน ผลลัพธ์ที่ได้ก็แตกต่างกันอย่างสิ้นเชิง

ส่วนตัวแนะนำให้ใช้ MAX_ORDER 100 ออเดอร์ จะได้ PRICERANGE ที่ไม่กว้างและไม่แคบเกินไป สาเหตุที่ต้องกำหนดให้ MAX_ORDER สูงสุดได้แค่ 100 เพราะถ้าเกินนี้จะทำให้ PRICERANGE แคบเกินไป เราอาจจะขาดทุนเพราะค่าธรรมเนียมได้

ถ้าเราตั้ง MAX_ORDER เป็น 100  เวลาบอทเริ่ม circle บอทจะเอาราคาปัจจุบันหารด้วย 100  นั่นหมายความว่า เช่น เราเทรดบิทคอยน์ ต่อให้ราคาบิทคอยน์จะร่วงลงเกือบ 100% จากออเดอร์แรกที่บอทซื้อ บอทก็จะยังมีตังค์เทรด และก็พยายามซื้อขายเพื่อลากจุดคุ้มทุนลงไปเรื่อยๆแล้วหาจังหวะเคลียร์ออเดอร์ทั้งหมด   ในความเป็นจริงแล้วแทบจะเป็นไปไม่ได้ที่บิทคอยน์จะร่วงลงขนาดนั้น แต่ถ้าต่อให้เกิดขึ้นจริงบอทเราก็จะยังเทรดอยู่

** ความเสี่ยงน้อย ผลตอบแทนน้อย คือสัจธรรมของโลก  ด้วยความที่กลยุทธ์ซอยยิกยิกมีความเสี่ยงที่น้อย จึงไม่ได้กำไรหวือหวาอะไรมาก แต่ก็ได้กำไรเรื่อยๆ กินน้อยๆแต่เน้นอยู่นานอยู่ยาว
  

## มีอะไรเพิ่มมาใน 2.0

- รองรับ Bitkub API V3
- แก้ไขข้อบกพร่องเรื่องการส่งคำสั่ง มีความแม่นยำมากขึ้น
- รายละเอียดใน console ครบถ้วน และดูง่ายสบายตากว่าเดิม

** Bikub API V3 ไม่มีบั๊กในการขายออเดอร์ขนาดเล็กแล้วนะครับ ดังนั้นตอนนี้ BTC สามารถใช้ ORDER_SIZE ขนาดเล็กๆได้แล้ว เช่น 15 บาท 20 บาท

## การติดตั้ง
สำหรับผู้ที่ไม่สันทัดด้านเทคฯ ผมแนะนำให้ใช้ Windows นะครับ โหลดโปรแกรมที่พร้อมใช้งานได้ใน [release](https://github.com/tidLord/Bitkub-SYY/releases)  แตก zip ตั้งค่า config.json แล้วกด .exe รันได้เลยครับ

สำหรับผู้ที่สันทัดด้านเทคฯ
clone repo :

    git clone https://github.com/tidLord/Bitkub-SYY.git

ติดตั้ง python, pip แล้วติดตั้ง requirements ให้เรียบร้อยครับ

    pip install -r requirements.txt

จากนั้นก็รันเลยครับ โดยส่วนตัวผมใช้ [PM2](https://pm2.keymetrics.io/) ครับ ชอบที่ monitor ผ่านหน้าเว็บได้

## หมายเหตุ

- ผู้พัฒนาใช้ Python เวอร์ชั่น 3.12.1 พัฒนาบน Windows 11 นะครับ

- โปรเจคนี้ใช้ชื่อว่า Bitkub-SYY มีคำว่า Bitkub ก็จริง แต่ไม่ได้มีความเกี่ยวข้องใดๆกับบริษัทบิทคับนะครับ ผมเป็นเพียงลูกค้าและผู้ใช้บริการเขาคนหนึ่งเท่านั้น ที่ต้องตั้งชื่อแล้วมีคำว่า Bitkub เพราะบอทโปรเจคนี้สร้างขึ้นมาเพื่อเทรดแค่กับบิทคับเท่านั้นครับ
- ผมทำบอทเทรดเป็นงานอดิเรก เอามาแจกจ่ายเพื่อความสนุกสนานและหวังว่าจะเป็นประโยชน์กับผู้ที่สนใจเท่านั้น นี่ไม่ได้เป็นการชักชวนใครมาลงทุนนะครับ การลงทุนมีความเสี่ยง การใช้บอทมีความเสี่ยง ถ้าเกิดความผิดพลาดไม่ว่าจะจากตัวกลยุทธ์ จากข้อผิดพลาดของโค๊ดหรือตัวโปรแกรม ผมจะไม่รับผิดชอบทุกกรณี  โปรดพิจาณาและตัดสินใจด้วยตัวท่านเองก่อนใช้งานครับ
   
##  Donate


<a href="https://www.buymeacoffee.com/tar888" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

สมัครบัญชี Bitkub ผ่าน Referral Link ของผมได้ที่ : [https://www.bitkub.com/signup?ref=348152](https://www.bitkub.com/signup?ref=348152)

(ย้ำนะครับ นี่ไม่ได้เป็นการชักชวนใครมาลงทุน)
