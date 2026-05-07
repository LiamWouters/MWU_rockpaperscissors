import pygame
from typing import Optional
from .UIelement import UIelement

EMPTY_SIZE = (10,10)

class ImageView(UIelement):
    def __init__(self, 
                 pos, 
                 image: Optional[pygame.Surface] = None,
                 show_bounding_box=False, 
                 active=True):
        super().__init__(pos, EMPTY_SIZE[0], EMPTY_SIZE[1], show_bounding_box, active)
        self._surface = None

        self.set_image(image)
    
    def _renderElement(self, screen):
        if self._surface == None:
            return
        screen.blit(self._surface, self.bounding_box.topleft)
    
    def set_image(self, image: Optional[pygame.Surface]):
        self._surface = image
        
        # Resize bounding box based on image
        if self._surface == None:
            self.set_bounding_box_size(EMPTY_SIZE[0], EMPTY_SIZE[1])
        else:
            img_w, img_h = self._surface.get_size()
            self.set_bounding_box_size(img_w, img_h)
        
    def clear(self) -> None:
        """ Remove the current image. """
        self._surface = None
        self.set_bounding_box_size(EMPTY_SIZE[0],EMPTY_SIZE[1])
