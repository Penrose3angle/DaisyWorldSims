"""
Wolf-Sheep Predation Model
================================
Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import mesa

from scheduler import RandomActivationByTypeFiltered
from agents import Daisy, GrassPatch, WhiteDaisy, BlackDaisy


class Gaia(mesa.Model):
    """
    Gaia Model
    """
    def __init__(self,
                 initial_temp=25.0,
                 initial_black=100,
                 initial_white=100,
                 solar_luminosity=1.4,  # choices [0,8, 0.6, 1.0, 1.4]
                 white_albedo=0.75,
                 black_albedo=0.25,
                 surface_albedo=0.4,
                 width=20,
                 height=20,
                 verbose=False):
        """
        Create Gaia Model with the following parameters.
        :param initial_temp:
        :param initial_black:
        :param initial_white:
        :param solar_luminosity:
        """
        super().__init__()
        # Parameters
        self.initial_temp = initial_temp
        self.world_temperature = initial_temp
        self.initial_black = initial_black
        self.initial_white = initial_white
        self.solar_luminosity = solar_luminosity
        self.white_albedo = white_albedo
        self.black_albedo = black_albedo
        self.surface_albedo = surface_albedo
        self.width = width
        self.height = height
        self.verbose = verbose

        # Declare a Scheduler
        self.schedule = RandomActivationByTypeFiltered(self)
        # Declare a World type (grid)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # Declare a Data Collector
        self.datacollector = mesa.DataCollector(
            {
                "Black Daisies": lambda m: m.schedule.get_type_count(BlackDaisy),
                "White Daisies": lambda m: m.schedule.get_type_count(WhiteDaisy),
                "Total Daisies": lambda m: m.schedule.get_type_count(BlackDaisy) + m.schedule.get_type_count(WhiteDaisy),
                "World Temp": lambda m: m.schedule.get_mean_temp(),
                # "Grass Temp": lambda m: m.schedule.get_type_count(GrassPatch, lambda x: x.temp),
            }
        )

        # Populating the world
        self.create_grass_patch()
        self.create_daisies(WhiteDaisy, self.initial_white, self.white_albedo)
        self.create_daisies(BlackDaisy, self.initial_black, self.black_albedo)

        # Setting
        self.running = True
        # Collect initial data from the model
        self.datacollector.collect(self)

    def create_grass_patch(self):
        for _agent, x, y in self.grid.coord_iter():
            grass = GrassPatch(self.next_id(), (x, y), self, self.initial_temp, self.surface_albedo)
            self.grid.place_agent(grass, (x, y))
            self.schedule.add(grass)

    def create_daisies(self, agent_type, initial_num, albedo):
        """Create Daisy agents"""
        for i in range(initial_num):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            daisies = [a for a in self.grid.get_cell_list_contents((x, y)) if isinstance(a, GrassPatch) is False]
            if len(daisies) == 0:
                remaining_lifespan = 5
                daisy = agent_type(self.next_id(), (x, y), self, albedo, remaining_lifespan)
                self.grid.place_agent(daisy, (x, y))
                self.schedule.add(daisy)

    def step(self):
        """
        Walk the schedule one step and collect the data from the model
        :return:
        """
        self.schedule.step()
        # Collect data at each step
        self.datacollector.collect(self)
        # Update the world temperature
        self.world_temperature = self.schedule.get_mean_temp()
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_type_count(BlackDaisy),
                    self.schedule.get_type_count(WhiteDaisy),
                    # self.schedule.get_type_count(GrassPatch, lambda x: x.fully_grown),
                ]
            )

    def run_model(self, step_count=200):
        """
        Run the model for the specified number of steps
        :param step_count:
        :return:
        """
        if self.verbose:
            print("Initial black daisy number: ", self.schedule.get_type_count(BlackDaisy))
            print("Initial white daisy number: ", self.schedule.get_type_count(WhiteDaisy))
            print("World Burn", self.schedule.get_mean_temp())

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print("Final black daisy number: ", self.schedule.get_type_count(BlackDaisy))
            print("Final white daisy number: ", self.schedule.get_type_count(WhiteDaisy))
            print("World Burn", self.schedule.get_mean_temp())


import random
random.seed = 32
empty_model = Gaia()
empty_model.verbose = True
empty_model.run_model(10)