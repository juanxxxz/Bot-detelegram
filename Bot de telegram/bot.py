import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Configuración básica - ¡CORREGIR!
TOKEN = "8253820120:AAE7d0l-eTr-Nrqq8sckSgRC7lFHtmoJzbg"
ADMIN_USER_ID = 6217130817  # Reemplaza con tu ID numérico real
CHANNEL_LINK = "https://t.me/tu_canal_aqui"

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Mensaje de bienvenida (sin cambios)
WELCOME_MESSAGE = """Hola bienvenido al bot de nuestro canal..."""

# Comando start (sin cambios)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Canal", callback_data="canal")],
        [InlineKeyboardButton("Descarga Directa", callback_data="descarga_directa")],
        [InlineKeyboardButton("Ayuda", callback_data="ayuda")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

# Manejar botones - CORREGIDO
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Limpiar estados previos
    context.user_data.clear()
    
    if query.data == "canal":
        canal_message = """Enviar el monto de 50 cup al numero: 9227 0699 9724 0794 y la confirmación al numero: 51309330, enviar captura de pantalla con el mensaje de la transferencia confirmada al bot"""
        await query.edit_message_text(canal_message)
        context.user_data['esperando_captura'] = True
        
    elif query.data == "descarga_directa":
        descarga_message = """Envía el link de descarga directa de lo que quieres descargar sin gastar megas o dinos la serie o pelicula que quieres obtener de esta forma"""
        await query.edit_message_text(descarga_message)
        context.user_data['esperando_descarga'] = True
        
    elif query.data == "ayuda":
        ayuda_message = "¿En qué lo podemos ayudar??"
        await query.edit_message_text(ayuda_message)
        context.user_data['esperando_ayuda'] = True
        
    elif query.data == "si_aprobar":
        try:
            original_user_id = context.user_data.get('pending_user')
            if original_user_id:
                await context.bot.send_message(
                    chat_id=original_user_id,
                    text=f"¡Pago aprobado! Aquí está el enlace a nuestro canal: {CHANNEL_LINK}"
                )
                await query.edit_message_text("Usuario aprobado y enlace enviado ✅")
                # Limpiar estado
                context.user_data.pop('pending_user', None)
        except Exception as e:
            logging.error(f"Error al enviar enlace: {e}")
            await query.edit_message_text("❌ Error al aprobar usuario")
            
    elif query.data == "no_rechazar":
        try:
            original_user_id = context.user_data.get('pending_user')
            if original_user_id:
                await context.bot.send_message(
                    chat_id=original_user_id,
                    text="Lo sentimos, su pago no ha sido aprobado. Por favor verifique la transferencia y vuelva a intentar."
                )
                await query.edit_message_text("Usuario rechazado ❌")
                # Limpiar estado
                context.user_data.pop('pending_user', None)
        except Exception as e:
            logging.error(f"Error al rechazar usuario: {e}")
            await query.edit_message_text("❌ Error al rechazar usuario")

# Manejar fotos - CORREGIDO
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('esperando_captura'):
        user = update.message.from_user
        photo = update.message.photo[-1]
        
        keyboard = [
            [InlineKeyboardButton("Sí ✅", callback_data="si_aprobar")],
            [InlineKeyboardButton("No ❌", callback_data="no_rechazar")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Guardar ID del usuario
        context.user_data['pending_user'] = user.id
        
        caption = f"Usuario {user.first_name} (@{user.username or 'sin_username'}) ID: {user.id} envió captura de pago"
        
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_USER_ID,
                photo=photo.file_id,
                caption=caption,
                reply_markup=reply_markup
            )
            await update.message.reply_text("✅ Captura enviada al administrador. Espere la confirmación.")
        except Exception as e:
            logging.error(f"Error al reenviar foto: {e}")
            await update.message.reply_text("❌ Error al procesar la captura. Intente más tarde.")
        
        # Limpiar estado
        context.user_data['esperando_captura'] = False

# Manejar mensajes de texto - CORREGIDO
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Si el mensaje es del administrador, manejar respuestas
    if update.message.from_user.id == ADMIN_USER_ID:
        await handle_admin_reply(update, context)
        return
        
    user = update.message.from_user
    message_text = update.message.text
    
    # Si está esperando descarga directa
    if context.user_data.get('esperando_descarga'):
        try:
            admin_message = f"📥 SOLICITUD DESCARGA DIRECTA\nDe: {user.first_name} (@{user.username or 'sin_username'})\nID: {user.id}\n\nMensaje: {message_text}"
            await context.bot.send_message(chat_id=ADMIN_USER_ID, text=admin_message)
            await update.message.reply_text("✅ Su solicitud ha sido enviada al administrador. Espere respuesta.")
        except Exception as e:
            logging.error(f"Error al reenviar solicitud de descarga: {e}")
            await update.message.reply_text("❌ Error al enviar solicitud. Intente más tarde.")
        context.user_data['esperando_descarga'] = False
        
    # Si está en modo ayuda
    elif context.user_data.get('esperando_ayuda'):
        try:
            admin_message = f"🆘 SOLICITUD DE AYUDA\nDe: {user.first_name} (@{user.username or 'sin_username'})\nID: {user.id}\n\nMensaje: {message_text}"
            await context.bot.send_message(chat_id=ADMIN_USER_ID, text=admin_message)
            await update.message.reply_text("✅ Su consulta ha sido enviada al administrador. Espere respuesta.")
        except Exception as e:
            logging.error(f"Error al reenviar solicitud de ayuda: {e}")
            await update.message.reply_text("❌ Error al enviar consulta. Intente más tarde.")
        context.user_data['esperando_ayuda'] = False

# Nueva función para manejar respuestas del administrador
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Aquí puedes implementar la lógica para que el admin responda a usuarios específicos
    # Por ejemplo, usando replies o comandos especiales
    pass

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot iniciado...")
    application.run_polling()

if __name__ == '__main__':
    main()
