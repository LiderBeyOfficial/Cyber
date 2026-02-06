import logging
import json
import random
import os
import datetime
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes

# --- TEMEL AYARLAR ---
TOKEN = "7781681396:AAHuxAKBs6mKtO2E_MDc5cLSbdAk5TeE5DI"
ADMIN_ID = 7979504487

# ZORUNLU KANALLAR (3 ADET)
KANALLAR = [
    ("📢 Duyuru Kanalı", "https://t.me/LBduyuru", "@LBduyuru"),
    ("💬 Sohbet Grubu", "https://t.me/LiderBeyChat", "@LiderBeyChat"),
    ("🛡️ Güvence Kanalı", "https://t.me/lbguvence", "@lbguvence")
]

DB_FILE = "liderbey_empire_full_db.json"

# --- VERİ TABANI SİSTEMİ ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {"users": {}, "live_log": "Lider Bey Sistemi Aktif! 👑", "coupons": {}}
    return {"users": {}, "live_log": "Lider Bey Sistemi Aktif! 👑", "coupons": {}}

def save_data():
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# --- MARKET VERİLERİ (TEK TEK TÜM PAKETLER) ---
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
            "yi5000": ("5000 İzlenme", 5000, "yt_video")
        },
        "BEĞENİ": {
            "yb25": ("25 Beğeni", 1000, "yt_video"),
            "yb100": ("100 Beğeni", 2500, "yt_video")
        }
    }
}

# --- KULLANICI YÖNETİMİ ---
def get_u(uid):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {
            'stars': 100, 
            'refs': 0, 
            'step': None, 
            'temp': {}, 
            'last_gift': None,
            'is_vip': False
        }
    return data["users"][uid]

async def check_all_subs(uid, context):
    """Kullanıcının 3 kanalda olup olmadığını kontrol eder."""
    for name, url, username in KANALLAR:
        try:
            member = await context.bot.get_chat_member(chat_id=username, user_id=uid)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# --- KLAVYELER ---
def main_menu_kb(uid):
    kb = [
        [InlineKeyboardButton(f"📡 {data['live_log']}", callback_data="log_yok")],
        [InlineKeyboardButton("🛍 MARKET", callback_data="m_ana"), InlineKeyboardButton("👤 PROFİL", callback_data="p_gor")],
        [InlineKeyboardButton("🎰 SLOT (50⭐)", callback_data="g_slot"), InlineKeyboardButton("🎡 ÇARK (20⭐)", callback_data="g_cark")],
        [InlineKeyboardButton("⚔️ DÜELLO", callback_data="g_duel"), InlineKeyboardButton("🎫 LOTO", callback_data="g_loto")],
        [InlineKeyboardButton("🎁 GÜNLÜK HEDİYE", callback_data="h_gunluk"), InlineKeyboardButton("🔑 KOD GİR", callback_data="k_gir")],
        [InlineKeyboardButton("🔗 REF", callback_data="r_link"), InlineKeyboardButton("🎫 DESTEK", callback_data="d_ticket")]
    ]
    if int(uid) == ADMIN_ID:
        kb.append([InlineKeyboardButton("👑 LİDER PANELİ", callback_data="admin_p")])
    return InlineKeyboardMarkup(kb)

# --- ANA KOMUTLAR ---
async def start(update, context):
    uid = update.effective_user.id
    u = get_u(uid)
    
    if not await check_all_subs(uid, context):
        btns = [[InlineKeyboardButton(n, url=url)] for n, url, user in KANALLAR]
        btns.append([InlineKeyboardButton("✅ Tümüne Katıldım", callback_data="sub_check")])
        await update.message.reply_text(
            "🚨 **HOŞ GELDİN!**\n\nSistemi başlatabilmek için aşağıdaki 3 kanala katılman zorunludur.",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return
    
    await update.message.reply_text(
        "👑 **Lider Bey İmparatorluğu Aktif!**\n\nBurası senin krallığın. Aşağıdan işlem seçebilirsin.",
        reply_markup=main_menu_kb(uid)
    )

# --- BUTON YAKALAYICI (CALLBACK) ---
async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    u = get_u(uid)
    
    await query.answer() # Butonun dönmesini durdurur

    if query.data == "sub_check":
        if await check_all_subs(uid, context):
            await query.message.edit_text("✅ Kanallar onaylandı! Hoş geldin.", reply_markup=main_menu_kb(uid))
        else:
            await query.answer("❌ Kanallardan biri hala eksik kanka!", show_alert=True)
        return

    # Kanallar kontrolü her butonda devrede
    if not await check_all_subs(uid, context):
        await query.answer("🚨 Önce 3 kanala da katılmalısın!", show_alert=True)
        return

    # MARKET SİSTEMİ
    if query.data == "m_ana":
        kb = [
            [InlineKeyboardButton("📸 İNSTAGRAM", callback_data="pl_INSTA"), InlineKeyboardButton("🎥 YOUTUBE", callback_data="pl_YT")],
            [InlineKeyboardButton("🎵 TİKTOK (YAKINDA)", callback_data="plt_yok")],
            [InlineKeyboardButton("🏠 ANA MENÜ", callback_data="home_don")]
        ]
        await query.edit_message_text("🛍 **Platform seçiniz:**", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data.startswith("pl_"):
        plt = query.data.split("_")[1]
        kb = [[InlineKeyboardButton(k, callback_data=f"cat_{plt}_{k}")] for k in MARKET_DATA[plt].keys()]
        kb.append([InlineKeyboardButton("⬅️ GERİ", callback_data="m_ana")])
        await query.edit_message_text(f"🛍 **{plt} Hizmetleri:**", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data.startswith("cat_"):
        _, plt, cat = query.data.split("_")
        kb = [[InlineKeyboardButton(f"{v[0]} - {v[1]}⭐", callback_data=f"buy_{k}")] for k, v in MARKET_DATA[plt][cat].items()]
        kb.append([InlineKeyboardButton("⬅️ GERİ", callback_data=f"pl_{plt}")])
        await query.edit_message_text(f"🛍 **{cat} Paketleri:**", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data.startswith("buy_"):
        pid = query.data.split("_")[1]
        p_info = None
        for p in MARKET_DATA.values():
            for c in p.values():
                if pid in c: p_info = c[pid]
        
        if u['stars'] < p_info[1]:
            await query.edit_message_text(f"❌ **Yetersiz Bakiye!**\n\nPaket: {p_info[1]}⭐\nSenin: {u['stars']}⭐", reply_markup=main_menu_kb(uid))
            return
        
        u['temp'] = {'pid': pid, 'price': p_info[1], 'name': p_info[0], 'type': p_info[2]}
        kb = [[InlineKeyboardButton("✅ ONAYLA", callback_data="onay_sip"), InlineKeyboardButton("❌ İPTAL", callback_data="home_don")]]
        await query.edit_message_text(f"❓ **{p_info[0]}** onaylıyor musun?\n\nÜcret: {p_info[1]}⭐", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "onay_sip":
        u['step'] = "link_bekle"
        await query.edit_message_text("📸 Lütfen **Kullanıcı Adı veya Link** gönderin:")

    # OYUNLAR
    elif query.data == "g_slot":
        if u['stars'] < 50:
            await query.answer("❌ Slot için 50⭐ lazım!", show_alert=True)
            return
        u['stars'] -= 50
        win = random.choices([0, 150, 400], weights=[75, 20, 5])[0]
        u['stars'] += win
        save_data()
        await query.edit_message_text(f"🎰 **SLOT SONUCU:**\n\nKazanç: {win}⭐\nGüncel Bakiye: {u['stars']}⭐", reply_markup=main_menu_kb(uid))

    elif query.data == "p_gor":
        await query.edit_message_text(f"👤 **PROFİLİN**\n\nID: `{uid}`\nBakiye: **{u['stars']}⭐**\nReferans: **{u['refs']}**", reply_markup=main_menu_kb(uid))

    elif query.data == "home_don":
        await query.edit_message_text("🏠 Ana menüye dönüldü.", reply_markup=main_menu_kb(uid))

# --- MESAJ İŞLEME ---
async def message_handler(update, context):
    uid = update.effective_user.id
    u = get_u(uid)
    text = update.message.text

    if u['step'] == "link_bekle":
        u['temp']['target'] = text
        u['step'] = "not_bekle"
        await update.message.reply_text("📝 Siparişiniz için bir **not** yazın:")
    
    elif u['step'] == "not_bekle":
        u['stars'] -= u['temp']['price']
        save_data()
        data['live_log'] = f"@{update.effective_user.username} {u['temp']['name']} aldı! ✅"
        
        adm_msg = (f"🚀 **YENİ SİPARİŞ!**\n\n👤 User: @{update.effective_user.username} ({uid})\n"
                   f"📦 Paket: {u['temp']['name']}\n🔗 Link: `{u['temp']['target']}`\n📝 Not: {text}")
        
        await context.bot.send_message(ADMIN_ID, adm_msg)
        await update.message.reply_text("✅ **Siparişiniz başarıyla alındı!** Admin onayından sonra işlem başlayacaktır.", reply_markup=main_menu_kb(uid))
        u['step'] = None

# --- ADMİN ÖZEL ---
async def admin_cmds(update, context):
    if update.effective_user.id != ADMIN_ID: return
    t = update.message.text
    if t.startswith("/starver"):
        args = t.split()
        target = args[1]; amount = int(args[2])
        get_u(target)['stars'] += amount
        save_data()
        await update.message.reply_text(f"✅ {target} ID'li kullanıcıya {amount} star eklendi.")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.COMMAND, admin_cmds))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("İmparatorluk Botu Hiç Kısaltılmadan Başlatıldı...")
    app.run_polling()
