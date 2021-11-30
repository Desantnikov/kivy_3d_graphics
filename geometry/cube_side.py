from typing import Tuple

from kivy.uix.behaviors.button import ButtonBehavior
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import Quad
from kivy.animation import Animation

from shapely.geometry import Polygon

from geometry import helpers
from geometry.point import Point
from geometry.enums import SPATIAL_DIRECTION
from constants import CUBE_SIDE_INITIAL_COLORS_VALUES


class CubeSide:
    INITIAL_COLORS_RGB = CUBE_SIDE_INITIAL_COLORS_VALUES

    def __init__(self, side_name: SPATIAL_DIRECTION, corners: Tuple[Point, ...]):
        self.side_name = side_name

        self.corners = corners
        self.coords = tuple(corner.coords[0] for corner in self.corners)

        self.edges = {
            SPATIAL_DIRECTION.LEFT: (self.corners[0], self.corners[1]),
            SPATIAL_DIRECTION.TOP: (self.corners[1], self.corners[2]),
            SPATIAL_DIRECTION.RIGHT: (self.corners[2], self.corners[3]),
            SPATIAL_DIRECTION.BOTTOM: (self.corners[3], self.corners[0]),
        }

        self.drawn_quad = None
        self.drawn_polygon = None

    def __contains__(self, point):
        return Polygon(self.coords).contains(point)

    def draw(self):
        assert self.drawn_quad is None, 'Trying to draw already drawn figure'

        self.drawn_quad = Quad(points=helpers.flatten(self.coords))#, color=Color(rgb=self.INITIAL_COLORS_RGB[self.side_name.name]))

    def transform(self):
        modified_coord_values = [
            coord + 15
            if idx % 2
            else coord
            for idx, coord in enumerate(helpers.flatten(self.coords))
        ]

        anim = Animation(points=modified_coord_values, duration=0.4, transition='out_back')
        anim += Animation(points=helpers.flatten(self.coords), duration=0.4, transition='in_back')

        anim.start(self.drawn_quad)
