from typing import Tuple
import random

import graphic_controller
from kivy.properties import AliasProperty
from kivy.event import EventDispatcher

from geometry.cube_side import CubeSide
from geometry.point import Point
from geometry.enums import SPATIAL_DIRECTION, TRANSFORMATION
from geometry import helpers
from constants import CUBE_SIDE_INITIAL_COLORS_VALUES, CUBE_SIZE, SPACES_X, SPACES_Y, X_OFFSET, Y_OFFSET


class Cube:
    __slots__ = ['position_within_parent_cube', 'size', 'sides', 'transformation_in_progress']

    SIDES_DRAWING_ORDER = [SPATIAL_DIRECTION.TOP, SPATIAL_DIRECTION.RIGHT, SPATIAL_DIRECTION.FRONT]
    SIDES_CALCULATION_ORDER = [
        SPATIAL_DIRECTION.FRONT,
        SPATIAL_DIRECTION.BACK,
        SPATIAL_DIRECTION.TOP,
        SPATIAL_DIRECTION.RIGHT,
    ]

    def __init__(self, position_within_parent_cube: Point, size: int = CUBE_SIZE):
        self.position_within_parent_cube = position_within_parent_cube
        self.size = size

        self.transformation_in_progress = False
        self.sides = {}
        self._set_sides()

    def __contains__(self, point):
        return any(point in side for side in self.drawn_sides)

    @property
    def drawn_sides(self):
        return filter(lambda side: side.drawn_quad, self.sides.values())

    def draw_sides(self):
        # for side_name in self.SIDES_DRAWING_ORDER:
        #     for edge in self.sides[side_name].edges.values():
        #         Line(points=helpers.flatten([point.coords[0] for point in edge]), color=(1,1,1))

        for side_name in self.SIDES_DRAWING_ORDER:
            cube_idx, row_idx, plot_idx = self.position_within_parent_cube.coords_flat

            graphic_controller.GraphicController.adjust_brightness(
                side=side_name,
                initial_color=CUBE_SIDE_INITIAL_COLORS_VALUES[side_name.name],
                cube_idx=cube_idx + 1,
                row_idx=row_idx + 1,
                plot_idx=plot_idx + 1,
            )

            self.sides[side_name].draw_side()

    def _redraw(self):
        for side in filter(lambda x: x.drawn_quad, self.sides.values()):
            side.edit_drawing([0, 0, 0, 100, 100, 100, 100, 0])
            # side.drawn_quad.texture = graphic_controller.GraphicController.make_gradient_texture(height=256)

    def touched(self, touch_button: str):
        if touch_button == 'right':
            self._redraw()
        elif touch_button == 'left':
            self._transform()

    def _transform(self, transformation: TRANSFORMATION = None):
        if transformation is None:
            transformation = random.choice(list(TRANSFORMATION))

        for side in self.drawn_sides:
            side.transform(transformation=transformation)

    def _set_sides(self):
        for side_name in self.SIDES_CALCULATION_ORDER:
            if side_name in [SPATIAL_DIRECTION.FRONT, SPATIAL_DIRECTION.BACK]:
                self.sides[side_name] = CubeSide(
                    side_name=side_name,
                    corners=self._calc_square_corners(side_name=side_name)
                )
                continue

            # corners order should be preserved for correct drawing
            corners = self.sides[SPATIAL_DIRECTION.FRONT].edges[side_name]
            corners += self.sides[SPATIAL_DIRECTION.BACK].edges[side_name][::-1]

            self.sides[side_name] = CubeSide(
                side_name=side_name,
                corners=corners,
            )

    def _calc_initial_point(self, side_name: SPATIAL_DIRECTION = SPATIAL_DIRECTION.FRONT) -> Point:
        """
        returns initial point for a side of a cube based on a cube's position within parent cube
        these x and y transformations were chosen randomly but cubes positions looks more or less ok after them
        """

        depth, width, height = self.position_within_parent_cube.coords_flat

        x = ((8 - width * 2) * SPACES_X + depth * SPACES_X + X_OFFSET)
        y = depth * SPACES_X + (5 + height * SPACES_Y) + Y_OFFSET

        side_to_point_map = {
            SPATIAL_DIRECTION.FRONT: Point(x, y),
            SPATIAL_DIRECTION.BACK: Point(x, y).apply_delta(delta_x=self.size / 2, delta_y=self.size / 2),
        }

        return side_to_point_map[side_name]

    def _calc_square_corners(self, side_name: SPATIAL_DIRECTION):
        initial_point = self._calc_initial_point(side_name=side_name)

        return (
            initial_point,  # bottom left
            initial_point.apply_delta(0, self.size),  # top left
            initial_point.apply_delta(self.size, self.size),  # top right
            initial_point.apply_delta(self.size, 0),  # bottom right
        )