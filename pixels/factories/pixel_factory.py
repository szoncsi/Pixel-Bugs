from abc import ABC, abstractmethod
from pixels.pixel import Pixel

class PixelFactory(ABC):
    @abstractmethod
    def create_pixel(self, color, width, height):
        pass
