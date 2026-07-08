#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamFlex19 | JioTV+ Auto Fetcher
- 100% GitHub Secrets - Kuch bhi hardcode nahi
- Exact category mapping from category_mapping.txt
"""

import os
import requests
import re
import json
import time
import random
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ── ALL VALUES FROM GITHUB SECRETS ──────────────────────────────────────────
ACCESS_TOKEN = os.environ.get('JIOTV_TOKEN', '')
CLEARKEY_URL = os.environ.get('CLEARKEY_URL', '')
JIO_API_BASE = os.environ.get('JIO_API_BASE', '')
JIO_SUB_ID = os.environ.get('JIO_SUB_ID', '')
JIO_RMN = os.environ.get('JIO_RMN', '')
JIO_API_SIG = os.environ.get('JIO_API_SIG', '')
JIO_FEATURE_CODE = os.environ.get('JIO_FEATURE_CODE', '')

# ── DEBUG ──────────────────────────────────────────────────────────────────
print("=== DEBUG: Checking Secrets ===")
print(f"JIOTV_TOKEN set: {'Yes' if ACCESS_TOKEN else 'NO!'}")
print(f"CLEARKEY_URL: {CLEARKEY_URL}")
print(f"JIO_API_BASE: {JIO_API_BASE}")
print(f"JIO_SUB_ID: {JIO_SUB_ID}")
print(f"JIO_RMN set: {'Yes' if JIO_RMN else 'NO!'}")
print(f"JIO_API_SIG set: {'Yes' if JIO_API_SIG else 'NO!'}")
print(f"JIO_FEATURE_CODE set: {'Yes' if JIO_FEATURE_CODE else 'NO!'}")
print("==============================")

# ── CHECK ──────────────────────────────────────────────────────────────────
MISSING = []
if not ACCESS_TOKEN: MISSING.append('JIOTV_TOKEN')
if not CLEARKEY_URL: MISSING.append('CLEARKEY_URL')
if not JIO_API_BASE: MISSING.append('JIO_API_BASE')
if not JIO_SUB_ID: MISSING.append('JIO_SUB_ID')
if not JIO_RMN: MISSING.append('JIO_RMN')
if not JIO_API_SIG: MISSING.append('JIO_API_SIG')
if not JIO_FEATURE_CODE: MISSING.append('JIO_FEATURE_CODE')

if MISSING:
    print(f"❌ Missing Secrets: {', '.join(MISSING)}")
    exit(1)
else:
    print("✅ All secrets loaded successfully!")

# ── CONFIG ──────────────────────────────────────────────────────────────────
OUTPUT_M3U = "streamflex_fresh.m3u"
OUTPUT_JSON = "streamflex_channels.json"
WATERMARK = "@StreamFlex19"
MAX_WORKERS = 5
RETRIES = 2
RETRY_W = 3
UA = "JioTV.Plus/2.3.1_2041 (Linux;Android 14) AndroidXMedia3/1.4.0"

# ── CATEGORY MAP ────────────────────────────────────────────────────────────
CATEGORY_MAP = {
    "CNBC TV18": "Business News",
    "CNBC TV18 Prime HD": "Business News",
    "CNBC Awaaz": "Business News",
    "NDTV Profit": "Business News",
    "ET Now": "Business News",
    "ET Now Swadesh": "Business News",
    "Zee Business": "Business News",
    "Aastha": "Devotional",
    "Sanskar": "Devotional",
    "Sadhna TV": "Devotional",
    "DD National": "Entertainment",
    "DD India": "Entertainment",
    "Zee TV": "Entertainment",
    "Star Plus": "Entertainment",
    "Colors": "Entertainment",
    "Sony": "Entertainment",
    "History TV18 HD": "Infotainment",
    "Discovery": "Infotainment",
    "Animal Planet": "Infotainment",
    "Nat Geo": "Infotainment",
    "Pogo": "Kids",
    "Cartoon Network": "Kids",
    "Nick": "Kids",
    "Disney": "Kids",
    "TravelXP": "Lifestyle",
    "TLC": "Lifestyle",
    "Food Food": "Lifestyle",
    "Star Gold": "Movies",
    "Zee Cinema": "Movies",
    "Sony MAX": "Movies",
    "MTV": "Music",
    "9XM": "Music",
    "Zing": "Music",
    "ABP News": "News",
    "Aaj Tak": "News",
    "India TV": "News",
    "NDTV": "News",
    "Times Now": "News",
    "Republic": "News",
    "DD Sports": "Sports",
    "Star Sports": "Sports",
    "Sony Sports Ten": "Sports",
}

def get_category(channel_name):
    name = channel_name.strip().lower()
    for key, cat in CATEGORY_MAP.items():
        if key.lower() in name or name in key.lower():
            return cat
    return 'Others'

def jio_headers(did, uid):
    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'deviceId': did,
        'subId': JIO_SUB_ID,
        'uniqueid': uid,
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

def jio_payload(did):
    return {
        'bitrateProfile': 'xxhdpi',
        'model': 'Mi TV 4A',
        'manufacturer': 'Xiaomi',
        'osVersion': '15',
        'serialNo': did,
        'is4kSupport': True,
        'hevcSupport': True,
        'dolbySupport': True,
        'appVersion': '2.6.4_2076',
        'deviceType': 'androidtv',
        'drmSupport': 'widevine',
    }

def rh(n): return ''.join(random.choices('0123456789abcdef', k=n))
def make_did(): return rh(16)
def make_uid(): return f"{rh(8)}-{rh(4)}-{rh(4)}-{rh(4)}-{rh(12)}"
def log(m): print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", flush=True)

# ── CHANNEL IDS ──────────────────────────────────────────────────────────
CHANNEL_IDS = [
    300000, 300001, 300002, 300003, 300004, 300005, 300006, 300007, 300008, 300009,
    300011, 300012, 300013, 300014, 300017, 300018, 300019, 300020, 300021, 300022,
    300023, 300024, 300025, 300026, 300027, 300028, 300029, 300030, 300031, 300032,
    300033, 300034, 300035, 300036, 300037, 300038, 300039, 300041, 300043, 300044,
    300045, 300046, 300047, 300048, 300049, 300050, 300051, 300052, 300053, 300054,
    300055, 300056, 300057, 300061, 300063, 300066, 300067, 300068, 300070, 300071,
    300072, 300073, 300074, 300075, 300077, 300079, 300080, 300081, 300083, 300084,
    300085, 300086, 300087, 300089, 300090, 300091, 300092, 300093, 300094, 300095,
    300096, 300098, 300100, 300101, 300102, 300103, 300105, 300106, 300107, 300108,
    300109, 300111, 300112, 300113, 300114, 300116, 300117, 300118, 300120, 300121,
    300124, 300125, 300126, 300127, 300128, 300129, 300131, 300132, 300133, 300134,
    300135, 300136, 300137, 300138, 300139, 300140, 300141, 300142, 300144, 300145,
    300146, 300148, 300149, 300150, 300151, 300152, 300153, 300154, 300156, 300157,
    300158, 300159, 300160, 300161, 300162, 300164, 300165, 300170, 300176, 300177,
    300178, 300179, 300180, 300181, 300186, 300205, 300206, 300207, 300208, 300209,
    300210, 300255, 300256, 300258, 300263, 300266, 300267, 300268, 300269, 300270,
    300273, 300275, 300277, 300278, 300279, 300280, 300281, 300284, 300286, 300288,
    300293, 300300, 300301, 300309, 300310, 300311, 300312, 300313, 300314, 300315,
    300318, 300320, 300322, 300323, 300325, 300327, 300328, 300330, 300332, 300336,
    300341, 300346, 300348, 300350, 300351, 300374, 300377, 300378, 300396, 300397,
    300428, 300443, 300451, 300453, 300455, 300458, 300459, 300488, 300507, 300508,
    300511, 300517, 300521, 300523, 300524, 300525, 300526, 300527, 300529, 300530,
    300531, 300532, 300533, 300534, 300535, 300536, 300537, 300538, 300539, 300540,
    300541, 300542, 300543, 300544, 300545, 300546, 300547, 300548, 300549, 300550,
    300551, 300552, 300553, 300555, 300556, 300557, 300558, 300561, 300562, 300563,
    300572, 300573, 300574, 300575, 300576, 300577, 300578, 300579, 300580, 300581,
    300582, 300583, 300584, 300585, 300586, 300587, 300588, 300603, 300605, 300609,
    300611, 300612, 300625, 300630, 300631, 300637, 301001, 301002, 301006, 301007,
    301009, 301016, 301017, 301018, 301020, 301022, 301023, 301024, 301026, 301027,
    301028, 301029, 301032, 301034, 301036, 301037, 301038, 301039, 301043, 301045,
    301046, 301048, 301049, 301050, 301051, 301052, 301053, 301055, 301056, 301057,
    301071, 301077, 301078, 301079, 301083, 301085, 301093, 301096, 301116, 301117,
    301118, 301119, 301120, 301124, 301125, 301128, 301129, 301133, 301135, 301136,
    301138, 301139, 301140, 301141, 301143, 301144, 301145, 301146, 301147, 301148,
    301149, 301150, 301151, 301155, 301160, 301163, 301164, 301165, 301166, 301167,
    301169, 301170, 301172, 301173, 301174, 301175, 301178, 301188, 301189, 301190,
    301191, 301192, 301194, 301196, 301198, 301199, 301201, 301202, 301204, 301205,
    301206, 301207, 301208, 301209, 301214, 301215, 301216, 301221, 301222, 301223,
    301224, 301225, 301228, 301229, 301233, 301234, 301235, 301236, 301237, 301239,
    301240, 301242, 301243, 301244, 301246, 301247, 301248, 301249, 301250, 301251,
    301252, 301253, 301255, 301256, 301257, 301260, 301262, 301266, 301267, 301268,
    301271, 301287, 301291, 301292, 301294, 301296, 301298, 301306, 301313, 301314,
    301316, 301318, 301319, 301321, 301322, 301325, 301326, 301327, 301336, 301337,
    301340, 301341, 301342, 301343, 301344, 301346, 301347, 301348, 301349, 301350,
    301351, 301352, 301354, 301355, 301356, 301357, 301358, 301361, 301363, 301364,
    301365, 301367, 301368, 301371, 301373, 301374, 301375, 301376, 301377, 301380,
    301381, 301382, 301383, 301384, 301385, 301386, 301389, 301394, 301395, 301396,
    301398, 301399, 301402, 301403, 301404, 301408, 301409, 301410, 301416, 301418,
    301419, 301421, 301422, 301424, 301426, 301427, 301428, 301430, 301431, 301434,
    301435, 301436, 301439, 301443, 301444, 301445, 301447, 301448, 301449, 301450,
    301451, 301452, 301456, 301457, 301458, 301460, 301461, 301462, 301463, 301464,
    301469, 301470, 301472, 301473, 301474, 301475, 301476, 301477, 301481, 301482,
    301483, 301484, 301486, 301488, 301489, 301499, 301500, 301501, 301502, 301504,
    301505, 301507, 301508, 301509, 301510, 301512, 301513, 301514, 301515, 301516,
    301517, 301518, 301524, 301525, 301526, 301527, 301528, 301529, 301543, 301544,
    301546, 301547, 301548, 301549, 301550, 301551, 301552, 301554, 301557, 301559,
    301560, 301564, 301566, 301567, 301570, 301571, 301572, 301574, 301575, 301576,
    301579, 301580, 301581, 301582, 301584, 301585, 301586, 301588, 301589, 301591,
    301594, 301596, 301597, 301598, 301601, 301606, 301607, 301608, 301609, 301610,
    301612, 301614, 301615, 301616, 301619, 301629, 301630, 301632, 301634, 301636,
    301637, 301648, 301650, 301651, 301652, 301653, 301654, 301660, 301661, 301662,
    301663, 301664, 301665, 301669, 301670, 301671, 301672, 301673, 301674, 301676,
    301677, 301679, 301680, 301682, 301683, 301684, 301685, 301686, 301687, 301689,
    301690, 301691, 301692, 301693, 301694, 301695, 301696, 301697, 301698, 301699,
    301700, 301701, 301702, 301703, 301704, 301705, 301706, 301709, 301710, 301715,
    301716, 301719, 301723, 301724, 301726, 301727, 301738, 301739, 301741, 301742,
    301748, 301749, 301750, 301751, 301755, 301756, 301757, 301758, 301763, 301764,
    301765, 301766, 301770, 301775, 301776, 301777, 301779, 301780, 301781, 301782,
    301784, 301785, 301786, 301787, 301789, 301790, 301792, 301793, 301794, 301797,
    301798, 301801, 301802, 301804, 301805, 301806, 301809, 301810, 301811, 301812,
    301813, 301814, 301816, 301817, 301818, 301822, 301823, 301824, 301825, 301826,
    301827, 301828, 301829, 301830, 301841, 301842, 301844, 301845, 301846, 301847,
    301851, 301852, 301858, 301861, 301865, 301867, 301868, 301869, 301870, 301871,
    301872, 301873, 301876, 301877, 301878, 301879, 301880, 301881, 301882, 301883,
    301884, 301885, 301886, 301887, 301888, 301889, 301890, 301891, 301894, 301895,
    301896, 301897, 301898, 301899, 301900, 301902, 301903, 301904, 301905, 301907,
    301909, 301910, 301911, 301912, 301913, 301915, 301916, 301917, 301919, 301920,
    301922, 301925, 301926, 301928, 301930, 301933, 301934, 301935, 301937, 301938,
    301940, 301941, 301942, 301945, 301947, 301948, 301950, 301951, 301952, 301958,
    301959, 301960, 301962, 301964, 301965, 301966, 301971, 301972, 301974, 301975,
    301977, 301978, 301980, 301981, 301982, 301983, 301984, 301985, 301986, 301988,
    301989, 301990, 301992, 301993, 301994, 301995, 301996, 301997, 301998, 302000,
    302001, 302059, 302060, 302061, 302062, 302064, 302065, 302066, 302067, 302068,
    302069, 302070, 302071, 302072, 302074, 302075, 302076, 302077, 302078, 302079,
    302080, 302081, 302082, 302083, 302084, 302085, 302086, 302087, 302088, 302089,
    302090, 302091, 302093, 302094, 302095, 302096, 302097, 302099, 302100, 302101,
    302102, 302103, 302104, 302105, 302106, 302108, 302109, 302110, 302111, 302112,
    302113, 302114, 302115, 302116, 302117, 302118, 302119, 302120, 302121, 302122,
    302123, 302124, 302125, 302126, 302128, 302130, 302133, 302135, 302136, 302137,
    302138, 302139, 302140, 302141, 302142, 302143, 302144, 302145, 302146, 302147,
    302148, 302149, 302150, 302151, 302152, 302153, 302154, 302155, 302156, 302157,
    302158, 302161, 302162, 302163, 302703, 302704, 302705, 302706, 302707, 302708,
    302709, 304002, 304003, 304004, 304005, 304006, 304007, 304008, 304009, 304010,
    304011, 304012, 304013, 304014, 304015, 304016, 304017, 304020, 304021, 304022,
    304024, 304026, 304028, 304029, 304030, 304031, 304032, 304033, 304034, 304036,
    304037, 304038, 304039, 304040, 304041, 304042, 304043, 304044, 304045, 304046,
    304048, 304049, 304050, 304051, 304052, 304054, 304055, 304056, 304057, 304058,
    304059, 304061, 304062, 304063, 304065, 304066, 304067, 304068, 304069, 304070,
    304071, 304072, 304073, 304074, 304075, 304076, 304077, 304078, 304079, 304080,
    304081, 304082, 304083, 304084, 304085, 304086, 304087, 304088, 304089, 304091,
    304092, 304099, 304100, 304101, 304102, 304103, 304104, 304105, 304106, 304107,
    304108, 304109, 304110, 304111, 304112, 304113, 304114, 304115, 304118, 304119,
    304120, 304121, 304123, 304124, 304128, 304129, 304130, 304131, 304132, 304134,
    304135, 304136, 304137, 304138, 304139, 304140, 304141, 304142, 304143, 304145,
    304146, 304147, 304148, 304149, 304150, 304152, 304153, 304154, 304155, 304156,
    304157, 304158, 304159, 304160, 304161, 304162, 304163, 304164, 304165, 304166,
    304167, 304168, 304169, 304170, 304171, 304172, 304173, 304174, 304175, 304176,
    304177, 304179, 304180, 304181, 304182, 304183, 304184, 304185, 304186, 304187,
    304188, 304189, 304190, 304191, 304192, 304194, 304196, 304197, 304198, 304199,
    304200, 304201, 304202, 304203, 304204, 304205, 304206, 304209, 304210, 304211,
    304212, 304214, 304216, 304219, 304221, 304222,
]

# ── FETCH CHANNEL ─────────────────────────────────────────────────────────
def fetch_channel(ch_id, session, did, uid):
    try:
        url = f"{JIO_API_BASE}/playback/v2/{ch_id}"
        headers = jio_headers(did, uid)
        payload = jio_payload(did)
        
        r = session.post(url, headers=headers, json=payload, timeout=15)

        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"

        data = r.json()
        pb = data.get('data', data)
        mpd_url = (pb.get('mpd') or {}).get('auto', '')
        
        if not mpd_url:
            return None, "No MPD"

        name = pb.get('name', f'Channel {ch_id}')
        logo = pb.get('images', '')
        vendor = pb.get('vendor') or pb.get('provider', 'Other')
        lang = pb.get('defaultLanguage', '')
        ext_id = pb.get('extID', '')
        tvg_id = ext_id if ext_id else re.sub(r'[^a-z0-9]', '', name.lower())
        mpd_base = re.sub(r'\?__hdnea__=.*', '', mpd_url)

        cat = get_category(name)
        if cat == 'Others':
            cat = get_category(vendor)

        # Fetch MPD for cookie
        mr = session.get(mpd_url, headers={'User-Agent': UA}, timeout=10)
        if mr.status_code != 200:
            return None, f"MPD HTTP {mr.status_code}"

        cookie = None
        m = re.search(r'__hdnea__=([^;]+)', mr.headers.get('Set-Cookie', ''))
        if m:
            cookie = m.group(1)
        if not cookie:
            m2 = re.search(r'__hdnea__=([^&\s]+)', mpd_url)
            if m2:
                cookie = m2.group(1)
        if not cookie:
            m3 = re.search(r'__hdnea__=([^&\s]+)', mr.url)
            if m3:
                cookie = m3.group(1)
        if not cookie:
            return None, "No cookie"

        exp_m = re.search(r'exp=(\d+)', cookie)
        expiry = datetime.fromtimestamp(int(exp_m.group(1))).strftime('%Y-%m-%d %H:%M:%S') if exp_m else None

        return {
            'channel_id': ch_id,
            'tvg_id': tvg_id,
            'name': name,
            'logo': logo,
            'group': cat,
            'language': lang,
            'mpd_base': mpd_base,
            'cookie': f'__hdnea__={cookie}',
            'cookie_expiry': expiry,
            'license_key': CLEARKEY_URL,
            'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }, None

    except Exception as e:
        return None, f"Error: {e}"

def m3u_entry(ch):
    return (
        f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-name="{ch["name"]}" '
        f'tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n'
        f'#KODIPROP:inputstream.adaptive.manifest_type=mpd\n'
        f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
        f'#KODIPROP:inputstream.adaptive.license_key={ch["license_key"]}\n'
        f'#EXTVLCOPT:http-user-agent={UA}\n'
        f'#EXTHTTP:{{"cookie":"{ch["cookie"]}"}}\n'
        f'{ch["mpd_base"]}'
    )

def save(entries, channels, success, failed, total, done=False):
    now = datetime.now(timezone.utc)

    with open(OUTPUT_M3U, 'w', encoding='utf-8') as f:
        f.write(
            f"#EXTM3U\n"
            f"# {WATERMARK}\n"
            f"# Generated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"# Total Channels: {success}\n"
            f"# License: {CLEARKEY_URL}\n\n"
            + '\n\n'.join(entries)
        )

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            'watermark': WATERMARK,
            'project': 'StreamFlex JioTV+ Channel Database',
            'license_url': CLEARKEY_URL,
            'generated_at': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'generated_ts': int(now.timestamp()),
            'status': 'complete' if done else 'in_progress',
            'total_requested': total,
            'success': success,
            'failed': failed,
            'channels': channels,
        }, f, indent=2, ensure_ascii=False)

def main():
    log('='*60)
    log(f'  {WATERMARK} | JioTV+ Auto Fetcher')
    log(f'  License URL: {CLEARKEY_URL}')
    log(f'  Total channels: {len(CHANNEL_IDS)}')
    log('='*60)

    session = requests.Session()
    did = make_did()
    uid = make_uid()
    entries = []
    channels = []
    success = failed = 0
    total = len(CHANNEL_IDS)
    lock = threading.Lock()
    processed = 0

    def process_channel(ch_id):
        nonlocal success, failed, processed
        result, err = fetch_channel(ch_id, session, did, uid)

        with lock:
            processed += 1
            if result:
                success += 1
                log(f'  ✅ [{processed}/{total}] {result["name"]} → {result["group"]}')
                entries.append(m3u_entry(result))
                channels.append(result)
            else:
                failed += 1
                log(f'  ❌ [{processed}/{total}] #{ch_id} — {err}')

            if processed % 50 == 0:
                save(entries, channels, success, failed, total)

        return result

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_channel, ch_id): ch_id for ch_id in CHANNEL_IDS}
        for future in as_completed(futures):
            pass

    save(entries, channels, success, failed, total, done=True)
    log('='*60)
    log(f'  ✅ DONE! {success} found | ❌ {failed} failed | Total: {total}')
    log('='*60)

if __name__ == '__main__':
    main()
