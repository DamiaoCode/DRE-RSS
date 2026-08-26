"""Persistência incremental dos procedimentos extraídos do RSS do DRE."""

import json
import os
from datetime import datetime
from typing import Dict, List
from zoneinfo import ZoneInfo

LISBON_TZ = ZoneInfo("Europe/Lisbon")


def lisbon_today() -> str:
    """Data de hoje em Europe/Lisbon, no formato DD-MM-YYYY."""
    return datetime.now(LISBON_TZ).strftime("%d-%m-%Y")


def daily_data_path(data_dir: str = "../data") -> str:
    return os.path.join(data_dir, f"{lisbon_today()}.json")


def load_json_list(filepath: str) -> List[Dict]:
    """Carrega uma lista JSON; devolve [] se o ficheiro não existir ou for inválido."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        print(f"⚠️ Conteúdo inesperado em {filepath}; a ignorar.")
        return []
    except Exception as e:
        print(f"⚠️ Erro ao carregar {filepath}: {e}")
        return []


def has_complete_details(item: Dict) -> bool:
    detalhes = item.get("detalhes_completos")
    return bool(detalhes and str(detalhes).strip())


def item_link(item: Dict) -> str:
    return (item.get("link") or "").strip()


def merge_procedimentos_by_link(
    existing: List[Dict], incoming: List[Dict]
) -> List[Dict]:
    """Junta procedimentos pelo link, sem perder itens já guardados.

    Preferência: o registo com detalhes completos. Itens só presentes em
    `existing` (já recolhidos mais cedo no mesmo dia) são mantidos mesmo que
    o RSS atual já não os liste.
    """
    by_link: Dict[str, Dict] = {}
    order: List[str] = []

    def add(item: Dict) -> None:
        link = item_link(item)
        if not link:
            return
        if link not in by_link:
            by_link[link] = item
            order.append(link)
            return
        current = by_link[link]
        if has_complete_details(item) and not has_complete_details(current):
            by_link[link] = item

    for item in existing:
        add(item)
    for item in incoming:
        add(item)

    return [by_link[link] for link in order]


def existing_complete_by_link(existing: List[Dict]) -> Dict[str, Dict]:
    """Mapa link → procedimento já extraído com detalhes."""
    return {
        item_link(item): item
        for item in existing
        if item_link(item) and has_complete_details(item)
    }
