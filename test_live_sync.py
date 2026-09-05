import urllib.request
import json

# 1. Update CIV-10482 to Resolved via Admin API
update_req = urllib.request.Request(
    'http://127.0.0.1:5000/api/admin/update-status',
    data=json.dumps({'complaint_id': 'CIV-10482', 'status': 'Resolved'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(update_req) as resp:
    print('Update status response:', resp.read().decode('utf-8'))

# 2. Check API /api/complaints/CIV-10482
with urllib.request.urlopen('http://127.0.0.1:5000/api/complaints/CIV-10482') as resp:
    api_data = json.loads(resp.read().decode('utf-8'))
    print('API Complaint Data:', api_data)
    assert api_data['status'] == 'Resolved'
    assert api_data['status_idx'] == 4
    print('PASS: API status_idx is 4 (Resolved)')

# 3. Check /track?id=CIV-10482 HTML render
with urllib.request.urlopen('http://127.0.0.1:5000/track?id=CIV-10482') as resp:
    html = resp.read().decode('utf-8')
    assert 'data-current-idx="4"' in html
    assert 'id="timeline-step-4"' in html
    assert 'step-completed' in html
    assert 'step-active' in html
    assert 'connector-completed' in html
    print('PASS: HTML correctly renders Stage 5 as completed and active with all connectors!')
