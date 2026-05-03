import pygame, os
from .UIelement import UIelement

class FileView(UIelement):
    def __init__(self, 
                 pos: tuple[int,int], 
                 font,
                 size, # tuple: (width, height) in pixels
                 file_path,
                 preamble="contents:\n",
                 colors={
                     "text": "#cccccc",
                     "bg": "#222222"
                 },
                 show_bounding_box=False):
        super().__init__(pos, size[0], size[1], show_bounding_box=show_bounding_box)
        
        self.font = font
        self.colors = colors
        self.file_path = file_path
        self.preamble = preamble
        
        self.text_surface = pygame.Surface(size)
        self.update_contents()
        
    def _renderElement(self, screen):
        screen.blit(self.text_surface, self.bounding_box.topleft) # Write the text on the top left
        
    def update_contents(self):
        """ Call this method whenever the input of the file changes to update the UIelement """
        contents = ""
        if not os.path.exists(self.file_path):
            contents = f"File: {self.file_path} not found."
        else:
            with open(self.file_path) as f:
                file_contents = f.read().replace(',', '').strip()
                contents = f"{self.preamble}\n{file_contents}"
        
        self.text_surface.fill(self.colors["bg"]) # Draw background
        text_rect = pygame.Rect(5, 5, self.bounding_box.width - 10, self.bounding_box.height - 10) # Create rect holding the text (5 px smaller on each side than bounding box)
        
        drawText(self.text_surface, contents, self.colors["text"], text_rect, self.font, aa=True)

###############
## drawText method source: https://www.pygame.org/wiki/TextWrap
## Slightly altered to support wrapping on '\n'
# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, textFull, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]
    
    split_text = textFull.split('\n')

    for text in split_text:
        while text:
            i = 1

            # determine if the row of text will be outside our area
            if y + fontHeight > rect.bottom:
                break

            # determine maximum width of line
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word      
            if i < len(text): 
                i = text.rfind(" ", 0, i)
            
            # render the line and blit it to the surface
            if bkg:
                image = font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)

            surface.blit(image, (rect.left, y))
            y += fontHeight + lineSpacing

            # remove the text we just blitted
            text = text[i:]

    return textFull
