#!/usr/bin/env python3
"""
สคริปต์ทดสอบและตรวจสอบความถูกต้องของระบบคลังแม่แบบ Prompt & Gemini Canvas Hub ธ.ก.ส.
ครอบคลุม 11 กลุ่มงาน สำนักธุรกรรมการเงิน ธ.ก.ส.
"""

import os
import sys
import re

PASS_COUNT = 0
FAIL_COUNT = 0

def assert_test(condition, message):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  ✅ PASS: {message}")
    else:
        FAIL_COUNT += 1
        print(f"  ❌ FAIL: {message}")

def run_tests():
    print("=" * 65)
    print("🌾 ตรวจสอบระบบคลังแม่แบบ Prompt & Gemini Canvas App Hub ธ.ก.ส.")
    print("=" * 65)

    # 1. Check Files Existence
    print("\n--- 1. File Integrity & Assets ---")
    assert_test(os.path.exists("index.html"), "index.html exists")
    assert_test(os.path.exists("data/templates.js"), "data/templates.js exists")
    assert_test(os.path.exists("data/canvas_templates.js"), "data/canvas_templates.js exists")
    assert_test(os.path.exists("data/qrcode.js"), "data/qrcode.js exists")
    assert_test(os.path.exists("notebooks/BAAC_Prompt_Engineering_Gemini.ipynb"), "Colab notebook exists")
    assert_test(os.path.exists("run_server.py"), "run_server.py exists")

    # Read contents
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    with open("data/templates.js", "r", encoding="utf-8") as f:
        templates_js = f.read()

    with open("data/canvas_templates.js", "r", encoding="utf-8") as f:
        canvas_js = f.read()

    with open("data/qrcode.js", "r", encoding="utf-8") as f:
        qrcode_js = f.read()

    # 2. Check Zero-API & Security
    print("\n--- 2. Zero-API & Zero-Setup ---")
    assert_test("api-key-input" not in html, "No API Key input elements in HTML")
    assert_test("baac_gemini_api_key" not in html, "No API Key localStorage reads")
    assert_test("โหมดจำลอง (Mock Mode)" not in html, "No confusing Mock Mode warnings")
    assert_test("ไม่ต้องใช้ API Key 100%" in html, "Reassuring Zero-API badge present in Header")

    # 3. Check Mobile-First & Touch Targets
    print("\n--- 3. Mobile-First & 1-Tap Copy ---")
    assert_test("min-h-[48px]" in html, "1-Tap Copy button meets minimum 48px height")
    assert_test("touch-target" in html, "Touch-target CSS class present")
    assert_test("font-size: 16px !important" in html, "16px font sizing prevents iOS Safari auto-zoom")
    assert_test("fallbackCopy" in html, "Two-stage fallback clipboard copy implemented")

    # 4. Check Sample Output Previews
    print("\n--- 4. Instant AI Output Preview ---")
    assert_test("SampleOutputRenderer" in html, "Markdown and table renderer component exists")
    assert_test("ตัวอย่างคำตอบ AI" in html, "Sample AI output tab exists")
    assert_test("sampleOutput:" in templates_js, "Templates contain pre-computed realistic sample outputs")

    # 5. Check Classroom QR Code
    print("\n--- 5. Classroom QR Code Access (150 Learners) ---")
    assert_test("generateQRCodeSVG" in qrcode_js, "qrcode.js defines generateQRCodeSVG")
    assert_test("data/qrcode.js" in html, "index.html imports qrcode.js")
    assert_test("QR Code ห้องเรียน (150 คน)" in html, "Prominent classroom QR button exists in Header")
    assert_test("qrHighContrast" in html, "High-contrast mode for classroom projectors exists")

    # 6. Check Complete 11 Departments in Daily Templates
    print("\n--- 6. Complete 11 BAAC Departments in Templates ---")
    for i in range(1, 12):
        code_str = f"{i:02d}"
        assert_test(f'code: "{code_str}"' in templates_js, f"Department code {code_str} present in templates.js")

    # 7. Check Gemini Canvas App Builder & APP-CRAFT Framework
    print("\n--- 7. Gemini Canvas App Builder & APP-CRAFT Framework ---")
    assert_test("data/canvas_templates.js" in html, "index.html imports data/canvas_templates.js")
    assert_test("สร้างแอพบน Gemini Canvas" in html, "Top Segmented Mode Switcher contains Canvas mode")
    assert_test("APP_CRAFT_GUIDE" in canvas_js, "canvas_templates.js defines APP_CRAFT_GUIDE")
    assert_test("A - Aim & Role" in canvas_js, "Step 1 (Aim & Role) present in guide")
    assert_test("P - Processing Logic" in canvas_js, "Step 2 (Processing Logic) present in guide")
    assert_test("P - Presentation & Style" in canvas_js, "Step 3 (Presentation & Style) present in guide")
    assert_test("C - Concrete Mock Data" in canvas_js, "Step 4 (Concrete Mock Data) present in guide")
    assert_test("R - Refinement on Canvas" in canvas_js, "Step 5 (Refinement on Canvas) present in guide")


    # 9. Check Mobile-First Ergonomics & Mobile App Experience
    print("\n--- 9. Mobile App Experience & PWA Ergonomics ---")
    assert_test("mobile-web-app-capable" in html, "PWA & mobile-web-app-capable meta tags present")
    assert_test("theme-color" in html, "Theme color meta tag for BAAC green present")
    assert_test("md:hidden" in html and "คลัง Prompt" in html, "Sticky Mobile Bottom Navigation bar present")
    assert_test("gemini.google.com" in html, "Direct 'เปิด Gemini' 1-tap deep links present")
    assert_test("InteractiveCanvasDemo" in html, "Interactive Zero-API Canvas Demo Simulator component present")
    assert_test("วิธีใช้บนมือถือ 3 ก้าว" in html, "Mobile 3-Step Quick Guide banner present")
    assert_test("showBackToTop" in html, "Floating Back-to-Top button present")

    # Check all 11 Canvas Apps exist
    print("\n--- 8. 11 Ready-to-Use Canvas App Generator Prompts ---")
    assert_test("CANVAS_APP_TEMPLATES" in canvas_js, "canvas_templates.js defines CANVAS_APP_TEMPLATES")
    for i in range(1, 12):
        code_str = f"{i:02d}"
        assert_test(f'deptCode: "{code_str}"' in canvas_js, f"Canvas Mini-App for Department {code_str} present")

    # Check key app functionalities
    assert_test("BAAC Strategic KPI & Action Dashboard" in canvas_js, "Dept 01 KPI Dashboard prompt exists")
    assert_test("Smart BRD & Test Case Generator Studio" in canvas_js, "Dept 02 BRD Generator prompt exists")
    assert_test("Withholding Tax & Branch EOD Checklist App" in canvas_js, "Dept 03 Tax & EOD prompt exists")
    assert_test("Branch Cash Demand & Holding Cost Simulator" in canvas_js, "Dept 04 Cash Demand prompt exists")
    assert_test("SPIN Error Analyzer & Revenue Sharing Calculator" in canvas_js, "Dept 05 SPIN Error prompt exists")
    assert_test("Interbank Transfer Exception & BOT SLA Desk" in canvas_js, "Dept 06 Interbank SLA prompt exists")
    assert_test("ICAS Cheque Validator & Return Code Resolver" in canvas_js, "Dept 07 ICAS Cheque prompt exists")
    assert_test("3-Way Reconciliation & Variance Matcher" in canvas_js, "Dept 08 Reconciliation prompt exists")
    assert_test("ATM Cash Short/Over & VOC Resolution Desk" in canvas_js, "Dept 09 ATM VOC prompt exists")
    assert_test("Banking Agent Due Diligence & Scoring Matrix" in canvas_js, "Dept 10 Agent Scoring prompt exists")
    assert_test("Off-site ATM Cash-out Predictor & CIT Planner" in canvas_js, "Dept 11 Offsite ATM CIT prompt exists")


    # 10. Check Category Completeness (Document, Analysis, Reconciliation)
    print("\n--- 10. Category Completeness for 11 BAAC Departments ---")
    all_depts = [
        "policy-plan", "system-dev", "banking-ops-compliance", "branch-cash-mgmt",
        "inter-branch-payment", "inter-bank-transfer", "cheque-clearing",
        "verification-settlement", "atm-reconciliation", "banking-agent", "offsite-atm-cash"
    ]
    
    # Document category in all 11 departments
    for did in all_depts:
        pattern = rf'deptId:\s*"{did}",\s*category:\s*"document"'
        assert_test(bool(re.search(pattern, templates_js)), f"Category 'document' present in {did}")

    # Analysis category in all 11 departments
    for did in all_depts:
        pattern = rf'deptId:\s*"{did}",\s*category:\s*"analysis"'
        assert_test(bool(re.search(pattern, templates_js)), f"Category 'analysis' present in {did}")

    # Reconcile category in operational financial departments (at least 9)
    reconcile_depts = [
        "banking-ops-compliance", "branch-cash-mgmt", "inter-branch-payment",
        "inter-bank-transfer", "cheque-clearing", "verification-settlement",
        "atm-reconciliation", "banking-agent", "offsite-atm-cash"
    ]
    for did in reconcile_depts:
        pattern = rf'deptId:\s*"{did}",\s*category:\s*"reconcile"'
        assert_test(bool(re.search(pattern, templates_js)), f"Category 'reconcile' present in {did}")

    # Dynamic category filtering assertions
    assert_test("availableCategories" in html, "Dynamic availableCategories hook in index.html")
    assert_test("filter(cat => cat.count > 0)" in html, "Hides 0-count categories dynamically in index.html")
    assert_test("setSelectedCategory(\"all\")" in html, "Auto-resets category when changing departments")


    # 11. Check Official BAAC Logo & CI Compliance
    print("\n--- 11. Official BAAC Logo & Corporate Identity (CI) ---")
    assert_test(os.path.exists("assets/baac-logo.webp"), "assets/baac-logo.webp exists")
    assert_test(os.path.exists("assets/logo_base64.js"), "assets/logo_base64.js exists")
    assert_test("assets/baac-logo.webp" in html, "Official BAAC logo linked in index.html (favicon & img)")
    assert_test("BAAC_LOGO_DATA_URI" in html, "BAAC_LOGO_DATA_URI embedded with offline fallback")
    assert_test("1593" in html, "Official BAAC Call Center 1593 in Topbar and Footer")
    assert_test("setFontScale" in html, "Interactive Accessibility Font Size adjuster (A-, A, A+) present")
    assert_test("ธนาคารพัฒนาชนบทที่ยั่งยืน" in html, "Official BAAC bank motto present")

    print("\n" + "=" * 65)
    print(f"ผลการทดสอบทั้งหมด: ผ่าน {PASS_COUNT} ข้อ, ไม่ผ่าน {FAIL_COUNT} ข้อ")
    print("=" * 65)

    if FAIL_COUNT == 0:
        print("🎉 ระบบผ่านการตรวจสอบความสมบูรณ์ครบถ้วน 100%!")
        return 0
    else:
        print(f"⚠️ พบข้อผิดพลาด {FAIL_COUNT} จุด โปรดตรวจสอบและแก้ไข")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
