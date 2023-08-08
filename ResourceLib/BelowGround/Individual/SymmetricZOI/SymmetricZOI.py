#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@date: 2022-Today
@author: marie-christin.wimmler@tu-dresden.de based on SimpleAsymmetricZOI
by ronny.peters@tu-dresden.de
"""

import numpy as np
from ResourceLib import ResourceModel


class SymmetricZOI(ResourceModel):
    ## SymmetricZOI case for below ground competition concept. Symmetric
    #  Zone Of Influence with plants occupying the same node of the grid share
    #  the below-ground resource of this node equally (BETTINA geometry of a
    #  plant assumed). See Peters 2017: ODD protocol of the model BETTINA IBM\n
    #  @param Tags to define SimpleAsymmetricZOI: see tag documentation
    #  @date: 2019 - Today
    def __init__(self, args):
        case = args.find("type").text
        print("Initiate belowground competition of type " + case + ".")
        self.getInputParameters(args)
        super().makeGrid()

    ## This functions prepares arrays for the competition
    #  concept. In the SymmetricZOI concept, plants geometric measures
    #  are saved in simple lists and the timestepping is updated. \n
    #  @param t_ini - initial time for next timestep \n
    #  @param t_end - end time for next timestep
    def prepareNextTimeStep(self, t_ini, t_end):
        self.xe = []
        self.ye = []
        self.r_root = []
        self.t_ini = t_ini
        self.t_end = t_end

    ## Before being able to calculate the resources, all plant entities need
    #  to be added with their current implementation for the next timestep.
    #  @param plant
    def addPlant(self, plant):
        x, y = plant.getPosition()
        geometry = plant.getGeometry()
        if geometry["r_root"] < (self._mesh_size * 1 / 2**0.5):
            print("WARNING: mesh too course for below-ground module!")
            print("Please refine mesh or increase initial root radius above " +
                  str(self._mesh_size) + "m !")
        if not ((self._x_1 < x < self._x_2) and (self._y_1 < y < self._y_2)):
            raise ValueError("""It appears as a plant is located outside of the
                             domain, where BC is defined. Please check domains
                             in project file!!""")
        self.xe.append(x)
        self.ye.append(y)
        self.r_root.append(geometry["r_root"])

    ## This function returns the BelowgroundResources calculated in the
    #  subsequent timestep.\n
    #  @return: np.array with $N_plant$ scalars
    def calculateBelowgroundResources(self):
        # Numpy array of shape [res_x, res_y, n_plants]
        distance = (((self.my_grid[0][:, :, np.newaxis] -
                      np.array(self.xe)[np.newaxis, np.newaxis, :])**2 +
                     (self.my_grid[1][:, :, np.newaxis] -
                      np.array(self.ye)[np.newaxis, np.newaxis, :])**2)**0.5)
        min_distance = np.min(distance)

        # Array of shape distance [res_x, res_y, n_plants], indicating which
        # cells are occupied by plant root plates
        root_radius = np.array(self.r_root)
        # If root radius < mesh size, set it to mesh size
        root_radius[np.where(root_radius < min_distance)] = min_distance
        plants_present = root_radius[np.newaxis, np.newaxis, :] >= distance

        # Count all nodes, which are occupied by plants
        # returns array of shape [n_plants]
        # BETTINA ODD 2017: variable 'countbelow'
        plant_counts = plants_present.sum(axis=(0, 1))

        # Calculate reciprocal of cell-own variables (array to count wins)
        # BETTINA ODD 2017: variable 'compete_below'
        # [res_x, res_y]
        plants_present_reci = 1. / plants_present.sum(axis=-1)

        # Sum up wins of each plant = plants_present_reci[plant]
        n_plants = len(plants_present[0, 0, :])
        plant_wins = np.zeros(n_plants)
        for i in range(n_plants):
            plant_wins[i] = np.sum(plants_present_reci[np.where(
                plants_present[:, :, i])])
        self.belowground_resources = plant_wins / plant_counts

    def getInputParameters(self, args):
        tags = {
            "prj_file": args,
            "required": ["type", "domain", "x_1", "x_2", "y_1", "y_2", "x_resolution", "y_resolution"]
        }
        super().getInputParameters(**tags)
        self._x_1 = self.x_1
        self._x_2 = self.x_2
        self._y_1 = self.y_1
        self._y_2 = self.y_2
        self.x_resolution = int(self.x_resolution)
        self.y_resolution = int(self.y_resolution)
