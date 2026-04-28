#!/usr/bin/env python
"""Quick test of mitigation endpoint"""

import requests

session_id = 'c8c5a0d5-8af7-4883-a1dd-5e660815cb47'

print('Testing mitigation...')
resp = requests.post('http://localhost:8000/mitigate', json={
    'session_id': session_id,
    'sensitive_col': 'gender',
    'target_col': 'hired'
})

print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'\nDPR Before: {data["dpr_before"]["value"]:.3f} ({data["dpr_before"]["status"]})')
    print(f'DPR After: {data["dpr_after"]["value"]:.3f} ({data["dpr_after"]["status"]})')
    print(f'Improvement: {data["dpr_after"]["value"] - data["dpr_before"]["value"]:.3f}')
    print(f'\nGroup rates before: {data["group_rates_before"]}')
    print(f'Group rates after: {data["group_rates_after"]}')
    print(f'\nWeights: {data["weights_applied"]}')
    print('\nMitigation test PASSED')
else:
    print(f'Error: {resp.text}')
