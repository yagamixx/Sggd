from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==================================================
# CONFIG
# ==================================================

BOT_TOKEN = "8974461603:AAFkY6CK49FcnF_zsGatD5Pf204YK68ryVk"

ADMIN_IDS = [7217351605]  # Replace with your Telegram ID

UPI_ID = "tanmay7979@fam"

# ==================================================
# PRODUCTS
# ==================================================

PRODUCTS = {
    "adult": {
        "name": "ADULT PREMIUM",
        "price": "99",
        "image": "https://i.imgur.com/8Km9tLL.jpg",
        "delivery": "https://yourlink.com/netflix",
        "demo": "https://t.me/netflixdemo"
    },

    "spotify": {
        "name": "Spotify Premium",
        "price": "99",
        "image": "https://i.imgur.com/ZF6s192.jpg",
        "delivery": "https://yourlink.com/spotify",
        "demo": "https://t.me/spotifydemo"
    }
}

# ==================================================
# MEMORY
# ==================================================

users = set()

# ==================================================
# START COMMAND
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    users.add(user_id)

    keyboard = []

    for product_id, product in PRODUCTS.items():

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{product['name']} - ₹{product['price']}",
                    callback_data=f"buy_{product_id}"
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🛒 Welcome To Premium Shop",
        reply_markup=reply_markup
    )

# ==================================================
# BUTTON HANDLER
# ==================================================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # ==========================================
    # BUY PRODUCT
    # ==========================================

    if data.startswith("buy_"):

        product_id = data.split("_")[1]

        product = PRODUCTS[product_id]

        caption = f"""
🔥 {product['name']}

💰 Price: ₹{product['price']}

💳 UPI ID:
`{UPI_ID}`

📤 Send Payment Screenshot After Payment
"""

        keyboard = [
            [
                InlineKeyboardButton(
                    "🛒 Buy Now",
                    callback_data=f"sendss_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎬 Demo",
                    url=product["demo"]
                )
            ]
        ]

        await query.message.reply_photo(
            photo=product["image"],
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================================
    # SEND SCREENSHOT
    # ==========================================

    elif data.startswith("sendss_"):

        product_id = data.split("_")[1]

        context.user_data["product"] = product_id

        await query.message.reply_text(
            "📤 Send Your Payment Screenshot Now"
        )

    # ==========================================
    # APPROVE PAYMENT
    # ==========================================

    elif data.startswith("approve_"):

        parts = data.split("_")

        user_id = int(parts[1])
        product_id = parts[2]

        product = PRODUCTS[product_id]

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text=f"""
✅ Payment Approved

🎁 Your Product Link:
{product['delivery']}
"""
            )

            await query.message.reply_text(
                "✅ Payment Approved Successfully"
            )

        except Exception as e:
            await query.message.reply_text(
                f"❌ Error\n{e}"
            )

    # ==========================================
    # REJECT PAYMENT
    # ==========================================

    elif data.startswith("reject_"):

        parts = data.split("_")

        user_id = int(parts[1])

        try:

            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Payment Rejected"
            )

            await query.message.reply_text(
                "❌ Payment Rejected"
            )

        except Exception as e:
            await query.message.reply_text(
                f"❌ Error\n{e}"
            )

# ==================================================
# SCREENSHOT HANDLER
# ==================================================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if "product" not in context.user_data:
        return

    product_id = context.user_data["product"]

    product = PRODUCTS[product_id]

    caption = f"""
💸 New Payment Request

👤 User ID:
{user_id}

🛍 Product:
{product['name']}

💰 Price:
₹{product['price']}
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{user_id}_{product_id}"
            ),

            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{user_id}_{product_id}"
            )
        ]
    ]

    for admin_id in ADMIN_IDS:

        await context.bot.send_photo(
            chat_id=admin_id,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    await update.message.reply_text(
        "✅ Screenshot Submitted\n⏳ Wait For Admin Approval"
    )

# ==================================================
# ADMIN PANEL
# ==================================================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        return

    text = f"""
👑 ADMIN PANEL

👥 Total Users: {len(users)}

📦 Total Products: {len(PRODUCTS)}

📢 Broadcast:
/broadcast your message
"""

    await update.message.reply_text(text)

# ==================================================
# BROADCAST
# ==================================================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        return

    if len(context.args) == 0:

        await update.message.reply_text(
            "Usage:\n/broadcast Hello"
        )

        return

    message = " ".join(context.args)

    success = 0

    for user in users:

        try:

            await context.bot.send_message(
                chat_id=user,
                text=message
            )

            success += 1

        except:
            pass

    await update.message.reply_text(
        f"✅ Broadcast Sent To {success} Users"
    )

# ==================================================
# MAIN
# ==================================================

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("broadcast", broadcast))

# Buttons
app.add_handler(CallbackQueryHandler(buttons))

# Photos
app.add_handler(
    MessageHandler(filters.PHOTO, photo_handler)
)

print("✅ Bot Running...")

app.run_polling()