from __future__ import annotations


def inventory_status(available_units: int, reorder_point: int, pending_units: int) -> str:
    net_available = available_units - pending_units
    if net_available <= reorder_point:
        return "Repor agora"
    if net_available <= int(reorder_point * 1.5):
        return "Monitorar"
    return "Estável"
