import math
import os
from typing import Optional

import requests

from app.repositories import rh_transporte_repository as repo

_NOMINATIM_UA = "FactoryOps-RH/1.0 (rh@venttos.com.br)"
_ORS_BASE = "https://api.openrouteservice.org"


def geocodificar(endereco: str, cidade: str = "Manaus", estado: str = "AM") -> Optional[dict]:
    """
    Geocodes an address via Nominatim (free, no API key).
    Returns {"lat": float, "lng": float, "display_name": str} or None.
    """
    query = f"{endereco}, {cidade}, {estado}, Brasil"
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "format": "json",
                "q": query,
                "countrycodes": "br",
                "limit": 1,
                "addressdetails": 0,
            },
            headers={"User-Agent": _NOMINATIM_UA},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json()
        if results:
            return {
                "lat": float(results[0]["lat"]),
                "lng": float(results[0]["lon"]),
                "display_name": results[0].get("display_name", ""),
            }
    except Exception:
        pass
    return None


def otimizar_rota(rota_id: int) -> Optional[list]:
    """
    Calls ORS /optimization (VRP) for the route.
    Returns list of collaborator IDs in optimized order, or None on failure.
    Requires ORS_API_KEY environment variable.
    """
    key = os.environ.get("ORS_API_KEY", "")
    if not key:
        return None

    rota = repo.buscar_rota(rota_id)
    if not rota:
        return None

    colabs = repo.listar_colaboradores_rota(rota_id)
    geocoded = [c for c in colabs if c["lat"] and c["lng"]]
    if len(geocoded) < 2:
        return None

    depot_lat = rota["partida_lat"] or -3.0965
    depot_lng = rota["partida_lng"] or -60.0208

    vehicles = [{
        "id": 0,
        "profile": "driving-car",
        "start": [depot_lng, depot_lat],
    }]
    jobs = [
        {"id": c["id"], "location": [c["lng"], c["lat"]]}
        for c in geocoded
    ]

    try:
        r = requests.post(
            f"{_ORS_BASE}/optimization",
            json={"vehicles": vehicles, "jobs": jobs},
            headers={"Authorization": key, "Content-Type": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        steps = data["routes"][0]["steps"]
        return [s["job"] for s in steps if s.get("type") == "job"]
    except Exception:
        return None


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r1, r2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(r1) * math.cos(r2) * math.sin(dlng / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(a))


def calcular_custos_rotas() -> list:
    rotas = repo.listar_rotas_para_custo()
    if not rotas:
        return []

    precos_raw = repo.listar_precos_combustivel()
    precos = {p['tipo']: p['preco_litro'] for p in precos_raw}

    resultado = []
    for r in rotas:
        coords = r.get('coords') or []
        tipo_comb = r['tipo_combustivel'] or 'diesel'
        consumo = r['consumo_km_l'] or 7.5
        preco = precos.get(tipo_comb) or precos.get('diesel') or 0.0

        if coords:
            pts: list = []
            if r['partida_lat'] and r['partida_lng']:
                depot = (r['partida_lat'], r['partida_lng'])
                pts = [depot] + coords + [depot]
            else:
                pts = coords
            dist_km = sum(
                _haversine_km(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
                for i in range(len(pts) - 1)
            )
        elif r['total_colabs'] > 0:
            dist_km = float(r['total_colabs']) * 5.0
        else:
            dist_km = 0.0

        litros = dist_km / consumo if consumo else 0.0
        custo = litros * preco

        resultado.append({
            'id': r['id'],
            'codigo': r['codigo'],
            'nome': r['nome'],
            'turno': r['turno'],
            'cor': r['cor'],
            'veiculo': r['veiculo'],
            'tipo_combustivel': tipo_comb,
            'consumo_km_l': round(consumo, 2),
            'total_colabs': int(r['total_colabs']),
            'colab_geocoded': int(r['colab_geocoded']),
            'dist_km_est': round(dist_km, 1),
            'litros_est': round(litros, 2),
            'custo_est': round(custo, 2),
            'preco_litro': round(preco, 3),
        })

    return resultado


_VELOCIDADE_URBANA_KMH = 28.0
_TEMPO_PARADA_MIN = 2.5
_FATOR_TRANSITO = 1.20


def _minutos_para_hora(minutos: float) -> str:
    m = int(minutos) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def _formatar_duracao(minutos: int) -> str:
    if minutos >= 60:
        return f"{minutos // 60}h {minutos % 60:02d}min"
    return f"{minutos}min"


def calcular_tempo_rota(rota_id: int, hora_saida: str) -> Optional[dict]:
    """
    Estimates arrival time at each stop.
    Uses haversine + average urban speed (28 km/h) with 20% traffic factor.
    hora_saida: "HH:MM"
    """
    rota = repo.buscar_rota(rota_id)
    if not rota:
        return None
    try:
        h, m = map(int, hora_saida.strip().split(':'))
        minutos_inicio = float(h * 60 + m)
    except (ValueError, AttributeError):
        return None

    colabs = repo.listar_colaboradores_rota(rota_id)

    depot_lat = float(rota['partida_lat'] or -3.0832)
    depot_lng = float(rota['partida_lng'] or -59.9969)

    paradas = []
    tempo_atual = minutos_inicio
    dist_acumulada = 0.0
    prev_lat, prev_lng = depot_lat, depot_lng

    for c in colabs:
        lat = c.get('lat')
        lng = c.get('lng')
        if lat and lng:
            lat, lng = float(lat), float(lng)
            dist = _haversine_km(prev_lat, prev_lng, lat, lng)
            tempo_viagem = (dist / _VELOCIDADE_URBANA_KMH) * 60 * _FATOR_TRANSITO
            tempo_atual += tempo_viagem + _TEMPO_PARADA_MIN
            dist_acumulada += dist
            prev_lat, prev_lng = lat, lng
            hora_chegada = _minutos_para_hora(tempo_atual)
        else:
            hora_chegada = None

        paradas.append({
            'id':                c['id'],
            'nome':              c['nome'],
            'bairro':            c.get('endereco_bairro') or '',
            'hora_chegada':      hora_chegada,
            'dist_acumulada_km': round(dist_acumulada, 1),
            'geocodificado':     bool(c.get('geocodificado')),
        })

    if (prev_lat != depot_lat or prev_lng != depot_lng):
        dist_retorno = _haversine_km(prev_lat, prev_lng, depot_lat, depot_lng)
        tempo_atual += (dist_retorno / _VELOCIDADE_URBANA_KMH) * 60 * _FATOR_TRANSITO
        dist_acumulada += dist_retorno

    duracao = round(tempo_atual - minutos_inicio)
    sem_geo = sum(1 for p in paradas if not p['geocodificado'])

    return {
        'hora_saida':        hora_saida,
        'hora_chegada_final': _minutos_para_hora(tempo_atual),
        'duracao_min':       duracao,
        'duracao_fmt':       _formatar_duracao(duracao),
        'dist_total_km':     round(dist_acumulada, 1),
        'paradas':           paradas,
        'total_paradas':     len(paradas),
        'sem_geo':           sem_geo,
        'velocidade_kmh':    _VELOCIDADE_URBANA_KMH,
    }


def buscar_preco_externo() -> Optional[dict]:
    """
    Tenta buscar preços de combustível de uma fonte externa.
    Requer a variável de ambiente FUEL_PRICE_URL apontando para um
    endpoint JSON que retorne {"diesel": X.XX, "gasolina": X.XX, ...}.
    Retorna None se indisponível.
    """
    url = os.environ.get("FUEL_PRICE_URL", "")
    if not url:
        return None
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": _NOMINATIM_UA})
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            return {k: float(v) for k, v in data.items() if isinstance(v, (int, float, str))}
    except Exception:
        pass
    return None


def calcular_trajeto(rota_id: int) -> Optional[dict]:
    """
    Calls ORS /v2/directions with depot + collaborators (ordered).
    Returns GeoJSON FeatureCollection or None.
    Requires ORS_API_KEY environment variable.
    """
    key = os.environ.get("ORS_API_KEY", "")
    if not key:
        return None

    rota = repo.buscar_rota(rota_id)
    if not rota:
        return None

    colabs = repo.listar_colaboradores_rota(rota_id)
    geocoded = [c for c in colabs if c["lat"] and c["lng"]]
    if not geocoded:
        return None

    depot_lat = rota["partida_lat"] or -3.0965
    depot_lng = rota["partida_lng"] or -60.0208

    coordinates = [[depot_lng, depot_lat]] + [[c["lng"], c["lat"]] for c in geocoded]

    if len(coordinates) < 2:
        return None

    try:
        r = requests.post(
            f"{_ORS_BASE}/v2/directions/driving-car/geojson",
            json={"coordinates": coordinates},
            headers={"Authorization": key, "Content-Type": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None
