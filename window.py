import sys
import pygame
from fractal import UniversalFractalEngine

pygame.init()
pygame.font.init()

# --- Config ---
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
CANVAS_WIDTH = 750
CANVAS_HEIGHT = 720
SIDEBAR_WIDTH = WINDOW_WIDTH - CANVAS_WIDTH

BG_COLOR = (18, 18, 24)
CANVAS_BG = (25, 26, 35)
SIDEBAR_BG = (32, 34, 46)
PANEL_BORDER = (45, 48, 64)
DRAW_COLOR = (255, 215, 0)
TEXT_COLOR = (220, 225, 235)
SUBTEXT_COLOR = (140, 145, 165)

BTN_COLOR = (52, 58, 70)
BTN_HOVER = (70, 78, 95)
CLEAR_BTN_COLOR = (220, 53, 69)
CLEAR_BTN_HOVER = (240, 73, 89)

TITLE_FONT = pygame.font.SysFont("Segoe UI", 20, bold=True)
BODY_FONT = pygame.font.SysFont("Segoe UI", 13)
BTN_FONT = pygame.font.SysFont("Segoe UI", 13, bold=True)


class DrawingApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Wikipedia Fractal Taxonomy Generator")
        self.clock = pygame.time.Clock()

        self.canvas_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
        self.canvas_surface.fill(CANVAS_BG)

        self.is_drawing = False
        self.last_pos = None
        self.drawn_points = []
        self.mode = "DRAW"

        self.engine = UniversalFractalEngine(CANVAS_WIDTH, CANVAS_HEIGHT)

        # 7 Wikipedia Fractal Category Buttons
        btn_x, btn_w, btn_h = CANVAS_WIDTH + 15, SIDEBAR_WIDTH - 30, 38
        self.buttons = {
            "ESCAPE_TIME": (pygame.Rect(btn_x, 90, btn_w, btn_h), "1. Escape-Time Set"),
            "IFS": (pygame.Rect(btn_x, 135, btn_w, btn_h), "2. IFS Branching"),
            "LSYSTEM": (pygame.Rect(btn_x, 180, btn_w, btn_h), "3. L-System Rewrite"),
            "ATTRACTOR": (pygame.Rect(btn_x, 225, btn_w, btn_h), "4. Strange Attractor"),
            "RANDOM_DLA": (pygame.Rect(btn_x, 270, btn_w, btn_h), "5. Random / DLA"),
            "SUBDIVISION": (pygame.Rect(btn_x, 315, btn_w, btn_h), "6. Finite Subdivision"),
            "SUBDIVISION_LINKS": (pygame.Rect(btn_x, 360, btn_w, btn_h), "7. Subdivision Links"),
        }
        self.btn_clear = pygame.Rect(btn_x, 420, btn_w, 38)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.is_on_canvas(pos):
                    if self.mode == "DRAW" and event.button == 1:
                        self.is_drawing = True
                        self.last_pos = pos
                        self.drawn_points.append(pos)
                    elif self.mode == "FRACTAL":
                        self.engine.handle_mouse_down(pos, event.button, self.drawn_points)

                elif event.button == 1:
                    if len(self.drawn_points) > 5:
                        for mode_key, (rect, _) in self.buttons.items():
                            if rect.collidepoint(pos):
                                self.mode = "FRACTAL"
                                self.engine.reset_navigation()
                                getattr(self.engine, f"generate_{mode_key.lower()}")(self.drawn_points)
                                break
                    if self.btn_clear.collidepoint(pos):
                        self.clear_canvas()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_drawing = False
                    self.last_pos = None
                    if self.mode == "FRACTAL":
                        self.engine.handle_mouse_up(event.button, self.drawn_points)

            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                if self.mode == "DRAW" and self.is_drawing and self.is_on_canvas(pos):
                    if self.last_pos:
                        pygame.draw.aaline(self.canvas_surface, DRAW_COLOR, self.last_pos, pos, 3)
                    self.last_pos = pos
                    self.drawn_points.append(pos)
                elif self.mode == "FRACTAL" and self.is_on_canvas(pos):
                    self.engine.handle_mouse_motion(pos)

    def is_on_canvas(self, pos):
        return 0 <= pos[0] < CANVAS_WIDTH and 0 <= pos[1] < CANVAS_HEIGHT

    def clear_canvas(self):
        self.canvas_surface.fill(CANVAS_BG)
        self.drawn_points.clear()
        self.mode = "DRAW"
        self.engine.reset_navigation()

    def draw_ui(self):
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, SIDEBAR_BG, (CANVAS_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, PANEL_BORDER, (CANVAS_WIDTH, 0), (CANVAS_WIDTH, WINDOW_HEIGHT), 2)

        if self.mode == "FRACTAL":
            self.engine.render(self.canvas_surface)
        self.screen.blit(self.canvas_surface, (0, 0))

        # Title Block
        title = TITLE_FONT.render("Fractal Taxonomy Studio", True, TEXT_COLOR)
        sub_text = BODY_FONT.render("Draw stroke & select generator:", True, SUBTEXT_COLOR)
        self.screen.blit(title, (CANVAS_WIDTH + 15, 20))
        self.screen.blit(sub_text, (CANVAS_WIDTH + 15, 48))

        mouse_pos = pygame.mouse.get_pos()

        # Render 7 Category Buttons
        for mode_key, (rect, label_text) in self.buttons.items():
            col = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
            pygame.draw.rect(self.screen, col, rect, border_radius=6)
            lbl = BTN_FONT.render(label_text, True, (255, 255, 255))
            self.screen.blit(lbl, lbl.get_rect(center=rect.center))

        # Clear Button
        clr_col = CLEAR_BTN_HOVER if self.btn_clear.collidepoint(mouse_pos) else CLEAR_BTN_COLOR
        pygame.draw.rect(self.screen, clr_col, self.btn_clear, border_radius=6)
        clr_lbl = BTN_FONT.render("Clear Drawing", True, (255, 255, 255))
        self.screen.blit(clr_lbl, clr_lbl.get_rect(center=self.btn_clear.center))

        # Status Footer
        pts_text = BODY_FONT.render(f"Stroke Points: {len(self.drawn_points)}", True, SUBTEXT_COLOR)
        self.screen.blit(pts_text, (CANVAS_WIDTH + 15, 480))

        if self.mode == "FRACTAL":
            nav_hdr = BODY_FONT.render(f"Active: {self.engine.mode}", True, TEXT_COLOR)
            pan_txt = BODY_FONT.render("• Drag to Pan around", True, SUBTEXT_COLOR)
            zoom_txt = BODY_FONT.render("• Scroll wheel to Zoom", True, SUBTEXT_COLOR)
            self.screen.blit(nav_hdr, (CANVAS_WIDTH + 15, 510))
            self.screen.blit(pan_txt, (CANVAS_WIDTH + 15, 535))
            self.screen.blit(zoom_txt, (CANVAS_WIDTH + 15, 555))

    def run(self):
        while True:
            self.handle_events()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    app = DrawingApp()
    app.run()