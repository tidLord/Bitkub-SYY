## !!!Attention!!!
ปัจจุบัน 19/12/2566 บิทคับปรับปรุง API เป็น version 3. ซึ่งตอนนี้บอทตัวนี้จะไม่สามารถใช้งานได้ จะต้องทำการแก้ไขและอัพเดททุกๆส่วนที่มีการรับส่งข้อมูลกับ exchange ก่อน

# Bitkub-SYY
บอทเทรดบิทคับ กลยุทธ์ซอยยิกยิก รับข้อมูลราคาสำหรับการคำนวณเพื่อซื้อขายจากเซิร์ฟเวอร์ของบิทคับผ่าน websocket และการส่งคำสั่งซื้อขายแบบ limit order ทำให้บอททำงานด้วยข้อมูลที่ realtime และส่งคำสั่งซื้อขายได้อย่างแม่นยำ

## กลยุทธ์ซอยยิกยิก

![](https://user-images.githubusercontent.com/96503948/183243023-dfa9ea3b-79a9-484e-a084-b195729b1f75.png)

พื้นฐานการทำงานมาจาก grid โดยจะมีเงื่อนไขพื้นฐานดังนี้
- ในกรณีที่ไม่มีออเดอร์ จะทำการซื้อทันที โดยไม่สนใจแนวโน้มตลาดใดๆ
- ในกรณีที่มีออเดอร์ในหน้าตักและราคาขึ้นสูงกว่าระยะราคาที่กำหนด(PRICERANGE) บอทจะทำการขายทันที ถ้าหากมีหลายออเดอร์บอทจะทำงานที่ออเดอร์ที่ราคาต่ำที่สุดก่อนเสมอ
- ในกรณีที่มีออเดอร์ในหน้าตักและราคาร่วงลงต่ำกว่าออเดอร์ที่ซื้อที่ราคาต่ำที่สุด รวมถึงต่ำกว่าระยะราคาที่กำหนด(PRICERANGE) บอทจะทำการซื้อเพิ่ม

ดังนั้นไม่ว่าสภาวะตลาดจะเป็นตลาดกระทิง ตลาดหมี หรืออยู่ในสภาวะ sideway  กลยุทธ์ซอยยิกยิกจะสามารถซื้อขายและทำกำไรได้ในทุกสภาวะตลาด

### ฟังก์ชั่นเคลียร์ออเดอร์

เมื่อมีออเดอร์ในหน้าตัก ระบบของบอทจะทำการเก็บสถิติการซื้อขายและจะคำนวณหาจุดคุ้มทุนที่สามารถสละยานหรือขายทุกออเดอร์ในหน้าตักทิ้งไปได้ ในกรณีที่บอทมีการซื้อขายออเดอร์ที่อยู่ด้านล่าง จุดคุ้มทุนจะขยับต่ำลงมาเรื่อยๆ ถ้าหากมีการเปิดใช้ฟังก์ชั่นนี้ เมื่อราคาถึงจุดคุ้มทุนที่จะออกได้แบบไม่ขาดทุน บอทจะทำการขายทุกออเดอร์ในหน้าตักทั้งหมดทิ้งทันที แล้วจากนั้นจะเริ่มทำการซื้อออเดอร์ใหม่และเริ่มต้นใหม่

## หน้า console

![](https://user-images.githubusercontent.com/96503948/183243054-7be1e24c-6fea-41d1-98c2-465fae7f7cef.png)

บอทจะทำงานในลักษณะ loop โดยแต่ละ loop จะมีข้อมูลดังนี้
- วันเวลาของ loop นั้นๆ
- ในกรณีที่มีออเดอร์ในหน้าตักก็จะโชว์ข้อมูลออเดอร์(ลำดับ, ราคาที่ซื้อ, เลข hash)
- break-even หรือจุดคุ้มทุน
- ชื่อเหรียญหรือโทเคนที่เทรด
- Ask, Bid
- สถานะของบอท บอทกำลังทำอะไรอยู่

## ไฟล์ต่างๆของบอท
ไฟล์เริ่มต้น

- **app.py** ไฟล์ python ไฟล์หลักของบอท
- **config.json** ไฟล์ config
- **temp.json** ไฟล์ความจำชั่วคราวของระบบบอท

หลังจากรันบอท(จะถูกสร้างขึ้นมาโดยอัตโนมัติ)

- **Bitkub-SYY.db** ไฟล์ฐานข้อมูลของบอท
- **last_active.txt** ไฟล์ text บอกวันเวลาที่บอททำงานครั้งล่าสุด (ในกรณีที่เครื่องที่ใช้รันบอทเกิดปัญหา เช่น ไฟดับ)
- **log.txt** ไฟล์ text บอกรายละเอียดการทำงานในทางเทคนิคของบอท รวมถึงข้อผิดพลาดต่างๆ (จะถูกสร้างขึ้นมาอัตโนมัติเมื่อมีเหตุการณ์สำคัญเกิดขึ้น) สามารถลบทิ้งได้แม้ในขณะที่บอททำงานอยู่ ไม่มีผลกับการทำงานของบอท

## config.json
ในไฟล์ config จะมี parameter ต่างๆดังนี้
- **KEY** คือ API Key ที่ได้จากบิทคับ
- **SECRET** คือ Secret Key ที่ได้จากบิทคับ
- **LINETOKEN** คือ token ที่ได้จาก LINE Notify
- **LINE** คือ เปิดหรือปิดใช้งาน LINE Notify (1=เปิด, 0=ปิด)
- **COIN** คือ เหรียญหรือโทเคนที่จะเทรด เช่น KUB, ETH, DOGE เป็นต้น
- **ORDERSIZE** คือ ปริมาณที่จะซื้อแต่ละออเดอร์ มีหน่วยเป็นบาท
- **MAX_ORDER** คือ จำนวนออเดอร์สูงสุดที่จะให้บอทสะสม ถ้าหากบอทซื้อสะสมและมีออเดอร์จำนวนเท่ากับค่านี้ บอทจะไม่ทำการซื้อออเดอร์ใหม่เพิ่ม
- **PRICERANGE** คือ ระยะห่างราคาที่จะขายหรือซื้อเพิ่มของแต่ละออเดอร์(หน่วยเป็นบาท) หรืออีกคำเรียกหนึ่งคือระยะห่าง grid
- **CLEAR_EVERY_BE** คือ เปิดใช้ฟังก์ชั่นเคลียร์ออเดอร์ (1=เปิด, 0=ปิด)
- **CLEAR_ORDER_COUNT** คือ จำนวนออเดอร์ขั้นต่ำที่จะอนุญาตให้บอทเคลียร์ออเดอร์เมื่อราคาสูงกว่าจุดคุ้มทุน เมื่อราคาสูงกว่าจุดคุ้มทุนแต่จำนวนออเดอร์ต่ำกว่า CLEAR_ORDER_COUNT ฟังก์ชั่นเคลียร์ออเดอร์ก็จะยังไม่ทำงาน
- **STOPNEXTCIRCLE** คือ หยุดบอทในการเปิดออเดอร์ใหม่ในกรณีที่ไม่มีออเดอร์ในหน้าตัก แต่ถ้าหากมีออเดอร์อยู่ในหน้าตัก บอทจะยังทำการซื้อขายจนกว่าออเดอร์จะหมดหน้าตัก (1=หยุด, 0=ไม่หยุด)

### สูตรการตั้งค่า(แบบอยู่ยงคงกระพัน)
- **ORDERSIZE** เช่น เรามีเงินทุนอยู่ 1,000 บาท เราต้องการแบ่งเป็น 20 ไม้(MAX_ORDER) ก็เอา 1,000 หารด้วย 20 =50 หมายความว่าได้ไม้ละ 50 บาท เราจะตั้ง ORDERSIZE เป็น 50
- **PRICERANGE** เช่น เราจะเทรดเหรียญ KUB และตอนนี้ราคา KUB อยู่ที่ 100 บาท เราก็ต้องตัดสินใจว่าเราจะรับราคาที่มัน dump ลงมาได้แค่ไหน เช่น เราจะทำให้มันรับได้ที่ 0 บาท ซึ่งราคาจาก 100 ถึง 0 มีระยะ 100-0=100 ทีนี้จำนวน MAX_ORDER เราคือ 20 เราก็เอา 100 หารด้วย 20 จะได้ 5  นี่หมายความว่า PRICERANGE เราคือ 5  ทุกๆการขยับของราคา KUB 5 บาท บอทเราจะทำการซื้อขายนั่นเอง

## ข้อควรระวัง
- ปัจจุบันบิทคับยังมีปัญหาในการขาย BTC ผ่าน API ที่ปริมาณน้อยๆ เช่น 10 บาท (จากที่ลองมาหลายๆเหรียญและหลายๆโทเคนยังไม่เจอปัญหานี้) โปรดหลีกเลี่ยงการเทรดกับ BTC
- อย่าเปลี่ยนเหรียญหรือโทเคนในขณะที่ยังมีออเดอร์ค้างอยู่ในหน้าตัก(ค้างอยู่ในฐานข้อมูล)
- ในขณะที่บอทกำลังเทรดอยู่ โปรดหลีกเลี่ยงการซื้อขายเหรียญหรือโทเคนนั้นๆด้วยตัวเอง
- เมื่อไม่มีออเดอร์ในหน้าตักแล้วและต้องการเปลี่ยนเหรียญหรือโทเคน โปรดทำการรีสตาร์ทบอทหลังจากตั้งค่าใน config เรียบร้อยแล้ว

## ข้อแนะนำ
- เปิดใช้งาน LINE Notify เพื่อการรับข้อมูลการซื้อขายรวมถึงข้อมูลกำไรและขาดทุนต่อออเดอร์แบบ realtime
- สามารถรันบอทนี้โดยใช้ PM2 ได้ แต่ห้ามใช้ PM2 รันบอทที่เป็น executable  หากใช้ linux ที่ไม่มี gui และต้องรันแบบ executable โปรดใช้แอพ screen (อ่านเพิ่มเติมได้ที่ [https://bot.tar.rip/blog/linux](https://bot.tar.rip/blog/linux))
- บอทมีระบบป้องกันการขายขาดทุนและจะไม่ขาดทุนเพราะค่าธรรมเนียม ถึงอย่างไรก็ตาม โปรดตั้ง PRICERANGE ให้มีระยะที่เหมาะสมไม่แคบจนเกินไป

## หมายเหตุ(ข้อมูลทางเทคนิค)
- ผู้พัฒนาใช้ Python เวอร์ชั่น 3.10.4 พัฒนาบน Windows 10
- รูปแบบการส่งคำสั่งคือ limit order และด้วยลักษณะของการส่งคำสั่งของบอท จะเป็นประเภท maker แต่ในปัจจุบันบิทคับยังไม่มีค่าธรรมเนียมโดยเฉพาะสำหรับ maker
- บอทมีการคำนวณค่าธรรมเนียมให้โดยอัตโนมัติ เพราะจากที่ผู้พัฒนาได้ทำการซื้อขายแล้ว เปอร์เซ็นต์ค่าธรรมเนียมนั้นมากกว่า 0.25% ไม่ตรงตามที่บิทคับแจ้ง ดังนั้นถ้าหากเปิดให้ตั้งหรือใช้ตัวเลข 0.25 อาจจะทำให้เกิดการขาดทุนได้ ผู้พัฒนาจึงใช้วิธีการคำนวณจากตัวเลขที่มีการซื้อขายและจ่ายค่าธรรมเนียมจริง เพื่อความปลอดภัยในการขาดทุนจากค่าธรรมเนียม
