from pixels.bug import Bug
from pixels.factories.pixel_factory import PixelFactory

class BugFactory(PixelFactory):
    def create_pixel(self, color, width, height, screen_width, screen_height, game_state, block_size):
            bug = Bug(color, width, height, screen_width, screen_height, game_state, block_size)
            return bug