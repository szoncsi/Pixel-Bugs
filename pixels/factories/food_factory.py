import random
from pixels.factories.pixel_factory import PixelFactory
from pixels.tree_sap import TreeSap


class FoodFactory(PixelFactory):
    def create_pixel(self, color, diameter, lifespan, screen_width=None, screen_height=None, game_state = None):

        tree_sap = TreeSap(color, diameter, lifespan, screen_width, screen_height, game_state)

        tree_sap.rect.x = random.randrange(screen_width - diameter)
        tree_sap.rect.y = random.randrange(screen_height - diameter)
        return tree_sap