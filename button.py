import pygame

class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
        bg_color=None,
        text_color=(0, 0, 0),
        font=None,
        image_path=None
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font or pygame.font.SysFont(None, 30)

        self.image = None
        if image_path is not None:
            self.image = pygame.image.load(image_path).convert_alpha()
            img_height = int(height * 0.6)
            self.image = pygame.transform.scale(self.image, (width, img_height))

    def draw(self, surface, enabled=True):
        if self.image is not None:
            img = self.image if enabled else self.image.copy()
            if not enabled:
                img.set_alpha(120)
            img_x = self.rect.x + (self.rect.width - img.get_width()) // 2
            surface.blit(img, (img_x, self.rect.y))
        else:
            color = self.bg_color if enabled else (180, 180, 180)
            pygame.draw.rect(surface, color, self.rect, border_radius=10)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=10)

        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(
                centerx=self.rect.centerx,
                bottom=self.rect.bottom - 2
            )
            surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)