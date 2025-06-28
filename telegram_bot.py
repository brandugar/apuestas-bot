# telegram_bot.py actualizado para manejar dos horarios diarios

import os
from apuestas import obtener_partidos, generar_senales
import requests
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1002600259944"  # Canal: Predicciones BR4


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, data={
        "chat_id": CHANNEL_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    })
    print("\n📬 Enviado:", res.status_code, res.text)


def main():
    ahora = datetime.datetime.now(
        datetime.timezone.utc) - datetime.timedelta(hours=5)  # Hora Colombia
    hora_actual = ahora.strftime("%H:%M")

    print(f"🕒 Hora actual Colombia: {hora_actual}")

    # Para las 8am y 3pm
    # if hora_actual.startswith("08:") or hora_actual.startswith("15:"):
    print("🕵️ Obteniendo partidos...")
    partidos = obtener_partidos()

    print("⚙️ Generando señales...")
    senales = generar_senales(partidos)

    if not senales:
        enviar_telegram("📭 No se generaron señales para hoy.")
    else:
        top_senales = senales[:2]  # Tomamos solo 2 mejores señales
        for senal in top_senales:
            enviar_telegram(senal)
    # else:
    #     print("⏰ No es hora de enviar señales. Solo se envían a las 8:00am y 3:00pm.")


if __name__ == "__main__":
    main()
