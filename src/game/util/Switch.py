import pygame
from .UIelement import UIelement

class Switch(UIelement):
    def __init__(self, 
                 pos: tuple[int,int], 
                 font,
                 slider_size,
                 size=(None, None), # Or tuple: (width, height) in pixels 
                 textPaddingX=5,
                 option1text="LeftOption",
                 option2text=None,
                 start_state=False,
                 colors={
                     "bg_off": "#777777",
                     "bg_on": "#5684D8",
                     "circle": "#ffffff",
                     "text_default": "#cccccc",
                     "text_hover": "#555555"
                 },
                 show_bounding_box=False):
        super().__init__(pos, size[0], size[1], show_bounding_box=show_bounding_box)
        
        self.font = font
        self.colors = colors
        self.option1_raw = option1text
        self.option2_raw = option2text
        self.state = start_state # False is Left, True is Right
        
        # Main slider bg
        self.slider_bg_rect = pygame.Rect(0, 0, slider_size[0], slider_size[1])
        self.slider_bg_rect.center = self.bounding_box.center
        
        # Text options
        self.option1_text = self.font.render(option1text, True, self.colors["text_default"])
        self.opt1_rect = self.option1_text.get_rect(midright=(self.slider_bg_rect.left - textPaddingX, self.bounding_box.centery))
        if self.option2_raw != None:
            self.option2_text = self.font.render(option2text, True, self.colors["text_default"])
            self.opt2_rect = self.option2_text.get_rect(midleft=(self.slider_bg_rect.right + textPaddingX, self.bounding_box.centery))
        else:
            self.option2_text = None
            self.opt2_rect = None
        
        # dynamic resizing of bounding box
        if size[0] is None or size[1] is None:
            text1_w, text1_h = self.opt1_rect.size

            if self.option2_text:
                text2_w, text2_h = self.opt2_rect.size
                largest_w = max(text1_w, text2_w) + (2 * textPaddingX)

                full_width = (2 * largest_w) + slider_size[0]
                full_height = max(text1_h, text2_h, slider_size[1])
            else:
                # single label layout
                full_width = text1_w + textPaddingX + slider_size[0]
                full_height = max(text1_h, slider_size[1])

            self.set_bounding_box_size(full_width, full_height)
            
        if self.option2_text:
            # Center slider
            self.slider_bg_rect.center = self.bounding_box.center
            self.opt1_rect.midright = (self.slider_bg_rect.left - textPaddingX, self.bounding_box.centery)
            self.opt2_rect.midleft = (self.slider_bg_rect.right + textPaddingX, self.bounding_box.centery)

        else:
            # Place text on the left inside the bounding box
            self.opt1_rect.midleft = (self.bounding_box.left + textPaddingX, self.bounding_box.centery)
            # Place slider to the right inside the bounding box
            self.slider_bg_rect.midright = (self.bounding_box.right - textPaddingX, self.bounding_box.centery)
    
    def _renderElement(self, screen):
        self._update_color()
        
        # slider background
        current_bg = self.colors["bg_on"] if self.state else self.colors["bg_off"]
        pygame.draw.rect(screen, current_bg, self.slider_bg_rect, border_radius=self.slider_bg_rect.height//2)
        
        # slider circle
        circle_radius = (self.slider_bg_rect.height // 2) - 3
        circle_x = (self.slider_bg_rect.right - circle_radius - 3) if self.state else (self.slider_bg_rect.left + circle_radius + 3)
        pygame.draw.circle(screen, self.colors["circle"], (circle_x, self.slider_bg_rect.centery), circle_radius)
        
        # Draw options
        screen.blit(self.option1_text, self.opt1_rect)
        if self.option2_text:
            screen.blit(self.option2_text, self.opt2_rect)
    
    def _update_color(self):
        mousePos = pygame.mouse.get_pos()
        if self.bounding_box.collidepoint(mousePos):
            self.option1_text = self.font.render(self.option1_raw, True, self.colors.get("text_hover", "#ffffff"))
            if self.option2_text:
                self.option2_text = self.font.render(self.option2_raw, True, self.colors.get("text_hover", "#ffffff"))
        else:
            self.option1_text = self.font.render(self.option1_raw, True, self.colors.get("text_default", "#ffffff"))
            if self.option2_text:
                self.option2_text = self.font.render(self.option2_raw, True, self.colors.get("text_default", "#ffffff"))
            
    def switch(self):
        self.state = not self.state
