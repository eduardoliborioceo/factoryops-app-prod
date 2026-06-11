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
