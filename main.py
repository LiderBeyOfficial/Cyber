import logging
import json
import random
import os
import datetime
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes

# --- KİMLİK VE AYARLAR ---
TOKEN = "7781681396:AAHuxAKBs6mKtO2E_MDc5cLSbdAk5TeE5DI"
ADMIN_ID = 7979504487

# 3 ZORUNLU KANAL LİSTESİ
KANALLAR = [
    ("📢 Duyuru Kanalı", "https://t.me/LBduyuru", "@LBduyuru"),
    ("💬 Sohbet Grubu", "https://t.me/LiderBeyChat", "@LiderBeyChat"),
    ("🛡️ Güvence Kanalı", "https://t.me/lbguvence", "@lbguvence")
]

DB_FILE = "liderbey_empire_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {"users": {}, "live_log": "Lider Bey Sistemi Aktif! 👑"}
    return {"users": {}, "live_log": "Lider Bey Sistemi Aktif! 👑"}

def save_data():
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

data = load_data()

# --- MARKET VERİLERİ (ASLA KISALTILMADI - TEK TEK TÜM PAKETLER) ---
MARKET_DATA = {
    "INSTA": {
        "TAKİPÇİ": {
            "it100": ("100 Takipçi", 1000, "user"),
            "it200": ("200 Takipçi", 2000, "user"),
            "it300": ("300 Takipçi", 2700, "user"),
            "it400": ("400 Takipçi", 3200, "user"),
            "it500": ("500 Takipçi", 4000, "user"),
            "it1000": ("1000 Takipçi", 8000, "user"),
            "it5000": ("5000 Takipçi", 40000, "user")
        },
        "BEĞENİ": {
            "ib100": ("100 Beğeni", 300, "link"),
            "ib200": ("200 Beğeni", 600, "link"),
            "ib300": ("300 Beğeni", 900, "link"),
            "ib400": ("400 Beğeni", 1200, "link"),
            "ib500": ("500 Beğeni", 1500, "link"),
            "ib1000": ("1000 Beğeni", 3000, "link"),
            "ib5000": ("5000 Beğeni", 15000, "link")
        },
        "YORUM": {
            "iy10": ("10 Yorum", 1000, "link"),
            "iy20": ("20 Yorum", 2000, "link"),
            "iy30": ("30 Yorum", 3000, "link"),
            "iy40": ("40 Yorum", 4000, "link"),
            "iy50": ("50 Yorum", 5000, "link")
        }
    },
    "YT": {
        "ABONE": {
            "ya25": ("25 Abone", 1000, "yt_channel"),
            "ya50": ("50 Abone", 2000, "yt_channel"),
            "ya100": ("100 Abone", 3000, "yt_channel")
        },
        "İZLENME": {
            "yi1000": ("1000 İzlenme", 1000, "yt_video"),
            "yi2000": ("2000 İzlenme", 2000, "yt_video"),
            "yi3000": ("3000 İzlenme", 3000, "yt_video"),
            "yi5000": ("5000 İzlenme", 5000, "yt_video")
        },
        "BEĞENİ": {
            "yb25": ("25 Beğeni", 1000, "yt_video"),
            "yb50": ("50 Beğeni", 1500, "yt_video"),
            "yb100": ("100 Beğeni", 2500, "yt_video")
        }
    }
}

# --- YARDIMCI SİSTEMLER ---
def get_u(uid):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {
            'stars': 100, 
            'refs': 0, 
            'step': None, 
            'temp': {}, 
            'last_gift': None
        }
    return data["users"][uid]

async def check_all_subs(uid, context):
    for name, url, username in KANALLAR:
        try:
            member = await context.bot.get_chat_member(chat_id=username, user_id=uid)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

def main_menu_kb(uid):
    kb = [
        [InlineKeyboardButton(f"📡 {data['live_log']}", callback_data="none")],
        [InlineKeyboardButton("🛍 MARKET", callback_data="btn_market"), InlineKeyboardButton("👤 PROFİL", callback_data="btn_profil")],
        [InlineKeyboardButton("🎰 SLOT (50⭐)", callback_data="btn_slot"), InlineKeyboardButton("🎡 ÇARK (20⭐)", callback_data="btn_cark")],
        [InlineKeyboardButton("⚔️ DÜELLO", callback_data="btn_duel"), InlineKeyboardButton("🎫 LOTO", callback_data="btn_loto")],
        [InlineKeyboardButton("🎁 GÜNLÜK HEDİYE", callback_data="btn_gift"), InlineKeyboardButton("🔑 KOD GİR", callback_data="btn_kod")],
        [InlineKeyboardButton("🔗 REFERANS", callback_data="btn_ref"), InlineKeyboardButton("🎫 DESTEK", callback_data="btn_destek")]
    ]
    if int(uid) == ADMIN_ID:
        kb.append([InlineKeyboardButton("👑 ADMİN PANELİ", callback_data="btn_admin")])
    return InlineKeyboardMarkup(kb)

# --- BOT ANA FONKSİYONLARI ---
async def start(update, context):
    uid = update.effective_user.id; u = get_u(uid)
    if not await check_all_subs(uid, context):
        btn = [[InlineKeyboardButton(n, url=url)] for n, url, user in KANALLAR]
        btn.append([InlineKeyboardButton("✅ Tümüne Katıldım", callback_data="check_subs")])
        await update.message.reply_text(
            "🚨 **DUR YOLCU!**\n\nSisteme giriş yapabilmek için 3 sponsorumuza da katılmalısın.",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    await update.message.reply_text(
        "👑 **Lider Bey İmparatorluğuna Hoş Geldin!**\n\nMenüden seçim yaparak başlayabilirsin.",
        reply_markup=main_menu_kb(uid)
    )

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; uid = q.from_user.id; u = get_u(uid)
    
    # Butonun basıldığını Telegram'a bildir (Tepkisizliği çözer)
    await q.answer()

    if q.data == "check_subs":
        if await check_all_subs(uid, context):
            await q.message.edit_text("✅ Hoş geldin kanka!", reply_markup=main_menu_kb(uid))
        else:
            await q.answer("❌ Kanallardan biri hala eksik!", show_alert=True)
        return

    # Kanalsız işlem engeli
    if not await check_all_subs(uid, context):
        await q.answer("⚠️ Önce kanallara katıl!", show_alert=True); return

    # --- MARKET DALLANMASI ---
    if q.data == "btn_market":
        kb = [
            [InlineKeyboardButton("📸 İNSTAGRAM", callback_data="plt_INSTA"), InlineKeyboardButton("🎥 YOUTUBE", callback_data="plt_YT")],
            [InlineKeyboardButton("🎵 TİKTOK", callback_data="plt_TT")],
            [InlineKeyboardButton("🏠 ANA MENÜ", callback_data="go_home")]
        ]
        await q.edit_message_text("🛍 **Bir Platform Seç:**", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data == "plt_TT":
        await q.answer("Tiktok hizmetleri yakında!", show_alert=True)

    elif q.data.startswith("plt_"):
        plt = q.data.split("_")[1]
        kb = [[InlineKeyboardButton(k, callback_data=f"cat_{plt}_{k}")] for k in MARKET_DATA[plt].keys()]
        kb.append([InlineKeyboardButton("⬅️ GERİ", callback_data="btn_market")])
        await q.edit_message_text(f"🛍 **{plt} Kategorileri:**", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("cat_"):
        _, plt, cat = q.data.split("_")
        kb = [[InlineKeyboardButton(f"{v[0]} - {v[1]}⭐", callback_data=f"buy_{k}")] for k, v in MARKET_DATA[plt][cat].items()]
        kb.append([InlineKeyboardButton("⬅️ GERİ", callback_data=f"plt_{plt}")])
        await q.edit_message_text(f"🛍 **{cat} Paket Listesi:**", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("buy_"):
        pid = q.data.split("_")[1]; p_info = None
        for p in MARKET_DATA.values():
            for c in p.values():
                if pid in c: p_info = c[pid]
        
        if u['stars'] < p_info[1]:
            await q.edit_message_text(f"❌ **Bakiye Yetersiz!**\nFiyat: {p_info[1]}⭐\nSende: {u['stars']}⭐", reply_markup=main_menu_kb(uid))
            return
        
        u['temp'] = {'pid': pid, 'price': p_info[1], 'name': p_info[0], 'type': p_info[2]}
        kb = [[InlineKeyboardButton("✅ ONAYLA", callback_data="sip_onay"), InlineKeyboardButton("❌ İPTAL", callback_data="go_home")]]
        await q.edit_message_text(f"❓ **{p_info[0]}** onaylıyor musun?\nÜcret: {p_info[1]}⭐", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data == "sip_onay":
        u['step'] = "get_target"
        await q.edit_message_text("📸 **Kullanıcı adı veya link girin:**")

    elif q.data == "btn_slot":
        if u['stars'] < 50: await q.answer("❌ 50⭐ lazım!", show_alert=True); return
        u['stars'] -= 50; win = random.choices([0, 150, 400], weights=[70, 20, 10])[0]
        u['stars'] += win; save_data()
        await q.edit_message_text(f"🎰 **Slot Sonucu:** {win}⭐ kazandın!\nBakiye: {u['stars']}⭐", reply_markup=main_menu_kb(uid))

    elif q.data == "btn_profil":
        await q.edit_message_text(f"👤 **PROFİL**\n\nID: `{uid}`\nBakiye: **{u['stars']}⭐**\nRef: **{u['refs']}**", reply_markup=main_menu_kb(uid))

    elif q.data == "go_home":
        await q.edit_message_text("🏠 Ana Menü", reply_markup=main_menu_kb(uid))

# --- MESAJ YAZMA ---
async def message_handler(update, context):
    uid = update.effective_user.id; u = get_u(uid); text = update.message.text
    
    if u['step'] == "get_target":
        u['temp']['target'] = text; u['step'] = "get_note"
        await update.message.reply_text("📝 **Sipariş Notu Yazın:**")

    elif u['step'] == "get_note":
        u['stars'] -= u['temp']['price']; save_data()
        data['live_log'] = f"@{update.effective_user.username} {u['temp']['name']} aldı! ✅"
        
        adm_msg = (f"🚀 **YENİ SİPARİŞ!**\n\n👤 Kullanıcı: @{update.effective_user.username} ({uid})\n"
                   f"📦 Paket: {u['temp']['name']}\n🔗 Hedef: `{u['temp']['target']}`\n📝 Not: {text}")
        
        await context.bot.send_message(ADMIN_ID, adm_msg)
        await update.message.reply_text("✅ **Sipariş Alındı!**", reply_markup=main_menu_kb(uid))
        u['step'] = None

async def admin_panel_cmd(update, context):
    if update.effective_user.id != ADMIN_ID: return
    t = update.message.text
    if t.startswith("/gonderildi"):
        tid = t.split()[1]
        await context.bot.send_message(tid, "👑 Paketiniz başarıyla gönderilmiştir!")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.COMMAND, admin_panel_cmd))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot Termux/Pella için hazır...")
    app.run_polling()
