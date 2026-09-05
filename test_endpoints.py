"""
Automated end-to-end verification script for Civisense endpoints
"""
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

def run_tests():
    print("[*] Running API & Page sanity checks...")

    # 1. Landing Page
    status, body = test_endpoint(f"{BASE_URL}/")
    assert status == 200, f"Landing page failed: {status}"
    assert "Civisense" in body, "Brand not in landing page"
    assert "Smarter Cities Start With" in body, "Hero section not in landing page"
    print("  [PASS] Landing Page (/) - 200 OK")

    # 2. Report Form Page
    status, body = test_endpoint(f"{BASE_URL}/report")
    assert status == 200, f"Report page failed: {status}"
    assert "Upload Photo Evidence" in body
    print("  [PASS] Report Page (/report) - 200 OK")

    # 3. Track Page with seed ID
    status, body = test_endpoint(f"{BASE_URL}/track?id=CIV-10482")
    assert status == 200, f"Track page failed: {status}"
    assert "CIV-10482" in body
    assert "Remediation Progress Timeline" in body
    print("  [PASS] Track Page (/track?id=CIV-10482) - 200 OK")

    # 4. Login Page & Admin Authentication
    status, body = test_endpoint(f"{BASE_URL}/login")
    assert status == 200
    print("  [PASS] Login Page (/login) - 200 OK")

    # 4b. Admin Dashboard access with Cookie Jar
    import http.cookiejar
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    login_data = urllib.parse.urlencode({
        "identifier": "admin",
        "password": "admin123",
        "role": "admin",
        "next": "/admin"
    }).encode('utf-8')
    resp = opener.open(f"{BASE_URL}/login", data=login_data)
    admin_body = resp.read().decode('utf-8')
    assert "categoryChart" in admin_body
    print("  [PASS] Authenticated Admin Dashboard (/admin) - 200 OK")


    # 5. Analytics API
    status, body = test_endpoint(f"{BASE_URL}/api/analytics")
    assert status == 200
    data = json.loads(body)
    assert "categories" in data and "statuses" in data and "priorities" in data
    print("  [PASS] Analytics API (/api/analytics) - 200 OK")

    # 6. Map Data API
    status, body = test_endpoint(f"{BASE_URL}/api/map-data")
    assert status == 200
    map_data = json.loads(body)
    assert len(map_data.get("complaints", [])) >= 8
    print(f"  [PASS] Map Data API (/api/map-data) - 200 OK ({len(map_data['complaints'])} markers returned)")

    # 7. Admin Status Update API
    update_payload = json.dumps({"complaint_id": "CIV-10482", "status": "Assigned"}).encode('utf-8')
    status, body = test_endpoint(
        f"{BASE_URL}/api/admin/update-status",
        method="POST",
        data=update_payload,
        headers={"Content-Type": "application/json"}
    )
    assert status == 200
    update_resp = json.loads(body)
    assert update_resp.get("success") is True
    print("  [PASS] Status Update API (/api/admin/update-status) - 200 OK")

    # Verify status changed in track view
    status, body = test_endpoint(f"{BASE_URL}/track?id=CIV-10482")
    assert "Assigned" in body
    print("  [PASS] Real-time Status Sync Verified in Track View")

    print("\n[ALL TESTS PASSED] End-to-end endpoints operating perfectly!")

if __name__ == "__main__":
    run_tests()
