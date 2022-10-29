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
        # Change the local temperature
        grid_content = self.model.grid.get_cell_list_contents(self.pos)
        grass = [a for a in grid_content if isinstance(a, GrassPatch)][0]
        absorbed_luminosity = (1 - self.albedo) * self.model.solar_luminosity
        if absorbed_luminosity > 0:
            local_heating = 72 * math.log(absorbed_luminosity) + 80
        else:
            local_heating = 80
        grass.local_temperature = float((grass.local_temperature + local_heating)/2)

        # Random chance of spawning to neighbouring grid
        seed_threshold = ((0.1457 * self.model.world_temperature) - (0.0032 * (self.model.world_temperature ** 2)) - 0.6443)
        # Successful spawning
        seed = random.random()
        # print(seed, seed_threshold, (seed<seed_threshold))
        if seed < seed_threshold:
            neighbourhood = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False)
            new_position = self.random.choice(neighbourhood)
            daisy = Daisy(
                self.model.next_id(), new_position, self.model, self.albedo, 5
            )
            self.model.grid.place_agent(daisy, new_position)
            self.model.schedule.add(daisy)

        # Use up one timestep
        self.remaining_lifespan -= 1

        # Die of old age - don't put this part first otherwise agent will die but the rest of the code still try to run.
        if self.remaining_lifespan < 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


class WhiteDaisy(Daisy):
    pass


class BlackDaisy(Daisy):
    pass


class GrassPatch(mesa.Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """

    def __init__(self, unique_id, pos, model, local_temperature):
        """
        Creates a new patch of grass
        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(unique_id, model)
        self.local_temperature = local_temperature
        self.pos = pos
