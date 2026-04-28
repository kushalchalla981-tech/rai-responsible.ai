#!/usr/bin/env python
"""Test script for reweighing mitigation - with server restart check"""

import requests
import pandas as pd
import io
import subprocess
import time
import sys

def wait_for_server(url="http://localhost:8000/health", max_attempts=30):
    """Wait for server to be ready"""
    for i in range(max_attempts):
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                print("   Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Waiting for server... ({i}/{max_attempts})")
    return False

def test_reweighing():
    """Test the reweighing mitigation endpoint"""
    print("=" * 60)
    print("Testing Reweighing Mitigation")
    print("=" * 60)
    
    # Check if server is running
    print("\n1. Checking server status...")
    try:
        resp = requests.get("http://localhost:8000/health", timeout=2)
        if resp.status_code == 200:
            print("   Server is running")
        else:
            print("   Server returned error:", resp.status_code)
            return False
    except Exception as e:
        print(f"   Server not responding: {e}")
        print("   Please start the backend server first:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    # Create a simple biased dataset
    print("\n2. Creating biased test dataset...")
    data = {
        'gender': ['Male'] * 80 + ['Female'] * 20,
        'hired': [1] * 70 + [0] * 10 + [1] * 10 + [0] * 10
    }
    df = pd.DataFrame(data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    print(f"   Created dataset with {len(df)} rows")
    print(f"   Male hired rate: 70/80 = 87.5%")
    print(f"   Female hired rate: 10/20 = 50%")
    
    # Upload dataset
    print("\n3. Uploading dataset...")
    files = {'file': ('test_bias.csv', csv_content)}
    resp = requests.post('http://localhost:8000/upload', files=files)
    if resp.status_code != 200:
        print(f"   Upload failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    result = resp.json()
    session_id = result['session_id']
    print(f"   Uploaded successfully")
    print(f"   Session ID: {session_id}")
    
    # Run analysis
    print("\n4. Running fairness analysis...")
    analysis_data = {
        'session_id': session_id,
        'sensitive_cols': ['gender'],
        'target_col': 'hired'
    }
    resp = requests.post('http://localhost:8000/analyze', json=analysis_data)
    if resp.status_code != 200:
        print(f"   Analysis failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    results = resp.json()
    print(f"   Analysis complete")
    print(f"   Results: {results}")
    
    dpr = results['gender']['demographic_parity_ratio']
    print(f"   DPR: {dpr['value']:.3f} (Status: {dpr['status']})")
    
    # Test mitigation
    if dpr['status'] == 'FAIL':
        print("\n5. Testing reweighing mitigation...")
        mitigation_data = {
            'session_id': session_id,
            'sensitive_col': 'gender',
            'target_col': 'hired'
        }
        resp = requests.post('http://localhost:8000/mitigate', json=mitigation_data)
        if resp.status_code != 200:
            print(f"   Mitigation failed: {resp.status_code}")
            print(f"   Response: {resp.text}")
            return False
        
        mitigation = resp.json()
        print(f"   Mitigation response received")
        print(f"   Response keys: {list(mitigation.keys())}")
        
        dpr_before = mitigation['dpr_before']
        dpr_after = mitigation['dpr_after']
        
        print(f"\n   Results:")
        print(f"   - DPR Before: {dpr_before['value']:.3f} ({dpr_before['status']})")
        print(f"   - DPR After: {dpr_after['value']:.3f} ({dpr_after['status']})")
        print(f"   - Improvement: {(dpr_after['value'] - dpr_before['value']):.3f}")
        print(f"   - Weights applied: {mitigation.get('weights_applied', 'N/A')}")
        print("\n" + "=" * 60)
        print("REWEIGHING TEST PASSED")
        print("=" * 60)
        return True
    else:
        print("\n   No bias detected - mitigation not needed")
        return True

if __name__ == "__main__":
    success = test_reweighing()
    sys.exit(0 if success else 1)
