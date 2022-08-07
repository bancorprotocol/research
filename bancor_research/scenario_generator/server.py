# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Sets up the interactive visualization server for the Mesa Agent-based simulation."""
from decimal import Decimal

import mesa

# The colors here are taken from Matplotlib's tab10 palette
from bancor_research.scenario_generator.model import BancorSimulation

from bancor_research.scenario_generator.constants import SIMULATION_WHALE_THRESHOLD

from bancor_research.bancor_simulator.v3.spec import DEFAULT_TRADING_FEE, DEFAULT_NETWORK_FEE, DEFAULT_WITHDRAWAL_FEE
from bancor_research.scenario_generator.agents import Trader, LP

RICH_COLOR = "#2ca02c"  # Green
POOR_COLOR = "#d62728"  # Red
MID_COLOR = "#1f77b4"  # Blue
INIT_TRADER_COLOR = "yellow"
INIT_LP_COLOR = "skyblue"


def agent_portrayal(agent: mesa.Agent):
    """
    A CanvasGrid object uses a user-provided portrayal method to generate a
    portrayal for each object. A portrayal is a JSON-ready dictionary which
    tells the relevant JavaScript code (GridDraw.js) where to draw what shape.

    The render method returns a dictionary, keyed on layers, with values as
    lists of portrayals to draw. Portrayals themselves are generated by the
    user-provided portrayal_method, which accepts an object as an input and
    produces a portrayal of it.

    A portrayal as a dictionary with the following structure:
        "x", "y": Coordinates for the cell in which the object is placed.
        "Shape": Can be either "circle", "rect", "arrowHead" or a custom image.
            For Circles:
                "r": The radius, defined as a fraction of cell size. r=1 will
                     fill the entire cell.
                "xAlign", "yAlign": Alignment of the circle within the cell.
                                    Defaults to 0.5 (center).
            For Rectangles:
                "w", "h": The width and height of the rectangle, which are in
                          fractions of cell width and height.
                "xAlign", "yAlign": Alignment of the rectangle within the
                                    cell. Defaults to 0.5 (center).
            For arrowHead:
                "scale": Proportion scaling as a fraction of cell size.
                "heading_x": represents x direction unit vector.
                "heading_y": represents y direction unit vector.
             For an image:
                The image must be placed in the same directory from which the
                server is launched. An image has the attributes "x", "y",
                "scale", "text" and "text_color".
        "Color": The color to draw the shape in; needs to be a valid HTML
                 color, e.g."Red" or "#AA08F8"
        "Filled": either "true" or "false", and determines whether the shape is
                  filled or not.
        "Layer": Layer number of 0 or above; higher-numbered layers are drawn
                 above lower-numbered layers.
        "text": The text to be inscribed inside the Shape. Normally useful for
                showing the unique_id of the agent.
        "text_color": The color to draw the inscribed text. Should be given in
                      conjunction of "text" property.


    Attributes:
        portrayal_method: Function which generates portrayals from objects, as
                          described above.
        grid_height, grid_width: Size of the grid to visualize, in cells.
        canvas_height, canvas_width: Size, in pixels, of the grid visualization
                                     to draw on the client.
        template: "canvas_module.html" stores the module's HTML template.

    """
    if agent is None:
        return

    portrayal = {}

    # update portrayal characteristics for each LP object
    if isinstance(agent, LP):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"

        color = INIT_LP_COLOR

        print("LP ", agent.user_name, agent.profit)

        # set agent color based on savings and loans
        threshold = 90
        lower = 10
        if threshold < agent.profit * 100:
            color = RICH_COLOR
        elif Decimal(lower) < agent.profit * 100 < Decimal(threshold):
            color = MID_COLOR
        elif agent.profit * 100 < Decimal(lower):
            color = POOR_COLOR

        portrayal["Color"] = color

    elif isinstance(agent, Trader):
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5
        portrayal["Layer"] = 1
        portrayal["Filled"] = "true"

        color = INIT_TRADER_COLOR

        print("Trader ", agent.user_name, agent.profit)

        # set agent color based on savings and loans
        threshold = 90
        lower = 10
        if threshold < agent.profit * 100:
            color = RICH_COLOR
        elif Decimal(lower) < agent.profit * 100 < Decimal(threshold):
            color = MID_COLOR
        elif agent.profit * 100 < Decimal(lower):
            color = POOR_COLOR

        portrayal["Color"] = color

    return portrayal


# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "whale_threshold": mesa.visualization.Slider(
        name="Whale Threshold",
        value=float(SIMULATION_WHALE_THRESHOLD),
        min_value=1000,
        max_value=200000,
        step=1000,
        description="Upper End of Random Initial Wallet Amount",
    ),
    "trading_fee": mesa.visualization.Slider(
        name="Trading Fee",
        value=float(DEFAULT_TRADING_FEE),
        min_value=0.001,
        max_value=0.05,
        step=0.001,
        description="Trading Fee",
    ),
    "network_fee": mesa.visualization.Slider(
        name="Network Fee",
        value=float(DEFAULT_NETWORK_FEE),
        min_value=0.001,
        max_value=0.05,
        step=0.001,
        description="Network fee",
    ),
    "withdrawal_fee": mesa.visualization.Slider(
        name="Withdrawal Fee",
        value=float(DEFAULT_WITHDRAWAL_FEE),
        min_value=0.001,
        max_value=0.05,
        step=0.001,
        description="Withdrawal fee",
    ),
}

# set the portrayal function and size of the canvas for visualization
canvas_element = mesa.visualization.CanvasGrid(
    portrayal_method=agent_portrayal,
    grid_width=20,
    grid_height=20,
    # canvas_width=500, canvas_height=500
)

# map data to chart in the ChartModule
chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "Balance > 90%", "Color": RICH_COLOR},
        {"Label": "Balance < 10%", "Color": POOR_COLOR},
        {"Label": "10% < Balance < 90%", "Color": MID_COLOR},
    ]
)

# create instance of Mesa ModularServer
server = mesa.visualization.ModularServer(
    visualization_elements=[canvas_element, chart_element],
    name="Bancor Simulation Model",
    model_params=model_params,
    model_cls=BancorSimulation,
)
