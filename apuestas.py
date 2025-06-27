# apuestas.py

import requests
import datetime

# Asegúrate de tener la variable de entorno BOT_TOKEN configurada
API_KEY = "232daadb65fac91b4b7a607399ade0f7"
# Ligas populares (códigos de The Odds API)
LIGAS = [
    "soccer_epl",                        # Premier League (Inglaterra)
    "soccer_spain_la_liga",             # La Liga (España)
    "soccer_italy_serie_a",             # Serie A (Italia)
    "soccer_germany_bundesliga",        # Bundesliga (Alemania)
    "soccer_france_ligue_one",          # Ligue 1 (Francia)
    "soccer_brazil_campeonato",         # Brasil Serie A
    "soccer_usa_mls"                    # USA MLS
]


def obtener_partidos():
    hoy = datetime.datetime.utcnow().date()
    partidos = []

    for liga in LIGAS:
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

    return partidos


def generar_senales(partidos):
    senales = []

    for partido in partidos:
        equipos = partido["home_team"] + " vs " + partido["away_team"]
        bookmaker = partido["bookmakers"][0] if partido["bookmakers"] else None

        if not bookmaker:
            continue

        cuotas_h2h = [o for o in bookmaker["markets"] if o["key"] == "h2h"]
        cuotas_total = [o for o in bookmaker["markets"]
                        if o["key"] == "totals"]

        if cuotas_total:
            total = cuotas_total[0]["outcomes"][0]
            if float(total["point"]) == 2.5:
                over = total["price"]
                if over >= 1.80:
                    senales.append(f"""⚽ *{equipos}*
🔮 Predicción: *Over 2.5 goles*
📈 Cuota: {over}
🧠 Análisis: Cuota alta sugiere probabilidad real de +2 goles.
""")

        if cuotas_h2h:
            outcomes = cuotas_h2h[0]["outcomes"]
            favorito = min(outcomes, key=lambda x: x["price"])
            if favorito["price"] <= 1.70:
                senales.append(f"""⚽ *{equipos}*
🔮 Predicción: *Gana {favorito["name"]}*
📈 Cuota: {favorito["price"]}
🧠 Análisis: Favorito claro con cuota menor a 1.70.
""")

    return senales
