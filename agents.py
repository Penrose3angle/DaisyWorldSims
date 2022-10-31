import math

import mesa
import random


class Daisy(mesa.Agent):
    def __init__(self, unique_id: int, pos, model, albedo: float, remaining_lifespan: int):
        super().__init__(unique_id, model)
        self.pos = pos
        self.albedo = albedo  # fraction (0.0 - 1.0) of energy absorbed as heat from sunlight
        self.remaining_lifespan = remaining_lifespan  # remaining lifespan of the daisy (timestep)

    def step(self):
        self.change_local_temperature()
        self.spawn()
        self.check_lifespan()

    def check_lifespan(self):
        self.remaining_lifespan -= 1
        if self.remaining_lifespan < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def change_local_temperature(self):
        """
        Change the local temperature
        every patch will calculate the temperature at that spot based on
        (1) the energy absorbed by the daisy at that patch and
        (2) the diffusion of 50% of the temperature value at that patch between its neighbors
        :param grid_content:
        :return:
        """
        grid_content = self.model.grid.get_cell_list_contents(self.pos)
        grass = [a for a in grid_content if isinstance(a, GrassPatch)][0]
        absorbed_luminosity = (1 - self.albedo) * self.model.solar_luminosity
        if absorbed_luminosity > 0:
            local_heating = 72 * math.log(absorbed_luminosity) + 80
        else:
            local_heating = 80
        grass.local_temperature = float((grass.local_temperature + local_heating) / 2)

    def spawn(self):
        """
        Random chance of spawning to neighbouring grid based on the local(?) world(?) temperature
        :param grid_content:
        :return:
        """
        # grid_content = self.model.grid.get_cell_list_contents(self.pos)
        # grass = [a for a in grid_content if isinstance(a, GrassPatch)][0]
        # local_temp = grass.local_temperature
        seed_threshold = (
                (0.1457 * self.model.world_temperature) - (0.0032 * (self.model.world_temperature ** 2)) - 0.6443)
        seed = random.random()
        if seed < seed_threshold:
            neighbourhood = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False)
            new_position = self.random.choice(neighbourhood)
            grid_content = self.model.grid.get_cell_list_contents(new_position)
            daisies = [a for a in grid_content if isinstance(a, GrassPatch) is False]
            if len(daisies) == 0:
                daisy = self._create_offspring(new_position)
                self.model.grid.place_agent(daisy, new_position)
                self.model.schedule.add(daisy)

    def _create_offspring(self, new_position):
        raise NotImplementedError


class WhiteDaisy(Daisy):
    def _create_offspring(self, new_position):
        daisy = WhiteDaisy(self.model.next_id(), new_position, self.model, self.albedo, 5)
        return daisy


class BlackDaisy(Daisy):
    def _create_offspring(self, new_position):
        daisy = BlackDaisy(self.model.next_id(), new_position, self.model, self.albedo, 5)
        return daisy


class GrassPatch(mesa.Agent):
    def __init__(self, unique_id, pos, model, local_temperature, albedo):
        """
        Creates a new patch of grass
        Args:
        """
        super().__init__(unique_id, model)
        self.local_temperature = local_temperature
        self.pos = pos
        self.albedo = albedo

    def step(self):
        grid_content = self.model.grid.get_cell_list_contents(self.pos)
        daisies = [a for a in grid_content if isinstance(a, GrassPatch) is False]
        if len(daisies) == 0:
            self.local_temperature = (1 - self.albedo) * self.model.solar_luminosity
