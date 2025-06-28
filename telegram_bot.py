# telegram_bot.py

import os
import datetime
import requests
from apuestas import preparar_y_guardar_senales, obtener_senales_para_envio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1002600259944"  # Reemplaza por tu canal


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
    hora_actual = ahora.hour

    print(f"🕒 Hora Colombia: {ahora.strftime('%H:%M')}")

    if hora_actual == 8:
        print("⚙️ Preparando señales del día...")
        preparar_y_guardar_senales()

    print("📡 Obteniendo señales para este horario...")
    senales = obtener_senales_para_envio(hora_actual)

    if not senales:
        enviar_telegram("📭 No se generaron señales para este horario.")
    else:
        for senal in senales:
            enviar_telegram(senal)


if __name__ == "__main__":
    main()
