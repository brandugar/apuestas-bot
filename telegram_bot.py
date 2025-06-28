# telegram_bot.py

import os
import datetime
import requests
from dotenv import load_dotenv
from apuestas import preparar_y_guardar_senales, obtener_senales_para_envio

# ✅ Carga las variables desde el archivo .env
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # También lo cargamos desde .env
# Imagen local que se enviará después de las señales (a las 8am)
IMAGE_PATH = "senal_3.png"
THANKS_IMAGE_PATH = "br4_gracias.png"


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    })
    print("📬 Enviado:", res.status_code, res.text)


def enviar_imagen(imagen_path, caption="🕒 Recuerda que a las 3PM habrá una nueva señal gratuita ⚽🔥"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    if not os.path.exists(imagen_path):
        print(f"❌ Imagen no encontrada: {imagen_path}")
        return

    with open(imagen_path, "rb") as photo:
        res = requests.post(url, data={
            "chat_id": CHANNEL_ID,
            "caption": caption,
            "parse_mode": "Markdown"
        }, files={"photo": photo})

    print("🖼 Imagen enviada:", res.status_code, res.text)


def main():
    ahora = datetime.datetime.now(
        datetime.timezone.utc) - datetime.timedelta(hours=5)  # Hora Colombia
    hora_actual = ahora.hour

    print(f"🕒 Hora Colombia: {ahora.strftime('%H:%M')}")

    print("⚙️ Preparando señales del día...")
    preparar_y_guardar_senales()

    senales = obtener_senales_para_envio(hora_actual)

    if not senales:
        enviar_telegram("📭 No se generaron señales para este horario.")
    else:
        for senal in senales:
            enviar_telegram(senal)

        # Si es 8am, también se envía la imagen informativa
        if hora_actual == 8:
            enviar_imagen(IMAGE_PATH)
        # Si es 8pm, se envía la imagen de agradecimiento
        if hora_actual == 20:
            enviar_imagen(
                THANKS_IMAGE_PATH, "📷 Gracias por confiar en BR4. Mañana más predicciones.")


if __name__ == "__main__":
    main()
