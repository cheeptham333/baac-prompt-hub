#!/usr/bin/env python3
"""
เว็บเซิร์ฟเวอร์จำลองสำหรับรันระบบ Prompt Engineering Portal & Gemini Canvas Hub ธ.ก.ส.
สำนักธุรกรรมการเงิน ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import socket

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def get_local_ip():
    """ตรวจจับ IP ในวง LAN อัตโนมัติเพื่อแสดงให้ผู้เรียน 150 คนสแกน"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Doesn't have to be reachable, just triggers OS routing table lookup
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def guess_type(self, path):
        if path.endswith('.ipynb'):
            return 'application/x-ipynb+json'
        if path.endswith('.js'):
            return 'application/javascript; charset=utf-8'
        return super().guess_type(path)

def main():
    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    local_ip = get_local_ip()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url_local = f"http://localhost:{PORT}"
        url_lan = f"http://{local_ip}:{PORT}"
        
        print("=" * 75)
        print("🌾 ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร (ธ.ก.ส.)")
        print("🏛️ สำนักธุรกรรมการเงิน - ระบบคลังแม่แบบ Prompt & Gemini Canvas App Hub")
        print("=" * 75)
        print("✨ สถาปัตยกรรม Zero-API: ไม่ต้องใช้ API Key 100% พร้อมใช้งานทันที")
        print(f"🚀 เซิร์ฟเวอร์เครื่องนี้: {url_local}")
        print(f"📱 URL สำหรับผู้เรียน 150 คนในห้องเรียน (Wi-Fi LAN): {url_lan}")
        print("💡 ให้วิทยากรกดปุ่ม 'QR Code ห้องเรียน (150 คน)' ที่มุมบนขวาเพื่อฉายขึ้นจอโปรเจกเตอร์")
        print("=" * 75)
        print("🛑 กด Ctrl + C เพื่อหยุดการทำงาน")
        print("=" * 75)
        
        try:
            webbrowser.open(url_local)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 ปิดการทำงานเซิร์ฟเวอร์เรียบร้อยแล้ว")
            sys.exit(0)

if __name__ == "__main__":
    main()
