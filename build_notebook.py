import json

notebook = {
    'cells': [],
    'metadata': {
        'accelerator': 'GPU',
        'colab': {
            'provenance': [],
            'toc_visible': True
        },
        'kernelspec': {
            'display_name': 'Python 3',
            'name': 'python3'
        },
        'language_info': {
            'name': 'python'
        }
    },
    'nbformat': 4,
    'nbformat_minor': 0
}

def add_md(text):
    notebook['cells'].append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': [line + '\n' for line in text.strip().split('\n')]
    })

def add_code(code):
    notebook['cells'].append({
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [line + '\n' for line in code.strip().split('\n')]
    })

# Title
add_md('''# 🌾 Google Gemini & Prompt Engineering Workshop
## สำหรับสำนักธุรกรรมการเงิน ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร (ธ.ก.ส.)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com)

สมุดงานเชิงปฏิบัติการ (Interactive Workshop Notebook) เล่มนี้ ออกแบบมาเพื่อเสริมศักยภาพพนักงาน **ธ.ก.ส. สำนักธุรกรรมการเงิน ทั้ง 11 กลุ่มงาน** ในการประยุกต์ใช้ Generative AI (Google Gemini) ในกระบวนการทำงานจริงอย่างมีประสิทธิภาพ ถูกต้อง และปลอดภัยตามหลักธรรมาภิบาลข้อมูล (Data Governance & PDPA)

---
### 📌 สารบัญหลักสูตร
1. **Part 1:** การติดตั้งและเชื่อมต่อ Google Gemini API
2. **Part 2:** แก่นแท้ของ Prompt Engineering สำหรับงานธนาคาร (RTF Framework, Security & PDPA)
3. **Part 3:** โค้ดตัวอย่างและ Prompt Templates ประจำ 11 กลุ่มงาน สำนักธุรกรรมการเงิน
4. **Part 4:** Workshop & Practice Exercises (แบบฝึกหัดสถานการณ์จริง + แนวทางเฉลย)
5. **Part 5:** Advanced Pattern: Structured Output (JSON Schema) สำหรับงานกระทบยอด
''')

# Part 1
add_md('''---
## 🚀 Part 1: การติดตั้งและเชื่อมต่อ Google Gemini API
ในส่วนนี้เราจะติดตั้งแพ็กเกจ `google-generativeai` และกำหนดค่า API Key''')

add_code('''# 1. ติดตั้ง SDK ของ Google Generative AI
!pip install -q -U google-generativeai
print("✅ ติดตั้ง Library สำเร็จพร้อมใช้งาน!")''')

add_code('''# 2. ตั้งค่า API Key และทดสอบการเชื่อมต่อ
import os
import google.generativeai as genai

try:
    from google.colab import userdata
    GEMINI_API_KEY = userdata.get('GEMINI_API_KEY')
except Exception:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.2,
        "top_p": 0.95,
        "max_output_tokens": 2048,
    }
)

print("🤖 เชื่อมต่อโมเดล Gemini สำเร็จ!")''')

# Part 2
add_md('''---
## 🧠 Part 2: แก่นแท้ Prompt Engineering สไตล์งานธนาคาร
การเขียน Prompt ในงานธนาคารต้องการ **ความแม่นยำสูง (High Precision)** และ **ความปลอดภัยของข้อมูล (Data Privacy)**

### 💡 RTF Framework:
- **R - Role (บทบาท):** กำหนดว่า AI เป็นใคร เช่น "คุณคือนักวิเคราะห์ระบบชำระเงิน ธ.ก.ส."
- **T - Task (ภารกิจ):** สั่งให้ทำอะไรอย่างเจาะจง ระบุขั้นตอนชัดเจน
- **F - Format (รูปแบบผลลัพธ์):** บังคับโครงสร้างคำตอบ เช่น ตาราง Markdown, หัวข้อสรุป, หรือ JSON

### 🛡️ กฎเหล็ก Data Privacy & PDPA:
1. **ห้ามใส่เลขบัญชีจริง:** แปลงเป็น Masking เสมอ เช่น `xxx-x-x1234-x`
2. **ห้ามใส่เลขบัตรประชาชน 13 หลัก:** แปลงเป็น `x-xxxx-xxxxx-xx-x`
3. **ตัดชื่อ-นามสกุลลูกค้าจริง:** ใช้ชื่อสมมติในการทดสอบ''')

add_code('''# ตัวอย่างฟังก์ชัน Masking ข้อมูลส่วนบุคคลก่อนส่งให้ AI
import re

def mask_sensitive_data(text: str) -> str:
    """ปิดบังข้อมูลสำคัญ (Account, Citizen ID, Phone) ก่อนส่งเข้า LLM"""
    text = re.sub(r'\\b(\\d{3})-?\\d{6}-?(\\d{1,3})\\b', r'\\1-xxxxxx-\\2', text)
    text = re.sub(r'\\b\\d{1}\\s?\\d{4}\\s?\\d{5}\\s?\\d{2}\\s?\\d{1}\\b', 'x-xxxx-xxxxx-xx-x', text)
    text = re.sub(r'\\b0[689]\\d-?\\d{3}-?\\d{4}\\b', '08x-xxx-xxxx', text)
    return text

sample_input = "ลูกค้าชื่อ นายสมชาย บัญชี 020123456789 โทร 081-234-5678 ร้องเรียนเงินไม่เข้า"
print("ข้อมูลดิบ:", sample_input)
print("ข้อมูลหลัง Mask:", mask_sensitive_data(sample_input))''')

# Part 3
add_md('''---
## 🏢 Part 3: Templates ประจำ 11 กลุ่มงาน สำนักธุรกรรมการเงิน
ครอบคลุมภารกิจทั้ง 11 กลุ่มงานของสำนักธุรกรรมการเงิน ธ.ก.ส.''')

add_code('''def ask_gemini(prompt: str, system_instruction: str = None) -> str:
    """ส่ง Prompt ไปยัง Gemini API และแสดงคำตอบอย่างสวยงาม"""
    try:
        if system_instruction:
            custom_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            response = custom_model.generate_content(prompt)
        else:
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ เกิดข้อผิดพลาดในการเรียก API: {e}\\n(หมายเหตุ: โปรดตรวจสอบว่าได้ระบุ GEMINI_API_KEY ที่ถูกต้องในขั้นตอนที่ 1)"''')

add_md('''### 📂 กลุ่มงานที่ 6: ปฏิบัติการโอนเงินระหว่างธนาคาร
**ภารกิจ:** ดูแลสนับสนุนการให้บริการของสาขาในการโอนเงินระหว่างธนาคาร ประสานงานและแก้ไขปัญหาการโอนเงิน ลูกค้า ธนาคารคู่โอน และแก้ไขข้อร้องเรียน''')

add_code('''system_prompt_g6 = """
คุณคือเจ้าหน้าที่อาวุโสด้านบริการธุรกรรมการเงิน ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร (ธ.ก.ส.)
สื่อสารด้วยน้ำเสียงสุภาพ เห็นอกเห็นใจลูกค้าเกษตรกร และอธิบายขั้นตอนทางการเงินอย่างชัดเจนโปร่งใส
"""

user_prompt_g6 = """
กรุณาร่างข้อความชี้แจงลูกค้าทาง SMS/Mobile Notification และร่างสคริปต์ให้เจ้าหน้าที่สาขาใช้โทรชี้แจงลูกค้า

ข้อมูลกรณี:
- ลูกค้า: คุณจำลอง (ลูกค้าสินเชื่อเพื่อการเกษตร ธ.ก.ส. สาขาแม่ริม)
- วันที่ทำรายการ: วันนี้ เวลา 09:30 น.
- ช่องทาง: แอปพลิเคชัน BAAC A-Mobile
- รายการ: โอนเงิน 15,000 บาท ไปยังบัญชีธนาคารกรุงเทพ ผ่านพร้อมเพย์
- ปัญหา: ยอดเงินในบัญชี ธ.ก.ส. ถูกตัดแล้ว แต่บัญชีปลายทางไม่ได้รับเงิน
- ผลตรวจสอบ: เครือข่าย Switching กลางมีปัญหา Time-out ทาง ธ.ก.ส. ได้ตั้งพักรายการไว้ และจะดำเนินการคืนเงินเข้าบัญชีต้นทางให้อัตโนมัติภายใน 19:00 น. ของวันทำการถัดไป ตามมาตรฐาน SLA ธปท.
"""

print("🔄 กำลังประมวลผล...")
result_g6 = ask_gemini(user_prompt_g6, system_instruction=system_prompt_g6)
print(result_g6)''')

add_md('''### 📂 กลุ่มงานที่ 7: ปฏิบัติการเรียกเก็บเช็ค
**ภารกิจ:** ติดตาม กำกับ ควบคุม การเรียกเก็บตามเช็ค ตราสารทางการเงิน ตรวจสอบความสมบูรณ์ของภาพเช็ค ลายมือชื่อ การอนุมัติหักบัญชี''')

add_code('''system_prompt_g7 = """
คุณคือผู้เชี่ยวชาญการตรวจหักบัญชีเช็คด้วยภาพเช็ค (ICAS) ตามมาตรฐานธนาคารแห่งประเทศไทยและระเบียบ ธ.ก.ส.
มีความเคร่งครัดในกฎหมายว่าด้วยตั๋วเงิน และแม่นยำในรหัสการคืนเช็ค
"""

user_prompt_g7 = """
กรุณาวิเคราะห์รายการเช็คต่อไปนี้ และระบุว่า "ผ่าน" หรือ "คืนเช็ค" พร้อมให้เหตุผลทางกฎหมาย/ระเบียบ:

ข้อมูลหน้าเช็ค:
- เช็คเลขที่: 2048911
- สั่งจ่ายจากบัญชี: บัญชีนายสุริยา (สาขาขอนแก่น)
- สั่งจ่ายให้: นายทองมี มีนา
- จำนวนเงินตัวเลข: 100,000 บาท
- จำนวนเงินตัวอักษร: "หนึ่งหมื่นบาทถ้วน"
- วันที่สั่งจ่าย: 11 กันยายน 2567
- สภาพภาพเช็ค: มีการขีดฆ่าตัวเลขแก้ไขเป็น 10,000 บาท แต่ไม่มีลายเซ็นกำกับของผู้สั่งจ่ายตรงจุดแก้ไข
"""

print("🔄 กำลังประมวลผล...")
result_g7 = ask_gemini(user_prompt_g7, system_instruction=system_prompt_g7)
print(result_g7)''')

add_md('''### 📂 กลุ่มงานที่ 8: ตรวจพิสูจน์และชำระดุล
**ภารกิจ:** ตรวจสอบ พิสูจน์ และปรับปรุงรายการธุรกรรมการโอนเงิน การกระทบยอดบัญชีเงินฝากผ่านช่องทางอัตโนมัติ''')

add_code('''system_prompt_g8 = """
คุณคือผู้เชี่ยวชาญด้านบัญชีและการกระทบยอดธุรกรรมอิเล็กทรอนิกส์ (Reconciliation Specialist) ของ ธ.ก.ส.
ชำนาญการวิเคราะห์ความแตกต่างระหว่างระบบ Core Banking, Switch Host และ Settlement Report
"""

user_prompt_g8 = """
กรุณาทำรายงานกระทบยอด (Reconcile) ประจำวัน และแนะนำรายการบันทึกบัญชีปรับปรุง:

ข้อมูลประจำวันที่ 11 ก.ย.:
1. บันทึก Core Banking (บัญชีลูกค้าถูกตัดเงิน): 1,200 รายการ มูลค่า 3,600,000 บาท
2. บันทึก Transaction Switch (ทำรายการสำเร็จ): 1,202 รายการ มูลค่า 3,608,000 บาท
3. รายงาน Settlement จากเครือข่ายกลาง: 1,200 รายการ มูลค่า 3,600,000 บาท
"""

print("🔄 กำลังประมวลผล...")
result_g8 = ask_gemini(user_prompt_g8, system_instruction=system_prompt_g8)
print(result_g8)''')

# Part 4
add_md('''---
## ✍️ Part 4: Workshop & Practice Exercises (แบบฝึกหัดสำหรับผู้เข้าอบรม)
ลองฝึกออกแบบ Prompt ด้วยตัวคุณเองตามโจทย์สถานการณ์จริงของ ธ.ก.ส.

### 📝 โจทย์ข้อที่ 1: กลุ่มงานบริหารจัดการเงินสดสาขา (กลุ่ม 4)
**สถานการณ์:** สาขาพิมาย คาดการณ์ว่าจะมีการเบิกจ่ายเงินสดสูงมากในสัปดาห์หน้า เนื่องจากตรงกับวันจ่ายเงินเบี้ยยังชีพผู้สูงอายุและเงินช่วยเหลือชาวนา
**ภารกิจของคุณ:** จงเขียน Prompt สั่งให้ Gemini วางแผนสำรองเงินสดรายวัน (Cash Replenishment Plan) เพื่อไม่ให้เงินสดตู้ ATM และเคาน์เตอร์ขาดมือ แต่ยังคงต้นทุนการถือครองเงินสด (Holding Cost) ต่ำที่สุด''')

add_code('''my_prompt_ex1 = """
# TODO: เขียน Prompt ของคุณที่นี่ตาม RTF Framework (Role - Task - Format)
"""

# ทดสอบรัน Prompt ของคุณ
# print(ask_gemini(my_prompt_ex1))''')

add_md('''### 📝 โจทย์ข้อที่ 2: กลุ่มงานตรวจพิสูจน์และกระทบยอดเงินสด ATM/CDM (กลุ่ม 9)
**สถานการณ์:** ตู้ ATM หน้าร้านค้าสหกรณ์ เกิดเหตุไฟดับชั่วขณะระหว่างที่ลูกค้ากำลังถอนเงิน 5,000 บาท บัญชีตัดเงินสำเร็จ แต่ลูกค้าไม่ได้รับเงินสด และแจ้งเรื่องร้องเรียนเข้ามา
**ภารกิจของคุณ:** จงเขียน Prompt สั่งให้ Gemini ร่างขั้นตอนสืบค้น Electronic Journal (EJ) และร่างหนังสือแจ้งผลการปรับปรุงยอดเงินคืนลูกค้า''')

add_code('''my_prompt_ex2 = """
# TODO: เขียน Prompt ของคุณที่นี่
"""

# ทดสอบรัน Prompt ของคุณ
# print(ask_gemini(my_prompt_ex2))''')

# Part 5
add_md('''---
## ⚡ Part 5: Advanced Pattern: Structured Output (JSON Schema)
สำหรับการนำ AI ไปเชื่อมต่อกับระบบงาน Core Banking เราสามารถบังคับให้ Gemini ส่งคำตอบเป็น **JSON ที่มี Schema ชัดเจน** 100% เพื่อนำไปประมวลผลต่อด้วยโปรแกรมโดยไม่มีข้อผิดพลาด''')

add_code('''import json
from google.generativeai.types import GenerationConfig

prompt_structured = """
วิเคราะห์ข้อความแจ้งปัญหาต่อไปนี้ และแปลงเป็นโครงสร้าง JSON:
'ลูกค้าสมหมาย แจ้งว่าเมื่อวานนี้ 10 ก.ย. โอนเงินผ่าน A-Mobile จำนวน 4,500 บาท ไปยังบัญชี กสิกรไทย 045-2-12345-6 ปลายทางไม่ได้รับเงิน แต่ตัดบัญชีตนเองแล้ว รหัสอ้างอิง TX991823'
"""

structured_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="คุณคือ API Parser แปลงข้อความร้องเรียนธุรกรรมการเงินเป็น JSON Schema เท่านั้น ห้ามตอบคำอธิบายอื่น",
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "transaction_date": {"type": "string"},
                "amount": {"type": "number"},
                "channel": {"type": "string"},
                "destination_bank": {"type": "string"},
                "destination_account": {"type": "string"},
                "reference_id": {"type": "string"},
                "issue_type": {"type": "string", "enum": ["MONEY_NOT_CREDITED", "WRONG_ACCOUNT", "SYSTEM_TIMEOUT", "OTHER"]}
            },
            "required": ["customer_name", "amount", "destination_bank", "issue_type"]
        }
    )
)

try:
    response = structured_model.generate_content(prompt_structured)
    print("ผลลัพธ์แบบ Structured JSON:")
    print(response.text)
    parsed = json.loads(response.text)
    print("\\nทดสอบดึงค่าใน Python:")
    print(f"ชื่อลูกค้า: {parsed.get('customer_name')}")
    print(f"ยอดเงิน: {parsed.get('amount'):,} บาท")
    print(f"ปัญหา: {parsed.get('issue_type')}")
except Exception as e:
    print(f"⚠️ เกิดข้อผิดพลาด: {e}")''')

add_md('''---
### 🎓 สรุปสิ่งที่ได้เรียนรู้และก้าวต่อไป
1. พนักงาน ธ.ก.ส. สามารถใช้ **RTF Framework** และ **APP-CRAFT Framework** เพื่อสร้าง Prompt และเว็บแอพบน Gemini Canvas สำหรับกลุ่มงานของตนเอง
2. การคำนึงถึง **Data Privacy (PDPA)** ต้องทำเสมอก่อนนำข้อมูลลูกค้ามาประมวลผล
3. สามารถนำ Template ทั้ง 11 กลุ่มงานจากระบบเว็บไซค์ไปประยุกต์ใช้งานจริงได้ทันที

**สำนักธุรกรรมการเงิน ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร**
''')

with open('notebooks/BAAC_Prompt_Engineering_Gemini.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=2)

print("🎉 สร้างไฟล์ notebooks/BAAC_Prompt_Engineering_Gemini.ipynb สำเร็จเรียบร้อย!")
