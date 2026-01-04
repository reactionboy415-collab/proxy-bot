import telebot
import requests
import io
import concurrent.futures
import time
import threading
import os
from telebot import types
from flask import Flask, request, Response, render_template_string

# --- CONFIGURATION & SECURITY ---
BOT_TOKEN = "7567299248:AAET-Xslbcqhrb432hOWWVxH_57NiylPwkg"
ADMIN_ID = 7840042951
ADMIN_USERNAME = "@dev2dex"
MAX_LIMIT = 5000
OFFICIAL_URL = "https://proxy-bot-g34t.onrender.com"
SUPABASE_URL = "https://vwmhbpgwhfwuwtattset.supabase.co/functions/v1/fetch-proxies"

bot = telebot.TeleBot(BOT_TOKEN)

# AUTHENTICATION TOKENS
tokens = {
    "auth": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImYyZTIyZWFhLTRhYjQtNDZhOC1hYzM3LTExYzA3YWQyNTgzNCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Z3bWhicGd3aGZ3dXd0YXR0c2V0LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI1ZmM0NTA3ZS00NTI2LTQ2OGItYjFkMi01YmVlOTZkNmQwMTEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY3NDA0Nzg0LCJpYXQiOjE3Njc0MDExODQsImVtYWlsIjoiamhvbmRlb0BnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiamhvbmRlb0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiSm9obiBkb2UiLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6IjVmYzQ1MDdlLTQ1MjYtNDY4Yi1iMWQyLTViZWU5NmQ2ZDAxMSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY3NDAxMTg0fV0sInNlc3Npb25faWQiOiI4MzkzYWU2Zi0zYTJlLTQ0ZDUtYjg1ZS1lYWEwMzQwNDdhYWEiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.ijYObw_fffHDtEIw3PPKqDyDW6StUn3NkaofNcfTakA5KMCwuzmW6UQq2_mSxfu5PHejh1xUNLQWQCH6weidjQ",
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3bWhicGd3aGZ3dXd0YXR0c2V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjczMjc0NjYsImV4cCI6MjA4MjkwMzQ2Nn0.LSMD2P4whDzoIW4UCig0ly0j6UOxd5fHhIkUhywnmrg",
}

user_data = {}

# MULTI-SOURCE DATABASE REGISTRY
DB_SOURCES = {
    "http": [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    ],
    "socks4": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt"
    ],
    "socks5": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    ]
}

# --- FLASK ENTERPRISE DASHBOARD ---
app = Flask(__name__)

DASHBOARD_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxy Hub v9.0 | API Control</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #0d1117; color: #c9d1d9; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { background: #161b22; padding: 40px; border-radius: 12px; border: 1px solid #30363d; width: 400px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; }
        h1 { color: #58a6ff; font-size: 24px; margin-bottom: 10px; }
        label { display: block; text-align: left; margin: 15px 0 5px; font-size: 14px; color: #8b949e; }
        select, input { width: 100%; padding: 10px; background: #0d1117; border: 1px solid #30363d; color: white; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #238636; color: white; border: none; border-radius: 6px; font-weight: bold; margin-top: 20px; cursor: pointer; transition: 0.2s; }
        button:hover { background: #2ea043; transform: scale(1.02); }
        .result-box { margin-top: 25px; padding: 15px; background: #010409; border-radius: 6px; font-family: monospace; color: #7ee787; font-size: 12px; word-break: break-all; border: 1px dashed #30363d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💎 Proxy Hub v9.0</h1>
        <p>Advanced API Endpoint Generator</p>
        <label>Protocol</label>
        <select id="proto"><option value="http">HTTP</option><option value="socks4">SOCKS4</option><option value="socks5">SOCKS5</option></select>
        <label>Speed Mode</label>
        <select id="mode"><option value="raw">🚀 Raw Flash (Bulk)</option><option value="verified">🛡️ Verified (Stable)</option></select>
        <label>Limit</label>
        <input type="number" id="qty" value="50" max="1000">
        <button onclick="generate()">Generate Master API Link</button>
        <div id="result" class="result-box">Endpoint will appear here...</div>
    </div>
    <script>
        function generate() {
            let p = document.getElementById('proto').value;
            let m = document.getElementById('mode').value;
            let q = document.getElementById('qty').value;
            let link = window.location.origin + '/api/' + m + '?type=' + p + '&qty=' + q;
            document.getElementById('result').innerText = link;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(DASHBOARD_UI)

@app.route('/api/raw')
def api_raw():
    proto = request.args.get('type', 'http')
    qty = int(request.args.get('qty', 100))
    sources = DB_SOURCES.get(proto, [])
    raw_list = fetch_from_backup(sources[0])
    return Response("\n".join(raw_list[:qty]), mimetype='text/plain')

@app.route('/api/verified')
def api_verified():
    proto = request.args.get('type', 'http')
    qty = int(request.args.get('qty', 10))
    if qty > 50: qty = 50
    sources = DB_SOURCES.get(proto, [])
    pool = fetch_from_backup(sources[0])[:150]
    verified = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(verify_node, p, proto) for p in pool]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res: verified.append(res.split(' | ')[0])
            if len(verified) >= qty: break
    return Response("\n".join(verified), mimetype='text/plain')

# --- CORE PROCESSING ENGINES ---
def fetch_cr_supabase(limit):
    headers = {"authorization": f"Bearer {tokens['auth']}", "apikey": tokens['apikey'], "content-type": "application/json"}
    try:
        r = requests.post(SUPABASE_URL, headers=headers, json={"limit": limit}, timeout=10)
        data = r.json()
        proxies = [f"{p['ip']}:{p['port']}" for p in data.get("proxies", [])]
        return proxies, data.get("totalAvailable", 0)
    except: return [], 0

def fetch_from_backup(url):
    try:
        r = requests.get(url, timeout=7)
        return [l.strip() for l in r.text.splitlines() if ":" in l]
    except: return []

def verify_node(addr, protocol):
    try:
        p_url = f"{protocol}://{addr}"
        start = time.time()
        r = requests.get("http://www.google.com", proxies={"http": p_url, "https": p_url}, timeout=3.0)
        if r.status_code == 200:
            lat = int((time.time() - start) * 1000)
            return f"{addr} | {lat}ms"
    except: pass
    return None

# --- TELEGRAM COMMAND CENTER ---
@bot.message_handler(commands=['start'])
def welcome(message):
    _, total = fetch_cr_supabase(1)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Request Proxies ⚡', 'API Access 🔑')
    bot.send_message(message.chat.id, 
        f"💎 **Proxy Hub Premium v9.0**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛰 **Active Nodes:** `{total if total > 0 else 'Global Pool'}`\n"
        f"🛡 **System:** `Anti-Ban Protected`\n"
        f"⚡ **Host:** `proxy-bot-g34t.onrender.com`\n"
        f"━━━━━━━━━━━━━━━━━━━━", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == 'API Access 🔑')
def show_api(message):
    bot.send_message(message.chat.id, 
        f"🔑 **Enterprise API Gateway**\n\n"
        f"Generate ultra-fast endpoints for your software and websites.\n\n"
        f"🌐 **Official Panel:**\n`{OFFICIAL_URL}`\n\n"
        f"Click the link to generate your unique Raw or Verified URL.", 
        disable_web_page_preview=True, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == 'Request Proxies ⚡')
def ask_qty(message):
    msg = bot.send_message(message.chat.id, "🔢 **Enter Extraction Quantity (Max 5000):**")
    bot.register_next_step_handler(msg, handle_qty)

def handle_qty(message):
    if not message.text.isdigit(): return
    user_data[message.chat.id] = {"qty": int(message.text)}
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(types.InlineKeyboardButton("HTTP", callback_data='p_http'),
               types.InlineKeyboardButton("SOCKS4", callback_data='p_socks4'),
               types.InlineKeyboardButton("SOCKS5", callback_data='p_socks5'))
    bot.send_message(message.chat.id, "🌐 **Select Protocol Selection:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def process_extraction(call):
    proto = call.data.replace('p_', '')
    target = user_data[call.message.chat.id]['qty']
    status = bot.edit_message_text(f"🚀 **Batch Testing {proto.upper()}...**", call.message.chat.id, call.message.message_id)
    
    verified = []
    sources = DB_SOURCES.get(proto, [])
    
    # Priority Fetching
    pool = []
    if proto == "http":
        sp_proxies, _ = fetch_cr_supabase(target * 5)
        pool.extend(sp_proxies)
    
    for src in sources:
        pool.extend(fetch_from_backup(src))
        if len(pool) > 1000: break

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        futures = [ex.submit(verify_node, p, proto) for p in pool[:800]]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                verified.append(res)
                if len(verified) % 10 == 0:
                    try:
                        bot.edit_message_text(f"🚀 **Live Tracking v9.0**\n━━━━━━━━━━━━\n✅ Verified: `{len(verified)}/{target}`\n🔎 Engine: `CR Parallel-Scan`", call.message.chat.id, status.message_id, parse_mode="Markdown")
                    except: pass
            if len(verified) >= target: break

    if verified:
        output = "\n".join(verified[:target])
        if len(verified) > 20:
            buf = io.BytesIO(output.encode()); buf.name = f"{proto}_cr_v9.txt"
            bot.send_document(call.message.chat.id, buf, caption=f"✅ **{proto.upper()} Extraction Complete**")
            bot.delete_message(call.message.chat.id, status.message_id)
        else:
            bot.edit_message_text(f"✅ **Verified {proto.upper()} Nodes:**\n\n`{output}`", call.message.chat.id, status.message_id, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ Zero active nodes found. Engine refreshing...", call.message.chat.id, status.message_id)

# --- STARTUP ENGINE ---
if __name__ == "__main__":
    # Handle Render Port Binding
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False), daemon=True).start()
    
    print(f"💎 Proxy Hub v9.0 | Host: {OFFICIAL_URL} | Port: {port}")
    bot.infinity_polling()
