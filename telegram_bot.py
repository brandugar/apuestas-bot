# telegram_bot.py

import os
from apuestas import obtener_partidos, generar_senales
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1002600259944"  # tu canal: Predicciones BR4


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    })
    print("📬 Enviado:", res.status_code, res.text)


def main():
    print("🕵️ Obteniendo partidos...")
    partidos = obtener_partidos()

    print("⚙️ Generando señales...")
    senales = generar_senales(partidos)

    if not senales:
        enviar_telegram("📭 No se generaron señales para hoy.")
    else:
        for senal in senales:
            enviar_telegram(senal)


if __name__ == "__main__":
    main()
