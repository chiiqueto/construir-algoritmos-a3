import os

import requests
import folium
from dotenv import load_dotenv
from folium import Icon, Map, Marker, Popup

load_dotenv(".env")

BASE_URL = "http://api.olhovivo.sptrans.com.br/v2.1"
LINHA_DOS_SLIDES = 2506
TERMO_BUSCA = "Lapa"

s = requests.Session()
res = s.post(f"{BASE_URL}/Login/Autenticar?token={os.getenv('SPTRANS_TOKEN')}")
if res.text != "true":
    raise SystemExit("Falha na autenticação. Verifique o SPTRANS_TOKEN no .env")
print("Autenticado:", res.text)

linhas = s.get(f"{BASE_URL}/Linha/Buscar?termosBusca={TERMO_BUSCA}").json()
linha, paradas = None, []
for l in linhas:
    if l.get("cl") == LINHA_DOS_SLIDES:
        continue
    paradas = s.get(
        f"{BASE_URL}/Parada/BuscarParadasPorLinha?codigoLinha={l['cl']}"
    ).json()
    if paradas:
        linha = l
        break

if not linha:
    raise SystemExit(f"Nenhuma linha com paradas encontrada para '{TERMO_BUSCA}'")

codigo_linha = linha["cl"]
print(f"Linha escolhida: {linha['lt']}-{linha['tl']} ({linha['tp']} / {linha['ts']}) - cl={codigo_linha}")
print(f"{len(paradas)} paradas encontradas")

pos = s.get(f"{BASE_URL}/Posicao/Linha?codigoLinha={codigo_linha}").json()
veiculos = pos.get("vs", [])
print(f"{len(veiculos)} ônibus em circulação às {pos.get('hr')}")

mapa = folium.Map(
    location=[-23.55, -46.63],
    zoom_start=12,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles &copy; Esri",
)

for p in paradas:
    if p.get("py") is None or p.get("px") is None:
        continue
    Marker(
        location=[p["py"], p["px"]],
        popup=Popup(f"{p.get('np', '')}<br>{p.get('ed', '')}", max_width=250),
        icon=Icon(color="blue", icon="map-pin", prefix="fa"),
    ).add_to(mapa)

for v in veiculos:
    if v.get("py") is None or v.get("px") is None:
        continue
    Marker(
        location=[v["py"], v["px"]],
        popup=Popup(f"Ônibus {v.get('p')}<br>Atualizado: {v.get('ta')}", max_width=250),
        icon=Icon(color="red", icon="bus", prefix="fa"),
    ).add_to(mapa)

mapa.save("mapa.html")
print("Mapa salvo em mapa.html")