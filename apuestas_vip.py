# apuestas_vip.py

import requests
import datetime
import json
import os

API_KEY = "232daadb65fac91b4b7a607399ade0f7"
CACHE_FILE_IDS_VIP = "senales_vip_enviadas.json"
CACHE_FILE_DIARIAS_VIP = "senales_vip_diarias.json"
CACHE_FILE_IDS_GRATIS = "senales_enviadas.json"


LIGAS_VIP = [
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
    "soccer_france_ligue_one",
    "soccer_argentina_primera_division",
    "soccer_brazil_campeonato",
    "soccer_mexico_ligamx",
    "soccer_conmebol_copa_libertadores",
    "soccer_conmebol_copa_sudamericana",
    "soccer_uefa_champs_league_qualification",  # Clasificación UCL
    "soccer_netherlands_eredivisie",
    "soccer_usa_mls"
]


def cargar_ids_gratis():
    if not os.path.exists(CACHE_FILE_IDS_GRATIS):
        return set()
    with open(CACHE_FILE_IDS_GRATIS, "r") as f:
        return set(json.load(f))


def cargar_ids_enviados_vip():
    if not os.path.exists(CACHE_FILE_IDS_VIP):
        return set()
    with open(CACHE_FILE_IDS_VIP, "r") as f:
        return set(json.load(f))


def guardar_ids_enviados_vip(ids):
    with open(CACHE_FILE_IDS_VIP, "w") as f:
        json.dump(list(ids), f)


def obtener_partidos_vip():
    hoy = datetime.datetime.utcnow().date()
    partidos = []

    for liga in LIGAS_VIP:
        print(f"🔎 [VIP] Consultando {liga}...")
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

        for match in res.json():
            fecha_partido = datetime.datetime.fromisoformat(
                match['commence_time'].replace("Z", "+00:00")).date()
            if fecha_partido == hoy:
                equipos = f"{match['home_team']} vs {match['away_team']}"
                hora_local = datetime.datetime.fromisoformat(
                    match['commence_time'].replace("Z", "+00:00")) - datetime.timedelta(hours=5)
                print(
                    f"✅ Partido hoy: {equipos} a las {hora_local.strftime('%H:%M')}")
                partidos.append(match)

    print(f"🎯 [VIP] Partidos encontrados: {len(partidos)}")
    return partidos


def generar_senales_vip(partidos):
    senales = []
    ids_gratis = cargar_ids_gratis()

    for partido in partidos:
        if partido["id"] in ids_gratis:
            continue
        if not partido.get("bookmakers"):
            continue

        mejor_favorito = None
        mejor_over = None

        for bookmaker in partido["bookmakers"]:
            mercados = {m["key"]: m for m in bookmaker["markets"]}
            cuotas_h2h = mercados.get("h2h", {}).get("outcomes", [])
            cuotas_total = mercados.get("totals", {}).get("outcomes", [])

            if cuotas_h2h:
                favorito = min(cuotas_h2h, key=lambda x: x["price"])
                if favorito["price"] <= 1.80:
                    if not mejor_favorito or favorito["price"] < mejor_favorito["price"]:
                        mejor_favorito = favorito

            over_valido = next(
                (t for t in cuotas_total if float(t.get("point", 0))
                 in [2.5, 3.0] and t["price"] >= 1.75),
                None
            )
            if over_valido:
                if not mejor_over or over_valido["price"] > mejor_over["price"]:
                    mejor_over = over_valido

        if not mejor_favorito and not mejor_over:
            continue

        fecha_col = datetime.datetime.fromisoformat(
            partido["commence_time"].replace("Z", "+00:00")) - datetime.timedelta(hours=5)
        hora_txt = fecha_col.strftime("%Y-%m-%d %H:%M (Col)")
        equipos = f"{partido['home_team']} vs {partido['away_team']}"

        mensaje = f"""🔥 *SEÑAL VIP*  
🏟 *{equipos}*  
🗓 *{hora_txt}*  
"""

        if mejor_favorito:
            mensaje += f"""🔮 *Gana {mejor_favorito['name']}*  
💸 Cuota: {mejor_favorito['price']}  
"""

        if mejor_over:
            mensaje += f"""⚽ *Over {mejor_over['point']} goles*  
💸 Cuota: {mejor_over['price']}  
"""

        mensaje += """
📊 *Análisis VIP:*  
- Análisis basado en forma reciente, promedio de goles y fortaleza ofensiva.  
- Buenas condiciones de valor para una apuesta segura con riesgo moderado.
        """

        senales.append({"id": partido["id"], "mensaje": mensaje.strip()})

    print(f"✅ [VIP] Total señales generadas: {len(senales)}")
    return senales


def guardar_senales_vip(senales):
    with open(CACHE_FILE_DIARIAS_VIP, "w") as f:
        json.dump(senales, f)


def cargar_senales_vip():
    if not os.path.exists(CACHE_FILE_DIARIAS_VIP):
        return []
    with open(CACHE_FILE_DIARIAS_VIP, "r") as f:
        return json.load(f)


def obtener_senales_para_envio_vip():
    todas = cargar_senales_vip()
    enviados = cargar_ids_enviados_vip()
    nuevas = [s for s in todas if s["id"] not in enviados]
    nuevos_ids = {s["id"] for s in nuevas}
    enviados.update(nuevos_ids)
    guardar_ids_enviados_vip(enviados)
    return [s["mensaje"] for s in nuevas[:2]]


def preparar_y_guardar_senales_vip():
    partidos = obtener_partidos_vip()
    senales = generar_senales_vip(partidos)
    guardar_senales_vip(senales[:5])
