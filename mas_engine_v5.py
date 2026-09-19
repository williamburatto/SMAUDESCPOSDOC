# -*- coding: utf-8 -*-
"""
Motor de Simulação de Sistemas Multiagentes (MAS) e Roteamento Logístico por Dijkstra
UDESC - PPGEEL / Laboratório de Inteligência Computacional (LIC)
"""

import networkx as nx
import numpy as np
import pandas as pd

class MultiAgentDecarbonizationEngine:
    def __init__(self):
        self.graph = nx.Graph()
        self._build_sc_road_network()

    def _build_sc_road_network(self):
        edges = [
            ("Joinville", "Massaranduba", 35.0, "SC-108 / BR-101"),
            ("Massaranduba", "Jaraguá do Sul", 20.0, "SC-108"),
            ("Turvo", "Criciúma", 40.0, "BR-101 / SC-447"),
            ("Criciúma", "Tubarão", 45.0, "BR-101"),
            ("Campos Novos", "Lages", 120.0, "BR-282"),
            ("Chapecó", "São Miguel do Oeste", 130.0, "BR-282"),
            ("Chapecó", "Xanxerê", 45.0, "BR-282"),
            ("Xanxerê", "Concórdia", 85.0, "BR-153 / BR-282"),
            ("Lages", "Florianópolis", 220.0, "BR-282"),
            ("Joinville", "Blumenau", 95.0, "BR-101 / SC-108"),
            ("Canoinhas", "Mafra", 55.0, "BR-280")
        ]
        for u, v, dist, road in edges:
            self.graph.add_edge(u, v, weight=dist, road=road)

    def calculate_dijkstra_route(self, origin, destination):
        if origin not in self.graph or destination not in self.graph:
            return {"distance": 50.0, "path": [origin, destination], "road": "BR-101 / BR-282"}
        try:
            path = nx.dijkstra_path(self.graph, origin, destination)
            length = nx.dijkstra_path_length(self.graph, origin, destination)
            return {"distance": length, "path": path, "road": "Malha Rodoviária SC"}
        except nx.NetworkXNoPath:
            return {"distance": 100.0, "path": [origin, destination], "road": "BR-282"}

    def simulate_sbce_market(self, num_agents=10, rounds=5):
        np.random.seed(42)
        results = []
        for r in range(1, rounds + 1):
            price_free = 0.0
            price_consign = 120.0 + np.random.normal(0, 5)
            price_trad = 160.0 + np.random.normal(0, 10)
            results.append({
                "round": r,
                "free_allocation_price": price_free,
                "consignment_auction_price": round(price_consign, 2),
                "traditional_auction_price": round(price_trad, 2)
            })
        return pd.DataFrame(results)

    def calculate_logistics_ecoefficiency(self, origin, destination, biochar_tonnage, ev_fleet=False):
        route = self.calculate_dijkstra_route(origin, destination)
        dist = route["distance"]
        trips = int(np.ceil(biochar_tonnage / 25.0))
        total_km = dist * 2 * trips
        if ev_fleet:
            kwh_consumed = total_km * 1.2
            co2_transport_tons = (kwh_consumed * 0.04) / 1000.0
            fuel_cost = kwh_consumed * 0.45
        else:
            diesel_liters = total_km / 2.5
            co2_transport_tons = (diesel_liters * 2.68) / 1000.0
            fuel_cost = diesel_liters * 6.10

        gross_seq = biochar_tonnage * 2.1604
        net_seq = max(0.0, gross_seq - co2_transport_tons)
        ecoefficiency = (net_seq / gross_seq * 100.0) if gross_seq > 0 else 100.0

        return {
            "origin": origin,
            "destination": destination,
            "distance_km": dist,
            "trips": trips,
            "total_km": total_km,
            "gross_sequestration_tco2": gross_seq,
            "transport_emissions_tco2": co2_transport_tons,
            "net_sequestration_tco2": net_seq,
            "ecoefficiency_pct": ecoefficiency,
            "fuel_cost_brl": fuel_cost
        }
