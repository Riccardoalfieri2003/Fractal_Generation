import numpy as np
import pygame


class DualFractalEngine:
    def __init__(self, canvas_width, canvas_height):
        self.width = canvas_width
        self.height = canvas_height

        # Engine Type: "IFS" or "JULIA"
        self.type = "JULIA"

        # IFS State
        self.points_by_depth = []

        # Escape-Time Julia State
        self.center_x = 0.0
        self.center_y = 0.0
        self.scale = 3.0
        self.fractal_surface = None

        # General Navigation
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.is_panning = False
        self.pan_start = (0, 0)

    def reset_navigation(self):
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.center_x = 0.0
        self.center_y = 0.0
        self.scale = 3.0

    # ==================== ENGINE 1: IFS (Branching/Fern) ====================
    def compute_ifs_transforms(self, user_points):
        pts = np.array(user_points, dtype=np.float64)
        if len(pts) < 10:
            return []

        indices = np.linspace(0, len(pts) - 1, 6, dtype=int)
        key_pts = pts[indices]

        p_start, p_end = key_pts[0], key_pts[-1]
        main_vector = p_end - p_start
        main_len = np.linalg.norm(main_vector) + 1e-6
        main_angle = np.arctan2(main_vector[1], main_vector[0])

        transforms = []
        for i in range(len(key_pts) - 1):
            sub_start, sub_end = key_pts[i], key_pts[i + 1]
            sub_vec = sub_end - sub_start
            sub_len = np.linalg.norm(sub_vec)

            scale = min((sub_len / main_len) * 1.3, 0.75)
            angle = np.arctan2(sub_vec[1], sub_vec[0]) - main_angle

            cos_a, sin_a = np.cos(angle), np.sin(angle)
            matrix = np.array([[scale * cos_a, -scale * sin_a], [scale * sin_a, scale * cos_a]])
            translation = sub_start - np.dot(matrix, p_start)
            transforms.append((matrix, translation))

        return transforms

    def generate_ifs(self, user_points, max_depth=5):
        self.type = "IFS"
        self.points_by_depth = []
        transforms = self.compute_ifs_transforms(user_points)
        if not transforms:
            return

        current_pts = np.array(user_points, dtype=np.float64)
        self.points_by_depth.append(current_pts)

        for depth in range(1, max_depth + 1):
            if len(current_pts) > 15000:
                sub_indices = np.random.choice(len(current_pts), 15000, replace=False)
                active_pts = current_pts[sub_indices]
            else:
                active_pts = current_pts

            next_pts_list = []
            for matrix, trans in transforms:
                next_pts_list.append(np.dot(active_pts, matrix.T) + trans)

            current_pts = np.vstack(next_pts_list)
            self.points_by_depth.append(current_pts)

    # ==================== ENGINE 2: JULIA (Escape-Time) ====================
    def generate_julia(self, user_points, max_iter=50):
        self.type = "JULIA"
        if len(user_points) < 5:
            return

        pts = np.array(user_points, dtype=np.float64)
        norm_x = (pts[:, 0] - self.width / 2.0) / (self.width / 2.0)
        norm_y = (pts[:, 1] - self.height / 2.0) / (self.height / 2.0)
        c_samples = norm_x + 1j * norm_y

        indices = np.linspace(0, len(c_samples) - 1, 5, dtype=int)
        c_seeds = c_samples[indices]

        xmin = self.center_x - self.scale / 2.0
        xmax = self.center_x + self.scale / 2.0
        ymin = self.center_y - (self.scale * self.height / self.width) / 2.0
        ymax = self.center_y + (self.scale * self.height / self.width) / 2.0

        res_x, res_y = self.width // 2, self.height // 2
        x = np.linspace(xmin, xmax, res_x)
        y = np.linspace(ymin, ymax, res_y)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y

        escape_grid = np.zeros(Z.shape, dtype=float)
        mask = np.ones(Z.shape, dtype=bool)

        c_main = np.mean(c_seeds)
        c_pert = c_seeds[0] - c_seeds[-1]

        for i in range(1, max_iter + 1):
            if not np.any(mask):
                break
            Z[mask] = Z[mask] ** 2 + c_main + (0.1 * c_pert / (Z[mask] + 1e-6))
            escaped = np.abs(Z) > 4.0
            newly_escaped = escaped & mask
            escape_grid[newly_escaped] = i - np.log2(np.log(np.maximum(np.abs(Z[newly_escaped]), 1.0)) + 1e-5)
            mask[escaped] = False

        norm_iter = escape_grid / max_iter
        R = np.clip(np.sin(norm_iter * np.pi * 3.5 + 0.5) * 255, 0, 255)
        G = np.clip(np.sin(norm_iter * np.pi * 3.0 + 1.2) * 200 + 45, 0, 255)
        B = np.clip(np.cos(norm_iter * np.pi * 2.5) * 255, 0, 255)

        rgb = np.dstack((R, G, B)).astype(np.uint8)
        raw_surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        self.fractal_surface = pygame.transform.smoothscale(raw_surf, (self.width, self.height))

    # ==================== UNIFIED RENDERING & NAV ====================
    def render(self, surface):
        surface.fill((25, 26, 35))
        
        if self.type == "JULIA" and self.fractal_surface is not None:
            surface.blit(self.fractal_surface, (0, 0))

        elif self.type == "IFS" and self.points_by_depth:
            cx, cy = self.width / 2.0, self.height / 2.0
            total_depths = len(self.points_by_depth)

            for depth, pts in enumerate(self.points_by_depth):
                transformed = (pts - [cx, cy]) * self.zoom + [cx + self.offset_x, cy + self.offset_y]
                valid = (
                    (transformed[:, 0] >= 0) & (transformed[:, 0] < self.width) &
                    (transformed[:, 1] >= 0) & (transformed[:, 1] < self.height)
                )
                vis_pts = transformed[valid].astype(int)
                
                t = depth / max(1, total_depths - 1)
                color = (int(255 * (1 - 0.7 * t)), int(215 * (1 - t)), int(255 * t))
                radius = max(1, int(3 - depth * 0.4))

                for pt in vis_pts:
                    pygame.draw.circle(surface, color, (pt[0], pt[1]), radius)

    def handle_mouse_down(self, pos, button, user_points):
        if button == 1:
            self.is_panning = True
            self.pan_start = pos
        elif button == 4:  # Zoom In
            if self.type == "JULIA":
                self.scale *= 0.8
                self.generate_julia(user_points)
            else:
                self.zoom *= 1.15
        elif button == 5:  # Zoom Out
            if self.type == "JULIA":
                self.scale /= 0.8
                self.generate_julia(user_points)
            else:
                self.zoom /= 1.15

    def handle_mouse_up(self, button, user_points):
        if button == 1 and self.is_panning:
            self.is_panning = False
            if self.type == "JULIA":
                self.generate_julia(user_points)

    def handle_mouse_motion(self, pos):
        if self.is_panning:
            dx = pos[0] - self.pan_start[0]
            dy = pos[1] - self.pan_start[1]
            if self.type == "JULIA":
                self.center_x -= (dx / self.width) * self.scale
                self.center_y -= (dy / self.height) * (self.scale * self.height / self.width)
            else:
                self.offset_x += dx
                self.offset_y += dy
            self.pan_start = pos