# apuestas.py

import requests
import datetime
import json
import os

CACHE_FILE = "senales_enviadas.json"
API_KEY = "232daadb65fac91b4b7a607399ade0f7"

LIGAS = [
    "soccer_epl",                        # Premier League (Inglaterra)
    "soccer_spain_la_liga",             # La Liga (España)
    "soccer_italy_serie_a",             # Serie A (Italia)
    "soccer_germany_bundesliga",        # Bundesliga (Alemania)
    "soccer_france_ligue_one",          # Ligue 1 (Francia)
    "soccer_brazil_campeonato",         # Brasil Serie A
    "soccer_usa_mls"                    # USA MLS
]


def cargar_ids_enviados():
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "r") as f:
        return set(json.load(f))


def guardar_ids_enviados(ids):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(ids), f)


def obtener_partidos():
    hoy = datetime.datetime.utcnow().date()
    partidos = []

    for liga in LIGAS:
        print(f"🔎 Consultando {liga}...")
        url = f"https://api.the-odds-api.com/v4/sports/{liga}/odds/"
        params = {
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "h2h,totals",
            "dateFormat": "iso",
        }

        res = requests.get(url, params=params)
        if res.status_code != 200:
            print(f"❌ Error con {liga}: {res.text}")
            continue

        data = res.json()
        for match in data:
            fecha_partido = datetime.datetime.fromisoformat(
                match['commence_time'].replace("Z", "+00:00")).date()

            if fecha_partido == hoy:
                equipos = match["home_team"] + " vs " + match["away_team"]
                print(f"✅ Partido: {equipos} - {match['commence_time']}")
                partidos.append(match)

    print(f"🎯 Total partidos encontrados: {len(partidos)}")
    return partidos


def generar_senales(partidos):
    senales = []
    ids_enviados = cargar_ids_enviados()

    nuevos_ids = set()

    for partido in partidos:
        partido_id = partido["id"]

        if partido_id in ids_enviados:
            continue  # Ya se envió esta señal antes
        equipos = partido["home_team"] + " vs " + partido["away_team"]
        fecha_utc = datetime.datetime.fromisoformat(
            partido["commence_time"].replace("Z", "+00:00")
        )
        fecha_colombia = fecha_utc - datetime.timedelta(hours=5)
        hora_formateada = fecha_colombia.strftime(
            "%Y-%m-%d %H:%M (hora colombiana)")

        bookmaker = partido["bookmakers"][0] if partido["bookmakers"] else None
        if not bookmaker:
            continue

        cuotas_h2h = [o for o in bookmaker["markets"] if o["key"] == "h2h"]
        cuotas_total = [o for o in bookmaker["markets"]
                        if o["key"] == "totals"]

        senal_over = None
        senal_ganador = None

        if cuotas_total:
            for total in cuotas_total[0]["outcomes"]:
                punto = float(total.get("point", 0))
                over = total["price"]
                if punto in [2.5, 3.0] and over >= 1.70:
                    senal_over = f"🔮 *Over {punto} goles*\n📈 Cuota: {over}\n🧠 Análisis: Partido con potencial ofensivo."
                    break

        if cuotas_h2h:
            outcomes = cuotas_h2h[0]["outcomes"]
            favorito = min(outcomes, key=lambda x: x["price"])
            if favorito["price"] <= 1.80:
                senal_ganador = f"🔮 *Gana {favorito['name']}*\n📈 Cuota: {favorito['price']}\n🧠 Análisis: Favorito con alta probabilidad de victoria."

        if senal_over or senal_ganador:
            mensaje = f"""⚽ *{equipos}*
🗓 Fecha: *{hora_formateada}*
"""
            if senal_ganador and senal_over:
                mensaje += senal_ganador + "\n\n" + senal_over
            elif senal_ganador:
                mensaje += senal_ganador
            elif senal_over:
                mensaje += senal_over

            nuevos_ids.add(partido_id)
            senales.append(mensaje)  # SOLO si hay señal

    # Actualizamos el cache
    ids_enviados.update(nuevos_ids)
    guardar_ids_enviados(ids_enviados)

    return senales
