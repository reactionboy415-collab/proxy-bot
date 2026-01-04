import telebot
import requests
import io
import concurrent.futures
import time
import threading
from telebot import types
from flask import Flask

# --- CONFIGURATION ---
BOT_TOKEN = "7567299248:AAET-Xslbcqhrb432hOWWVxH_57NiylPwkg"
ADMIN_ID = 7840042951
ADMIN_USERNAME = "@dev2dex"
MAX_LIMIT = 5000
SUPABASE_URL = "https://vwmhbpgwhfwuwtattset.supabase.co/functions/v1/fetch-proxies"

bot = telebot.TeleBot(BOT_TOKEN)

# FIXED SYNTAX - Clean single string
tokens = {
    "auth": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImYyZTIyZWFhLTRhYjQtNDZhOC1hYzM3LTExYzA3YWQyNTgzNCIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Z3bWhicGd3aGZ3dXd0YXR0c2V0LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI1ZmM0NTA3ZS00NTI2LTQ2OGItYjFkMi01YmVlOTZkNmQwMTEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY3NDA0Nzg0LCJpYXQiOjE3Njc0MDExODQsImVtYWlsIjoiamhvbmRlb0BnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiamhvbmRlb0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiSm9obiBkb2UiLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6IjVmYzQ1MDdlLTQ1MjYtNDY4Yi1iMWQyLTViZWU5NmQ2ZDAxMSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY3NDAxMTg0fV0sInNlc3Npb25faWQiOiI4MzkzYWU2Zi0zYTJlLTQ0ZDUtYjg1ZS1lYWEwMzQwNDdhYWEiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.ijYObw_fffHDtEIw3PPKqDyDW6StUn3NkaofNcfTakA5KMCwuzmW6UQq2_mSxfu5PHejh1xUNLQWQCH6weidjQ",
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ3bWhicGd3aGZ3dXd0YXR0c2V0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjczMjc0NjYsImV4cCI6MjA4MjkwMzQ2Nn0.LSMD2P4whDzoIW4UCig0ly0j6UOxd5fHhIkUhywnmrg",
}

user_data = {}

# --- ENHANCED TRUSTED DATABASES ---
DB_SOURCES = {
    "http": [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
    ],
    "socks4": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt"
    ],
    "socks5": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5"
    ]
}

# --- RENDER HEALTH CHECK SERVER ---
app = Flask(__name__)
@app.route('/')
def health(): return "Proxy Hub Alive", 200
def run_web(): app.run(host='0.0.0.0', port=10000)

# --- CORE ENGINES ---
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
        if r.status_code == 200:
            return [line.strip() for line in r.text.splitlines() if ":" in line]
    except: return []
    return []

def verify_node(addr, protocol):
    try:
        proxies = {"http": f"{protocol}://{addr}", "https": f"{protocol}://{addr}"}
        start = time.time()
        r = requests.get("http://www.google.com", proxies=proxies, timeout=3.0)
        latency = int((time.time() - start) * 1000)
        
        if r.status_code == 200:
            try:
                ip_only = addr.split(':')[0]
                geo = requests.get(f"http://ip-api.com/json/{ip_only}?fields=countryCode", timeout=1.2).json()
                country = geo.get("countryCode", "??")
            except: country = "??"
            return f"{addr} | {country} | {latency}ms"
    except: pass
    return None

# --- TELEGRAM HANDLERS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    _, total = fetch_cr_supabase(1)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Request Proxies ⚡')
    bot.send_message(message.chat.id, 
        f"💎 **Proxy Hub Premium v8.5**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 **Global Pool:** `{total if total > 0 else 'Online'}` Nodes\n"
        f"📡 **Main DB:** `CR Supabase` (Active)\n"
        f"🛰 **Backup DB:** `CR Cloud + GitHub` (Active)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Powered by CR Infrastructure", 
        reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == 'Request Proxies ⚡')
def ask_qty(message):
    msg = bot.send_message(message.chat.id, f"🔢 **Enter Quantity (Max {MAX_LIMIT}):**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, handle_qty)

def handle_qty(message):
    if not message.text.isdigit(): return
    user_data[message.chat.id] = {"qty": int(message.text)}
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("HTTP", callback_data='p_http'),
        types.InlineKeyboardButton("SOCKS4", callback_data='p_socks4'),
        types.InlineKeyboardButton("SOCKS5", callback_data='p_socks5')
    )
    bot.send_message(message.chat.id, "🌐 **Select Protocol:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('p_'))
def start_processing(call):
    chat_id = call.message.chat.id
    protocol = call.data.replace('p_', '')
    target = user_data[chat_id]['qty']
    
    status_msg = bot.edit_message_text(
        f"🔄 **Batch Processing {protocol.upper()}...**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Target: `{target}`\n"
        f"━━━━━━━━━━━━━━━━━━━━", chat_id, call.message.message_id, parse_mode="Markdown")

    final_verified = []
    scanned_total = 0
    
    # POWER BATCH ENGINE
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        sources = DB_SOURCES.get(protocol, [])
        fetch_tasks = [executor.submit(fetch_from_backup, url) for url in sources]
        
        # Add Supabase as primary if HTTP
        if protocol == "http":
            fetch_tasks.append(executor.submit(fetch_cr_supabase, target * 10))
        
        for future in concurrent.futures.as_completed(fetch_tasks):
            res = future.result()
            raw_list = res[0] if isinstance(res, tuple) else res
            if not raw_list: continue

            # Test this source immediately (Batch Logic)
            test_tasks = [executor.submit(verify_node, p, protocol) for p in raw_list[:500]]
            
            for test_future in concurrent.futures.as_completed(test_tasks):
                node = test_future.result()
                scanned_total += 1
                if node:
                    final_verified.append(node)
                    if len(final_verified) % 10 == 0 or len(final_verified) == target:
                        try:
                            bot.edit_message_text(
                                f"🚀 **Live Verification Tracking**\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"✅ **Verified:** `{len(final_verified)}/{target}`\n"
                                f"🔎 **Scanned:** `{scanned_total}` Nodes\n"
                                f"━━━━━━━━━━━━━━━━━━━━", 
                                chat_id, status_msg.message_id, parse_mode="Markdown")
                        except: pass
                
                if len(final_verified) >= target: break
            if len(final_verified) >= target: break

    if final_verified:
        output_text = "\n".join(final_verified[:target])
        if target > 20:
            buf = io.BytesIO(output_text.encode()); buf.name = f"cr_{protocol}.txt"
            bot.send_document(chat_id, buf, caption=f"✅ **Target Reached ({protocol.upper()})**")
            bot.delete_message(chat_id, status_msg.message_id)
        else:
            bot.edit_message_text(f"✅ **Latest {protocol.upper()} Nodes:**\n\n`{output_text}`", chat_id, status_msg.message_id, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ No responsive nodes found. Try another protocol.", chat_id, status_msg.message_id)

# --- EXECUTION ---
if __name__ == "__main__":
    # Start Render Health check in background
    threading.Thread(target=run_web, daemon=True).start()
    print("💎 Proxy Hub v8.5 is Running...")
    bot.infinity_polling()