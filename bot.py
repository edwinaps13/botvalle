import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ContextTypes, ConversationHandler
)

# Cargar sitios desde JSON
with open("sitios.json", "r", encoding="utf-8") as f:
    sitios = json.load(f)

BUSCANDO_SITIO = 1

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Buscar sitio", callback_data="buscar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hola 👋 ¿Qué deseas hacer?", reply_markup=reply_markup)

# Al presionar el botón de buscar
async def buscar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Escribe el nombre o parte del nombre del sitio que estás buscando:")
    return BUSCANDO_SITIO

# El usuario escribe el nombre del sitio
async def recibir_busqueda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    resultados = [s for s in sitios if texto in s["SITIO"].lower()]

    if not resultados:
        await update.message.reply_text("⚠️ No se encontraron sitios con ese nombre.")
        return ConversationHandler.END

    # Crear botones para los sitios encontrados
    keyboard = [
        [InlineKeyboardButton(s["SITIO"], callback_data=f"sitio_{i}")]
        for i, s in enumerate(resultados[:10])  # máximo 10 resultados
    ]

    context.user_data["resultados"] = resultados
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona el sitio que estás buscando:", reply_markup=reply_markup)
    return ConversationHandler.END

# El usuario elige uno de los sitios sugeridos
async def mostrar_detalles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("sitio_"):
        idx = int(query.data.split("_")[1])
        sitio = context.user_data["resultados"][idx]

        mensaje = (
            f"<b>📍 Sitio:</b> {sitio.get('SITIO', 'N/A')}\n"
            f"<b>🆔 ID:</b> {sitio.get('IDENTIFICADOR', 'N/A')}\n"
            f"<b>   Nic:</b> {sitio.get('NIC', 'N/A')}\n"
            f"<b>📌 Dirección:</b> {sitio.get('DIRECCION', 'N/A')}\n"
            f"<b>📡 Coordenadas:</b> {sitio.get('LATITUD')}, {sitio.get('LONGITUD')}\n"
            f"<b>👤 Propietario EEL:</b> {sitio.get('PROPIETARIO EEL ', 'N/A')}\n"
            f'<b>🌐 Ver en Google Maps:</b> <a href="https://www.google.com/maps?q={sitio.get("LATITUD")},{sitio.get("LONGITUD")}">Abrir ubicación</a>'
        )

        await query.message.reply_text(mensaje, parse_mode="HTML")

# Configura el bot
TOKEN = "8202668609:AAF3i4qVMYrtc30h9wHf1WEuoFQVNgjVeLs"

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Conversación para buscar
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(buscar_callback, pattern="^buscar$")],
        states={BUSCANDO_SITIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_busqueda)]},
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(mostrar_detalles, pattern="^sitio_"))

    print("🤖 Bot corriendo con búsqueda de sitios...")
    app.run_polling()
