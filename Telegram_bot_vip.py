# telegram_bot_vip.py

import os
import datetime
import requests
from dotenv import load_dotenv
from apuestas_vip import preparar_y_guardar_senales_vip, obtener_senales_para_envio_vip

# Cargar variables de entorno (.env)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID_VIP")


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    })
    print("📬 Enviado:", res.status_code, res.text)


def main():
    ahora = datetime.datetime.now(
        datetime.timezone.utc) - datetime.timedelta(hours=5)  # Hora Colombia

    print(f"🕒 [VIP] Hora Colombia: {ahora.strftime('%H:%M')}")

    print("⚙️ [VIP] Preparando señales VIP del día...")
    preparar_y_guardar_senales_vip()

    print("📡 [VIP] Obteniendo señales VIP para este horario...")
    senales_vip = obtener_senales_para_envio_vip()

    if not senales_vip:
        enviar_telegram("📭 No se generaron señales VIP para hoy.")
    else:
        for senal in senales_vip:
            enviar_telegram(senal)


if __name__ == "__main__":
    main()
