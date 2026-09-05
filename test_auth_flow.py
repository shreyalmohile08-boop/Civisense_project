"""
Test complete authentication flow: Admin & Citizen Login, Registration, RBAC Protection, and Session Persistence
"""
import urllib.request
import urllib.parse
import http.cookiejar
import json

BASE_URL = "http://127.0.0.1:5000"

# Setup cookie handler for session persistence
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def run_auth_tests():
    print("[*] Testing Authentication & RBAC System...")

    # 1. Access /login page
    resp = opener.open(f"{BASE_URL}/login")
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "Citizen Portal" in html
    assert "Municipal Authority" in html
    assert "1-Click Demo Login" in html
    print("  [PASS] Login page rendered with dual portals (Citizen & Admin).")

    # 2. Access /admin directly without login (should redirect to login)
    resp = opener.open(f"{BASE_URL}/admin")
    final_url = resp.geturl()
    assert "/login" in final_url
    print("  [PASS] Unauthenticated access to /admin properly blocked & redirected to /login.")

    # 3. Test Municipal Admin Login
    admin_login_data = urllib.parse.urlencode({
        "identifier": "admin",
        "password": "admin123",
        "role": "admin",
        "next": "/admin"
    }).encode('utf-8')
    resp = opener.open(f"{BASE_URL}/login", data=admin_login_data)
    final_url = resp.geturl()
    assert "/admin" in final_url
    html = resp.read().decode('utf-8')
    assert "Command Center" in html
    print("  [PASS] Municipal Admin login succeeded and granted access to /admin.")

    # 4. Test Logout
    resp = opener.open(f"{BASE_URL}/logout")
    assert resp.status == 200
    print("  [PASS] Admin logout succeeded.")

    # 5. Test Citizen Login (Rajesh Sharma)
    citizen_login_data = urllib.parse.urlencode({
        "identifier": "citizen",
        "password": "citizen123",
        "role": "citizen",
        "next": ""
    }).encode('utf-8')
    resp = opener.open(f"{BASE_URL}/login", data=citizen_login_data)
    final_url = resp.geturl()
    assert "/my-reports" in final_url
    html = resp.read().decode('utf-8')
    assert "Citizen Grievance Portfolio" in html
    assert "Rajesh Sharma" in html
    print("  [PASS] Citizen login succeeded and opened Citizen Grievance Portfolio (/my-reports).")

    # 6. Citizen attempting to access /admin should be blocked
    resp = opener.open(f"{BASE_URL}/admin")
    final_url = resp.geturl()
    assert "/login" in final_url
    print("  [PASS] Citizen attempting to access /admin properly blocked by RBAC.")

    # 7. Test New Citizen Registration
    import random
    rand_num = random.randint(1000, 9999)
    reg_data = urllib.parse.urlencode({
        "name": f"Priya Sharma {rand_num}",
        "username": f"priya_{rand_num}",
        "email": f"priya{rand_num}@gmail.com",
        "phone": f"+91 94220 {rand_num}",
        "password": "password123"
    }).encode('utf-8')
    resp = opener.open(f"{BASE_URL}/register", data=reg_data)
    final_url = resp.geturl()
    assert "/my-reports" in final_url
    print(f"  [PASS] New citizen registration succeeded (user: priya_{rand_num}).")

    print("\n[ALL AUTHENTICATION TESTS PASSED] Dual-role login system is 100% operational!")

if __name__ == "__main__":
    run_auth_tests()
