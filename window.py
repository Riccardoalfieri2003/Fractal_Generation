import sys
import pygame
from fractal import DualFractalEngine

pygame.init()
pygame.font.init()

# --- Config ---
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
CANVAS_WIDTH = 750
CANVAS_HEIGHT = 700
SIDEBAR_WIDTH = WINDOW_WIDTH - CANVAS_WIDTH

BG_COLOR = (18, 18, 24)
CANVAS_BG = (25, 26, 35)
SIDEBAR_BG = (32, 34, 46)
PANEL_BORDER = (45, 48, 64)
DRAW_COLOR = (255, 215, 0)
TEXT_COLOR = (220, 225, 235)
SUBTEXT_COLOR = (140, 145, 165)

JULIA_BTN_COLOR = (88, 101, 242)
JULIA_BTN_HOVER = (105, 118, 255)
IFS_BTN_COLOR = (40, 167, 69)
IFS_BTN_HOVER = (55, 185, 85)
CLEAR_BTN_COLOR = (220, 53, 69)
CLEAR_BTN_HOVER = (240, 73, 89)

TITLE_FONT = pygame.font.SysFont("Segoe UI", 22, bold=True)
BODY_FONT = pygame.font.SysFont("Segoe UI", 14)
BTN_FONT = pygame.font.SysFont("Segoe UI", 15, bold=True)


class DrawingApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Dual Mode Fractal Generator")
        self.clock = pygame.time.Clock()

        self.canvas_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
        self.canvas_surface.fill(CANVAS_BG)

        self.is_drawing = False
        self.last_pos = None
        self.drawn_points = []
        self.mode = "DRAW"

        self.fractal_engine = DualFractalEngine(CANVAS_WIDTH, CANVAS_HEIGHT)

        # UI Buttons
        self.btn_julia = pygame.Rect(CANVAS_WIDTH + 20, 120, SIDEBAR_WIDTH - 40, 45)
        self.btn_ifs = pygame.Rect(CANVAS_WIDTH + 20, 175, SIDEBAR_WIDTH - 40, 45)
        self.btn_clear = pygame.Rect(CANVAS_WIDTH + 20, 235, SIDEBAR_WIDTH - 40, 40)

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
                        self.fractal_engine.handle_mouse_down(pos, event.button, self.drawn_points)

                elif event.button == 1:
                    if self.btn_julia.collidepoint(pos) and len(self.drawn_points) > 5:
                        self.mode = "FRACTAL"
                        self.fractal_engine.reset_navigation()
                        self.fractal_engine.generate_julia(self.drawn_points)
                    elif self.btn_ifs.collidepoint(pos) and len(self.drawn_points) > 5:
                        self.mode = "FRACTAL"
                        self.fractal_engine.reset_navigation()
                        self.fractal_engine.generate_ifs(self.drawn_points)
                    elif self.btn_clear.collidepoint(pos):
                        self.clear_canvas()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_drawing = False
                    self.last_pos = None
                    if self.mode == "FRACTAL":
                        self.fractal_engine.handle_mouse_up(event.button, self.drawn_points)

            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
                if self.mode == "DRAW" and self.is_drawing and self.is_on_canvas(pos):
                    if self.last_pos:
                        pygame.draw.aaline(self.canvas_surface, DRAW_COLOR, self.last_pos, pos, 3)
                    self.last_pos = pos
                    self.drawn_points.append(pos)
                elif self.mode == "FRACTAL" and self.is_on_canvas(pos):
                    self.fractal_engine.handle_mouse_motion(pos)

    def is_on_canvas(self, pos):
        return 0 <= pos[0] < CANVAS_WIDTH and 0 <= pos[1] < CANVAS_HEIGHT

    def clear_canvas(self):
        self.canvas_surface.fill(CANVAS_BG)
        self.drawn_points.clear()
        self.mode = "DRAW"
        self.fractal_engine.reset_navigation()

    def draw_ui(self):
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, SIDEBAR_BG, (CANVAS_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, PANEL_BORDER, (CANVAS_WIDTH, 0), (CANVAS_WIDTH, WINDOW_HEIGHT), 2)

        if self.mode == "FRACTAL":
            self.fractal_engine.render(self.canvas_surface)
        self.screen.blit(self.canvas_surface, (0, 0))

        title = TITLE_FONT.render("Fractal Studio", True, TEXT_COLOR)
        sub_text = BODY_FONT.render("Draw stroke & select mode", True, SUBTEXT_COLOR)
        self.screen.blit(title, (CANVAS_WIDTH + 20, 25))
        self.screen.blit(sub_text, (CANVAS_WIDTH + 20, 55))

        status_str = f"Status: {self.mode} MODE"
        status_color = (100, 220, 120) if self.mode == "DRAW" else (255, 180, 50)
        status_txt = BODY_FONT.render(status_str, True, status_color)
        self.screen.blit(status_txt, (CANVAS_WIDTH + 20, 85))

        mouse_pos = pygame.mouse.get_pos()

        # Julia Button
        j_col = JULIA_BTN_HOVER if self.btn_julia.collidepoint(mouse_pos) else JULIA_BTN_COLOR
        pygame.draw.rect(self.screen, j_col, self.btn_julia, border_radius=8)
        j_lbl = BTN_FONT.render("Generate Julia Set", True, (255, 255, 255))
        self.screen.blit(j_lbl, j_lbl.get_rect(center=self.btn_julia.center))

        # IFS Button
        ifs_col = IFS_BTN_HOVER if self.btn_ifs.collidepoint(mouse_pos) else IFS_BTN_COLOR
        pygame.draw.rect(self.screen, ifs_col, self.btn_ifs, border_radius=8)
        ifs_lbl = BTN_FONT.render("Generate IFS Branch", True, (255, 255, 255))
        self.screen.blit(ifs_lbl, ifs_lbl.get_rect(center=self.btn_ifs.center))

        # Clear Button
        clr_col = CLEAR_BTN_HOVER if self.btn_clear.collidepoint(mouse_pos) else CLEAR_BTN_COLOR
        pygame.draw.rect(self.screen, clr_col, self.btn_clear, border_radius=8)
        clr_lbl = BTN_FONT.render("Clear Canvas", True, (255, 255, 255))
        self.screen.blit(clr_lbl, clr_lbl.get_rect(center=self.btn_clear.center))

        # Stats & Nav Info
        pts_text = BODY_FONT.render(f"Stroke Points: {len(self.drawn_points)}", True, SUBTEXT_COLOR)
        self.screen.blit(pts_text, (CANVAS_WIDTH + 20, 295))

        if self.mode == "FRACTAL":
            nav_hdr = BODY_FONT.render(f"Active Mode: {self.fractal_engine.type}", True, TEXT_COLOR)
            pan_txt = BODY_FONT.render("• Drag left-click to Pan", True, SUBTEXT_COLOR)
            zoom_txt = BODY_FONT.render("• Scroll wheel to Zoom", True, SUBTEXT_COLOR)
            self.screen.blit(nav_hdr, (CANVAS_WIDTH + 20, 330))
            self.screen.blit(pan_txt, (CANVAS_WIDTH + 20, 355))
            self.screen.blit(zoom_txt, (CANVAS_WIDTH + 20, 375))

    def run(self):
        while True:
            self.handle_events()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    app = DrawingApp()
    app.run()