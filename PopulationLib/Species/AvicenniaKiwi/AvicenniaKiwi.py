#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def createPlant():
    """
    Constructor containing species-specific parameters and the initial geometry of a plant required by the Kiwi plant module.
    Returns:
        multiple dict
    """
    geometry = {}
    parameter = {}
    geometry["height"] = 0                              # m
    geometry["r_stem"] = 0.005                          # m
    geometry["r_crown"] = 0.22                          # m
    parameter["salt_effect_d"] = -0.18
    parameter["salt_effect_ui"] = 72
    parameter["max_height"] = 3500                      # cm
    parameter["max_dbh"] = 140                          # cm
    parameter["max_growth"] = 162                       # cm
    parameter["b2"] = 48.04
    parameter["b3"] = 0.172
    parameter["mortality_constant"] = 0.467
    parameter["a_zoi_scaling"] = 10
    # Zone of influence is used as proxy for root plate and crown radius
    # Scaling dbh to zone of influence (ZOI) based on eq. 1 in
    # Berger & Hildenbrandt 2000
    geometry["r_bg"] = parameter["a_zoi_scaling"] * geometry["r_stem"]*0.5
    geometry["r_ag"] = geometry["r_bg"]
    # resource module FixedSalinity
    parameter["r_salinity"] = "forman"
    # resource module FON
    parameter["aa"] = 10
    parameter["bb"] = 1
    parameter["fmin"] = 0.1
    return geometry, parameter
