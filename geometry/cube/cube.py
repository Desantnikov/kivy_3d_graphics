from kivy.graphics import Color

from geometry.cube.cube_side import CubeSide
from geometry.point import Point
from geometry.cube.enums import SPATIAL_DIRECTION
from geometry import helpers


class Cube:
    SIDES_DRAWING_ORDER = [SPATIAL_DIRECTION.TOP, SPATIAL_DIRECTION.RIGHT, SPATIAL_DIRECTION.FRONT]
    SIDES_CALCULATION_ORDER = [
        SPATIAL_DIRECTION.FRONT,
        SPATIAL_DIRECTION.BACK,
        SPATIAL_DIRECTION.TOP,
        SPATIAL_DIRECTION.RIGHT,
    ]

    def __init__(self, front_side_initial_point: Point, size: int, position_within_parent_cube: Point):
        self.position_within_parent_cube = position_within_parent_cube
        self.size = size

        # back side initial point == center of front side
        back_side_initial_point = front_side_initial_point.apply_delta(
            delta_x=self.size / 2,
            delta_y=self.size / 2,
        )

        self.sides_initial_points = {
            SPATIAL_DIRECTION.FRONT: front_side_initial_point,
            SPATIAL_DIRECTION.BACK: back_side_initial_point,
        }

        self.sides = {}
        for side_name in self.SIDES_CALCULATION_ORDER:
            self.sides[side_name] = self.calc_side(side_name)

    def __contains__(self, point):
        return any([point in side for side in self.sides.values()])

    @property
    def drawn_sides(self):
        return list(filter(lambda side: side.drawn_quad is not None, self.sides.values()))

    def calc_side(self, side_name: SPATIAL_DIRECTION) -> CubeSide:
        if side_name in [SPATIAL_DIRECTION.FRONT, SPATIAL_DIRECTION.BACK]:
            initial_point = self.sides_initial_points[side_name]
            corners = helpers.calc_square_corners(initial_point, self.size)
            return CubeSide(side_name=side_name, corners=corners)

        # if not FRONT/BACK side - just choose already calculated corners according to side position
        corners = self.sides[SPATIAL_DIRECTION.FRONT].edges[side_name]
        corners += self.sides[SPATIAL_DIRECTION.BACK].edges[side_name][::-1]  # reversed order is necessary for drawing
        return CubeSide(side_name=side_name, corners=corners)

    def draw(self):
        for side_name in self.SIDES_DRAWING_ORDER:
            cube_idx, row_idx, plot_idx = self.position_within_parent_cube.coords[0]

            shadow_multiplier = helpers.get_side_shadow_multiplier(side_name, plot_idx, row_idx, cube_idx)
            color_with_shadow = helpers.adjust_color_brightness(side_name, shadow_multiplier)

            Color(rgb=color_with_shadow)

            self.sides[side_name].draw()

    def transform(self):
        for side in self.drawn_sides:
            side.transform()


