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

print("=" * 60)
print("🔍 STREAMFLEX19 | DEBUG SINGLE CHANNEL TEST")
print("=" * 60)

# ── CHECK SECRETS ──────────────────────────────────────────────────────────
print("\n📌 CHECKING SECRETS:")
print(f"  JIOTV_TOKEN     : {'✅ SET' if ACCESS_TOKEN else '❌ MISSING'} (length: {len(ACCESS_TOKEN) if ACCESS_TOKEN else 0})")
print(f"  CLEARKEY_URL    : {CLEARKEY_URL if CLEARKEY_URL else '❌ MISSING'}")
print(f"  JIO_API_BASE    : {JIO_API_BASE if JIO_API_BASE else '❌ MISSING'}")
print(f"  JIO_SUB_ID      : {JIO_SUB_ID if JIO_SUB_ID else '❌ MISSING'}")
print(f"  JIO_RMN         : {'✅ SET' if JIO_RMN else '❌ MISSING'}")
print(f"  JIO_API_SIG     : {'✅ SET' if JIO_API_SIG else '❌ MISSING'}")
print(f"  JIO_FEATURE_CODE: {'✅ SET' if JIO_FEATURE_CODE else '❌ MISSING'}")

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
    print(f"\n❌ MISSING SECRETS: {', '.join(MISSING)}")
    sys.exit(1)

print("\n✅ All secrets loaded successfully!")

# ── TEST API CALL ──────────────────────────────────────────────────────────
print(f"\n📡 TESTING CHANNEL: {CHANNEL_ID}")
print("-" * 60)

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

print(f"🌐 URL: {url}")
print(f"📤 Headers: {json.dumps({k: v[:20]+'...' if k in ['x-accesstoken', 'rmn'] and len(v) > 20 else v for k, v in headers.items()}, indent=2)}")
print(f"📤 Payload: {json.dumps(payload, indent=2)}")

try:
    print("\n⏳ Sending request...")
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    
    print(f"\n📥 RESPONSE STATUS: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Channel found!")
        data = response.json()
        pb = data.get('data', data)
        name = pb.get('name', 'Unknown')
        mpd = (pb.get('mpd') or {}).get('auto', 'Not found')
        print(f"\n📺 Channel Name: {name}")
        print(f"📁 MPD URL: {mpd[:100]}..." if len(mpd) > 100 else f"📁 MPD URL: {mpd}")
        print("\n✅ DEBUG COMPLETE - CHANNEL WORKING!")
        print(f"\n✅ SUCCESS! Channel {CHANNEL_ID} is working!")
    else:
        print(f"❌ FAILED! HTTP {response.status_code}")
        print(f"📄 Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🔍 DEBUG COMPLETE")
print("=" * 60)
