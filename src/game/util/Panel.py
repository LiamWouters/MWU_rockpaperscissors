import pygame
from .UIelement import UIelement

class Panel(UIelement):
    def __init__(self, 
                 elements: list[UIelement],
                 x_padding: int = 10,
                 y_padding: int = 10,
                 active=True):
        super().__init__((0, 0), 10, 10, show_bounding_box=False, show_bg=True, active=active, z_layer=0)
        
        self.elements: list[UIelement] = elements
        self.x_padding: int = x_padding
        self.y_padding: int = y_padding
        
        self.bg_color = "#1d232b"
        
        self.recalculate_layout()

    def recalculate_layout(self):
        """Calculates size and center based on children's bounding boxes."""
        if not self.elements:
            return
        
        # Create the encompassing bounding box
        combined_rect = self.elements[0].bounding_box.copy()    # get first bounding box
        for e in self.elements[1:]:
            combined_rect.union_ip(e.bounding_box)             # join the others onto it
        
        # Apply padding
        combined_rect.inflate_ip(self.x_padding * 2, self.y_padding * 2)
        
        # Replace bounding box
        self.bounding_box = combined_rect
        
    def _renderElement(self, screen):
        self.recalculate_layout()
