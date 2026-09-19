# -*- coding: utf-8 -*-
"""
Módulo de Dados de Santa Catarina e Constantes de Conversão Energética / Agrícola
UDESC - PPGEEL / Laboratório de Inteligência Computacional (LIC)
"""

import pandas as pd
import numpy as np

# Constante de conversão homologada (0.9548 MWh/t com LHV = 13.75 MJ/kg e eficiência de 25%)
MWH_PER_TON_RESIDUE = 0.9548
LHV_ARROZ_MJ_KG = 13.75
EFFICIENCY_CONVERSION = 0.25
BIOCHAR_C_FIXO_PCT = 58.92
CO2_SEQ_PER_TON_BIOCHAR = 2.1604

MUNICIPALITIES_COORDS = {
    "Joinville": (-26.30, -48.84),
    "Massaranduba": (-26.61, -49.00),
    "Turvo": (-28.92, -49.67),
    "Criciúma": (-28.67, -49.37),
    "Tubarão": (-28.47, -49.01),
    "Chapecó": (-27.10, -52.61),
    "São Miguel do Oeste": (-26.72, -53.51),
    "Campos Novos": (-27.40, -51.22),
    "Lages": (-27.81, -50.32),
    "Blumenau": (-26.91, -49.06),
    "Florianópolis": (-27.59, -48.54),
    "Jaraguá do Sul": (-26.48, -49.08),
    "Canoinhas": (-26.17, -50.38),
    "Mafra": (-26.11, -49.80),
    "Xanxerê": (-26.87, -52.40),
    "Concórdia": (-27.23, -52.02)
}

CROP_FACTORS = {
    "Arroz": {"residue_factor": 1.0, "lhv": 13.75, "carbon_content": 0.40},
    "Soja": {"residue_factor": 0.73, "lhv": 15.20, "carbon_content": 0.42},
    "Milho": {"residue_factor": 0.58, "lhv": 14.80, "carbon_content": 0.41},
    "Trigo": {"residue_factor": 0.65, "lhv": 14.10, "carbon_content": 0.39},
    "Feijão": {"residue_factor": 0.50, "lhv": 13.50, "carbon_content": 0.38}
}

def calculate_electric_potential(tonnage, efficiency=0.25):
    return tonnage * 1000 * LHV_ARROZ_MJ_KG / 3600 * efficiency
