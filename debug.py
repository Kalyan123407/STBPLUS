#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamFlex19 | Debug Script - Single Channel Test
Channel: 301709
"""

import os
import requests
import json
import sys
from datetime import datetime

# ── ALL VALUES FROM GITHUB SECRETS ──────────────────────────────────────────
ACCESS_TOKEN = os.environ.get('JIOTV_TOKEN', '')
CLEARKEY_URL = os.environ.get('CLEARKEY_URL', '')
JIO_API_BASE = os.environ.get('JIO_API_BASE', '')
JIO_SUB_ID = os.environ.get('JIO_SUB_ID', '')
JIO_RMN = os.environ.get('JIO_RMN', '')
JIO_API_SIG = os.environ.get('JIO_API_SIG', '')
JIO_FEATURE_CODE = os.environ.get('JIO_FEATURE_CODE', '')

# ── TEST CHANNEL ──────────────────────────────────────────────────────────
CHANNEL_ID = 301709
UA = "JioTV.Plus/2.3.1_2041 (Linux;Android 14) AndroidXMedia3/1.4.0"

# ── OUTPUT FILE ──────────────────────────────────────────────────────────
OUTPUT_FILE = "debug_output.txt"

def log(msg):
    """Write to both console and file"""
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# ── CLEAR OUTPUT FILE ──────────────────────────────────────────────────────
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("")

log("=" * 60)
log("🔍 STREAMFLEX19 | DEBUG SINGLE CHANNEL TEST")
log(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
log("=" * 60)

# ── CHECK SECRETS ──────────────────────────────────────────────────────────
log("\n📌 CHECKING SECRETS:")
log(f"  JIOTV_TOKEN     : {'✅ SET' if ACCESS_TOKEN else '❌ MISSING'} (length: {len(ACCESS_TOKEN) if ACCESS_TOKEN else 0})")
log(f"  CLEARKEY_URL    : {CLEARKEY_URL if CLEARKEY_URL else '❌ MISSING'}")
log(f"  JIO_API_BASE    : {JIO_API_BASE if JIO_API_BASE else '❌ MISSING'}")
log(f"  JIO_SUB_ID      : {JIO_SUB_ID if JIO_SUB_ID else '❌ MISSING'}")
log(f"  JIO_RMN         : {'✅ SET' if JIO_RMN else '❌ MISSING'}")
log(f"  JIO_API_SIG     : {'✅ SET' if JIO_API_SIG else '❌ MISSING'}")
log(f"  JIO_FEATURE_CODE: {'✅ SET' if JIO_FEATURE_CODE else '❌ MISSING'}")

# ── CHECK MISSING ──────────────────────────────────────────────────────────
MISSING = []
if not ACCESS_TOKEN: MISSING.append('JIOTV_TOKEN')
if not CLEARKEY_URL: MISSING.append('CLEARKEY_URL')
if not JIO_API_BASE: MISSING.append('JIO_API_BASE')
if not JIO_SUB_ID: MISSING.append('JIO_SUB_ID')
if not JIO_RMN: MISSING.append('JIO_RMN')
if not JIO_API_SIG: MISSING.append('JIO_API_SIG')
if not JIO_FEATURE_CODE: MISSING.append('JIO_FEATURE_CODE')

if MISSING:
    log(f"\n❌ MISSING SECRETS: {', '.join(MISSING)}")
    log("\n" + "=" * 60)
    log("🔍 DEBUG COMPLETE - FAILED")
    log("=" * 60)
    sys.exit(1)

log("\n✅ All secrets loaded successfully!")

# ── TEST API CALL ──────────────────────────────────────────────────────────
log(f"\n📡 TESTING CHANNEL: {CHANNEL_ID}")
log("-" * 60)

url = f"{JIO_API_BASE}/playback/v2/{CHANNEL_ID}"
headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'deviceId': '07301080a973b1f4',
    'subId': JIO_SUB_ID,
    'uniqueid': 'test-debug-001',
    'User-Agent': UA,
    'x-accesstoken': ACCESS_TOKEN,
    'x-apisignatures': JIO_API_SIG,
    'x-appname': 'JioTVPlus',
    'x-feature-code': JIO_FEATURE_CODE,
    'x-page': 'Player',
    'x-platform': 'androidtv',
    'restriction': '0',
    'rmn': JIO_RMN,
}

payload = {
    'bitrateProfile': 'xxhdpi',
    'model': 'Mi TV 4A',
    'manufacturer': 'Xiaomi',
    'osVersion': '15',
    'serialNo': '07301080a973b1f4',
    'is4kSupport': True,
    'hevcSupport': True,
    'dolbySupport': True,
    'appVersion': '2.6.4_2076',
    'deviceType': 'androidtv',
    'drmSupport': 'widevine',
}

log(f"🌐 URL: {url}")

# Mask sensitive data
safe_headers = {}
for k, v in headers.items():
    if k in ['x-accesstoken', 'rmn'] and len(v) > 10:
        safe_headers[k] = v[:10] + '...' + v[-5:]
    else:
        safe_headers[k] = v
log(f"📤 Headers: {json.dumps(safe_headers, indent=2)}")
log(f"📤 Payload: {json.dumps(payload, indent=2)}")

try:
    log("\n⏳ Sending request...")
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    
    log(f"\n📥 RESPONSE STATUS: {response.status_code}")
    
    if response.status_code == 200:
        log("✅ SUCCESS! Channel found!")
        data = response.json()
        pb = data.get('data', data)
        name = pb.get('name', 'Unknown')
        mpd = (pb.get('mpd') or {}).get('auto', 'Not found')
        log(f"\n📺 Channel Name: {name}")
        log(f"📁 MPD URL: {mpd[:100]}..." if len(mpd) > 100 else f"📁 MPD URL: {mpd}")
        log("\n✅ DEBUG COMPLETE - CHANNEL WORKING!")
        log(f"\n✅ SUCCESS! Channel {CHANNEL_ID} is working!")
        
        # Save result
        result = {
            'status': 'success',
            'channel_id': CHANNEL_ID,
            'name': name,
            'mpd_url': mpd,
            'timestamp': datetime.now().isoformat()
        }
        with open('debug_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            
    else:
        log(f"❌ FAILED! HTTP {response.status_code}")
        log(f"📄 Response: {response.text[:500]}")
        
        # Save error
        result = {
            'status': 'failed',
            'channel_id': CHANNEL_ID,
            'http_code': response.status_code,
            'response': response.text[:500],
            'timestamp': datetime.now().isoformat()
        }
        with open('debug_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
except Exception as e:
    log(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
    
    # Save exception
    result = {
        'status': 'error',
        'channel_id': CHANNEL_ID,
        'error': str(e),
        'timestamp': datetime.now().isoformat()
    }
    with open('debug_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

log("\n" + "=" * 60)
log("🔍 DEBUG COMPLETE")
log(f"📁 Output saved to: {OUTPUT_FILE}")
log("=" * 60)

# Print summary
print("\n📊 SUMMARY:")
print(f"  File: {OUTPUT_FILE}")
try:
    with open(OUTPUT_FILE, 'r') as f:
        print(f"  Size: {len(f.read())} bytes")
except:
    print("  Size: 0 bytes")
