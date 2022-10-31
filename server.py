from typing import Dict

import mesa

from agents import GrassPatch, WhiteDaisy, BlackDaisy
from model import Gaia

# Japanese Garden color palette created by mejalisa that consists
# beige, sand, cream, black, red
# #ede1b1,#cdb79e,#fafad2,#2e2e2e,#8b0000 colors.


def daisy_portrayal(agent) -> Dict:
    if agent is None:
        return

    portrayal = {}

    if type(agent) is WhiteDaisy:
        portrayal = {
            "Shape": "circle",
            "Color": "#fafad2",
            "Filled": "true",
            "Layer": 1,
            "r": 0.5,
            'remaining_lifespan': agent.remaining_lifespan
        }

    elif type(agent) is BlackDaisy:
        portrayal = {
            "Shape": "circle",
            "Color": "#2e2e2e",
            "Filled": "true",
            "Layer": 1,
            "r": 0.5,
            'remaining_lifespan': agent.remaining_lifespan
        }

    elif type(agent) is GrassPatch:
        portrayal["Local Temp"] = round(agent.local_temperature, 1)
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        if agent.local_temperature >= 25:
            portrayal["Color"] = '#8b0000'
        else:
            portrayal["Color"] = '#283618'

    return portrayal


def get_text_status(model):
    return f"White Daisy: {model.schedule.get_type_count(WhiteDaisy)}, " \
           f"Black Daisy: {model.schedule.get_type_count(BlackDaisy)}, " \
           f"World Temperature: {round(model.schedule.get_mean_temp(), 2)}"


canvas_element = mesa.visualization.CanvasGrid(daisy_portrayal, 20, 20, 500, 500)
chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "White Daisies", "Color": "#AA0000"},
        {"Label": "Black Daisies", "Color": "#666666"},
    ],
    data_collector_name='datacollector'
)

chart_element_2 = mesa.visualization.ChartModule(
    [
        {"Label": "World Temp", "Color": "#AA0000"},
        # {"Label": "Black Daisies", "Color": "#666666"},
    ],
    data_collector_name='datacollector'
)

model_params = {
    # The following line is an example to showcase StaticText.
    "title": mesa.visualization.StaticText("Parameters:"),
    ''
    'initial_temp': mesa.visualization.Slider("Initial Temperature", 25, 1, 50),
    'initial_white': mesa.visualization.Slider("Initial White Daisies", 50, 0, 100),
    'initial_black': mesa.visualization.Slider("Initial Black Daisies", 50, 0, 100),
    'solar_luminosity': mesa.visualization.Slider("Solar Luminosity", 1.0, 0.6, 1.4, 0.1, description='How much energy a daisy can absorb'),

    # "grass": mesa.visualization.Checkbox("Grass Enabled", True),
}

# arguments: Model, [canvas_element, chart_element], <Title>, model_params (sidebar)
server = mesa.visualization.ModularServer(
    Gaia,
    [canvas_element, get_text_status, chart_element, chart_element_2],
    "Daisy World Simulation",
    model_params
)
server.port = 8521
