# apuestas.py

import requests
import datetime
import json
import os

API_KEY = "232daadb65fac91b4b7a607399ade0f7"
CACHE_FILE_IDS = "senales_enviadas.json"
CACHE_FILE_DIARIAS = "senales_diarias.json"

LIGAS = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
    "soccer_conmebol_copa_libertadores",
    "soccer_brazil_campeonato",
    "soccer_usa_mls"
]

ahora = datetime.datetime.now(
    datetime.timezone.utc) - datetime.timedelta(hours=5)  # Hora Colombia
hora_actual = ahora.hour


def cargar_ids_enviados():
    if not os.path.exists(CACHE_FILE_IDS):
        return set()
    with open(CACHE_FILE_IDS, "r") as f:
        return set(json.load(f))


def guardar_ids_enviados(ids):
    with open(CACHE_FILE_IDS, "w") as f:
        json.dump(list(ids), f)


def obtener_partidos():
    hoy = datetime.datetime.utcnow().date()
    partidos = []

    if hora_actual == 8 or hora_actual == 15:
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
                    partidos.append(match)

        print(f"🎯 Total partidos encontrados: {len(partidos)}")
        return partidos
    else:
        print("⏳ No es hora de buscar partidos. Hora actual:", hora_actual)
        return []


def generar_senales(partidos):
    señales = []

    for partido in partidos:
        equipos = partido["home_team"] + " vs " + partido["away_team"]
        partido_id = partido["id"]
        fecha_utc = datetime.datetime.fromisoformat(
            partido["commence_time"].replace("Z", "+00:00"))
        fecha_colombia = fecha_utc - datetime.timedelta(hours=5)
        hora_formateada = fecha_colombia.strftime(
            "%Y-%m-%d %H:%M (hora colombiana)")

        bookmaker = partido["bookmakers"][0] if partido["bookmakers"] else None
        if not bookmaker:
            continue

        cuotas_h2h = [m for m in bookmaker["markets"] if m["key"] == "h2h"]
        cuotas_total = [m for m in bookmaker["markets"]
                        if m["key"] == "totals"]

        senal_over = None
        senal_ganador = None

        if cuotas_total:
            for total in cuotas_total[0]["outcomes"]:
                punto = float(total.get("point", 0))
                cuota = total["price"]
                if punto in [2.5, 3.0] and cuota >= 1.70:
                    senal_over = (
                        f"🔮 *Pronóstico:* Over {punto} goles\n"
                        f"💸 *Cuota:* {cuota}\n"
                        f"📈 *Análisis:* Partido con potencial ofensivo."
                    )
                    break

        if cuotas_h2h:
            outcomes = cuotas_h2h[0]["outcomes"]
            favorito = min(outcomes, key=lambda x: x["price"])
            if favorito["price"] <= 1.80:
                senal_ganador = (
                    f"🔮 *Pronóstico:* Gana {favorito['name']}\n"
                    f"💸 *Cuota:* {favorito['price']}\n"
                    f"📈 *Análisis:* Favorito con alta probabilidad de victoria."
                )

        if senal_over or senal_ganador:
            mensaje = f"""📊 *SEÑAL DEL DÍA*

⚽️ *{equipos}*  
📅 *Fecha:* {hora_formateada}

"""
            if senal_ganador:
                mensaje += senal_ganador + "\n\n"
            if senal_over:
                mensaje += senal_over

            señales.append({
                "id": partido_id,
                "mensaje": mensaje.strip()
            })

    return señales


def guardar_senales_diarias(senales):
    with open(CACHE_FILE_DIARIAS, "w") as f:
        json.dump(senales, f)


def cargar_senales_diarias():
    if not os.path.exists(CACHE_FILE_DIARIAS):
        return []
    with open(CACHE_FILE_DIARIAS, "r") as f:
        return json.load(f)


def obtener_senales_para_envio(hora_actual):
    todas_senales = cargar_senales_diarias()
    ids_enviados = cargar_ids_enviados()
    nuevas = [s for s in todas_senales if s["id"] not in ids_enviados]

    if hora_actual < 15:
        a_enviar = nuevas[:2]
    else:
        a_enviar = nuevas[2:3]

    nuevos_ids = set(s["id"] for s in a_enviar)
    ids_enviados.update(nuevos_ids)
    guardar_ids_enviados(ids_enviados)

    return [s["mensaje"] for s in a_enviar]


def preparar_y_guardar_senales():
    partidos = obtener_partidos()
    todas = generar_senales(partidos)
    guardar_senales_diarias(todas[:3])
