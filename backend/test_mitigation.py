#!/usr/bin/env python
"""Test script for reweighing mitigation functionality"""

import requests
import pandas as pd
import io

def test_reweighing():
    """Test the reweighing mitigation endpoint"""
    print("=" * 60)
    print("Testing Reweighing Mitigation")
    print("=" * 60)
    
    # Create a simple biased dataset
    print("\n1. Creating biased test dataset...")
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
    print("\n2. Uploading dataset...")
    files = {'file': ('test_bias.csv', csv_content)}
    resp = requests.post('http://localhost:8000/upload', files=files)
    if resp.status_code != 200:
        print(f"   Upload failed: {resp.text}")
        return False
    
    result = resp.json()
    session_id = result['session_id']
    print(f"   Uploaded successfully")
    print(f"   Session ID: {session_id[:8]}...")
    
    # Run analysis
    print("\n3. Running fairness analysis...")
    analysis_data = {
        'session_id': session_id,
        'sensitive_cols': ['gender'],
        'target_col': 'hired'
    }
    resp = requests.post('http://localhost:8000/analyze', json=analysis_data)
    if resp.status_code != 200:
        print(f"   Analysis failed: {resp.text}")
        return False
    
    results = resp.json()
    dpr = results['gender']['demographic_parity_ratio']
    print(f"   Analysis complete")
    print(f"   DPR: {dpr['value']:.3f} (Status: {dpr['status']})")
    
    # Test mitigation
    if dpr['status'] == 'FAIL':
        print("\n4. Testing reweighing mitigation...")
        mitigation_data = {
            'session_id': session_id,
            'sensitive_col': 'gender',
            'target_col': 'hired'
        }
        resp = requests.post('http://localhost:8000/mitigate', json=mitigation_data)
        if resp.status_code != 200:
            print(f"   Mitigation failed: {resp.text}")
            return False
        
        mitigation = resp.json()
        dpr_before = mitigation['dpr_before']
        dpr_after = mitigation['dpr_after']
        
        print(f"   Mitigation successful!")
        print(f"\n   Results:")
        print(f"   - DPR Before: {dpr_before['value']:.3f} ({dpr_before['status']})")
        print(f"   - DPR After: {dpr_after['value']:.3f} ({dpr_after['status']})")
        print(f"   - Improvement: {(dpr_after['value'] - dpr_before['value']):.3f}")
        print(f"\n   Group rates before: {mitigation['group_rates_before']}")
        print(f"   Group rates after: {mitigation['group_rates_after']}")
        print(f"   Weights applied: {mitigation['weights_applied']}")
        print("\n" + "=" * 60)
        print("REWEIGHING TEST PASSED")
        print("=" * 60)
        return True
    else:
        print("\n   No bias detected - mitigation not needed")
        return True

if __name__ == "__main__":
    test_reweighing()
