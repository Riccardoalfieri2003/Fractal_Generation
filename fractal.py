import random
import numpy as np
import pygame


class UniversalFractalEngine:
    def __init__(self, canvas_width, canvas_height):
        self.width = canvas_width
        self.height = canvas_height

        self.mode = "ESCAPE_TIME"
        self.points_by_depth = []
        self.line_segments_by_depth = []
        self.fractal_surface = None

        # Navigation Controls
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.center_x = 0.0
        self.center_y = 0.0
        self.scale = 3.0

        self.is_panning = False
        self.pan_start = (0, 0)

    def reset_navigation(self):
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.center_x = 0.0
        self.center_y = 0.0
        self.scale = 3.0

    # 1. ESCAPE-TIME FRACTALS (Julia / Burning Ship hybrid)
    # 1. ESCAPE-TIME FRACTALS (Pure Classical Julia Set)
    def generate_escape_time(self, user_points, max_iter=50):
        self.mode = "ESCAPE_TIME"
        if len(user_points) < 5:
            return

        # Map drawing stroke into complex numbers
        pts = np.array(user_points, dtype=np.float64)
        norm_x = (pts[:, 0] - self.width / 2.0) / (self.width / 2.0)
        norm_y = (pts[:, 1] - self.height / 2.0) / (self.height / 2.0)
        c_samples = norm_x + 1j * norm_y

        # Pick complex constant 'c' directly from the stroke centroid
        c = np.mean(c_samples)

        # Build complex coordinate grid
        xmin, xmax = self.center_x - self.scale / 2.0, self.center_x + self.scale / 2.0
        ymin = self.center_y - (self.scale * self.height / self.width) / 2.0
        ymax = self.center_y + (self.scale * self.height / self.width) / 2.0

        res_x, res_y = self.width // 2, self.height // 2
        x = np.linspace(xmin, xmax, res_x)
        y = np.linspace(ymin, ymax, res_y)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y

        escape_grid = np.zeros(Z.shape, dtype=float)
        mask = np.ones(Z.shape, dtype=bool)

        # Classical Julia recurrence: Z = Z^2 + c
        for i in range(1, max_iter + 1):
            if not np.any(mask):
                break
            Z[mask] = Z[mask] ** 2 + c

            escaped = np.abs(Z) > 4.0
            newly_escaped = escaped & mask
            escape_grid[newly_escaped] = i - np.log2(
                np.log(np.maximum(np.abs(Z[newly_escaped]), 1.0)) + 1e-5
            )
            mask[escaped] = False

        # Gradient Color Mapping (Gold/Copper to Oceanic Blue)
        norm_iter = escape_grid / max_iter
        R = np.clip(np.sin(norm_iter * np.pi * 3.5 + 0.5) * 255, 0, 255)
        G = np.clip(np.sin(norm_iter * np.pi * 3.0 + 1.2) * 200 + 45, 0, 255)
        B = np.clip(np.cos(norm_iter * np.pi * 2.5) * 255, 0, 255)

        rgb = np.dstack((R, G, B)).astype(np.uint8)
        raw_surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        self.fractal_surface = pygame.transform.smoothscale(
            raw_surf, (self.width, self.height)
        )

    # 2. ITERATED FUNCTION SYSTEM (IFS)
    def generate_ifs(self, user_points, max_depth=5):
        self.mode = "IFS"
        self.points_by_depth = []

        pts = np.array(user_points, dtype=np.float64)
        if len(pts) < 10:
            return

        indices = np.linspace(0, len(pts) - 1, 6, dtype=int)
        key_pts = pts[indices]
        p_start, p_end = key_pts[0], key_pts[-1]
        main_vector = p_end - p_start
        main_len = np.linalg.norm(main_vector) + 1e-6
        main_angle = np.arctan2(main_vector[1], main_vector[0])

        transforms = []
        for i in range(len(key_pts) - 1):
            sub_vec = key_pts[i + 1] - key_pts[i]
            scale = min((np.linalg.norm(sub_vec) / main_len) * 1.3, 0.75)
            angle = np.arctan2(sub_vec[1], sub_vec[0]) - main_angle
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            matrix = np.array([[scale * cos_a, -scale * sin_a], [scale * sin_a, scale * cos_a]])
            trans = key_pts[i] - np.dot(matrix, p_start)
            transforms.append((matrix, trans))

        current_pts = pts
        self.points_by_depth.append(current_pts)

        for _ in range(max_depth):
            active_pts = (
                current_pts[np.random.choice(len(current_pts), 15000, replace=False)]
                if len(current_pts) > 15000
                else current_pts
            )
            next_pts = [np.dot(active_pts, m.T) + t for m, t in transforms]
            current_pts = np.vstack(next_pts)
            self.points_by_depth.append(current_pts)

    # 3. L-SYSTEMS (Branching string rewrite)
    def generate_lsystem(self, user_points, max_depth=4):
        self.mode = "LSYSTEM"
        self.line_segments_by_depth = []

        pts = np.array(user_points, dtype=np.float64)
        if len(pts) < 2:
            return

        # Derive initial angle and segment length from user stroke
        stroke_vec = pts[-1] - pts[0]
        angle_step = np.radians(np.degrees(np.arctan2(stroke_vec[1], stroke_vec[0])) % 45 + 15)

        # L-System Grammar: Plant rule
        axiom = "F"
        rule = "F[+F]F[-F]F"
        string = axiom
        for _ in range(max_depth):
            string = string.replace("F", rule)

        segments = []
        stack = []
        pos = np.array([self.width / 2.0, self.height - 50], dtype=float)
        dir_angle = -np.pi / 2.0
        length = 12.0

        for char in string:
            if char == "F":
                new_pos = pos + np.array([np.cos(dir_angle), np.sin(dir_angle)]) * length
                segments.append((pos.copy(), new_pos.copy()))
                pos = new_pos
            elif char == "+":
                dir_angle += angle_step
            elif char == "-":
                dir_angle -= angle_step
            elif char == "[":
                stack.append((pos.copy(), dir_angle))
            elif char == "]":
                pos, dir_angle = stack.pop()

        self.line_segments_by_depth.append(segments)

    # 4. STRANGE ATTRACTORS (Clifford Attractor)
    def generate_attractor(self, user_points, num_points=60000):
        self.mode = "ATTRACTOR"
        self.points_by_depth = []

        pts = np.array(user_points, dtype=np.float64)
        if len(pts) < 4:
            return

        # Map stroke parameters to Clifford Attractor variables (a, b, c, d)
        a = (pts[0, 0] / self.width) * 4.0 - 2.0
        b = (pts[len(pts) // 3, 1] / self.height) * 4.0 - 2.0
        c = (pts[(2 * len(pts)) // 3, 0] / self.width) * 4.0 - 2.0
        d = (pts[-1, 1] / self.height) * 4.0 - 2.0

        attractor_pts = np.zeros((num_points, 2), dtype=float)
        x, y = 0.1, 0.1

        for i in range(num_points):
            xn = np.sin(a * y) + c * np.cos(a * x)
            yn = np.sin(b * x) + d * np.cos(b * y)
            x, y = xn, yn
            attractor_pts[i] = [x, y]

        # Scale attractor to screen center
        attractor_pts = attractor_pts * (self.width / 6.0) + [self.width / 2.0, self.height / 2.0]
        self.points_by_depth.append(attractor_pts)

    # 5. RANDOM / DLA FRACTALS (Diffusion-Limited Aggregation)
    def generate_random_dla(self, user_points, num_particles=1200):
        self.mode = "RANDOM_DLA"
        self.points_by_depth = []

        pts = np.array(user_points, dtype=int)
        if len(pts) < 2:
            return

        # Seed cluster with user drawing
        cluster = set((p[0], p[1]) for p in pts[::3])
        dla_pts = list(cluster)

        bbox_min = np.min(pts, axis=0) - 20
        bbox_max = np.max(pts, axis=0) + 20

        for _ in range(num_particles):
            px = random.randint(max(10, bbox_min[0]), min(self.width - 10, bbox_max[0]))
            py = random.randint(max(10, bbox_min[1]), min(self.height - 10, bbox_max[1]))

            for _ in range(150):  # Random walk steps
                dx, dy = random.choice([(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)])
                px += dx
                py += dy

                # Check neighbor collision with seed cluster
                if any((px + nx, py + ny) in cluster for nx in [-2, 0, 2] for ny in [-2, 0, 2]):
                    cluster.add((px, py))
                    dla_pts.append((px, py))
                    break

        self.points_by_depth.append(np.array(dla_pts, dtype=float))

    # 6. FINITE SUBDIVISION RULES (Barycentric Triangular Mesh)
    def generate_subdivision(self, user_points, max_depth=4):
        self.mode = "SUBDIVISION"
        self.line_segments_by_depth = []

        pts = np.array(user_points, dtype=float)
        if len(pts) < 3:
            return

        p1, p2, p3 = pts[0], pts[len(pts) // 2], pts[-1]
        triangles = [(p1, p2, p3)]

        for _ in range(max_depth):
            next_triangles = []
            for a, b, c in triangles:
                m_ab = (a + b) / 2.0
                m_bc = (b + c) / 2.0
                m_ca = (c + a) / 2.0
                next_triangles.extend([(a, m_ab, m_ca), (m_ab, b, m_bc), (m_ca, m_bc, c), (m_ab, m_bc, m_ca)])
            triangles = next_triangles

        segments = []
        for a, b, c in triangles:
            segments.extend([(a, b), (b, c), (c, a)])

        self.line_segments_by_depth.append(segments)

    # 7. SUBDIVISION LINKS (Alternating braid curve loops)
    def generate_subdivision_links(self, user_points, max_depth=3):
        self.mode = "SUBDIVISION_LINKS"
        self.line_segments_by_depth = []

        pts = np.array(user_points, dtype=float)
        if len(pts) < 4:
            return

        segments = []
        for i in range(len(pts) - 1):
            p_a, p_b = pts[i], pts[i + 1]
            vec = p_b - p_a
            perp = np.array([-vec[1], vec[0]]) * 0.35

            for d in range(1, max_depth + 1):
                scale = 1.0 / d
                segments.append((p_a + perp * scale, p_b + perp * scale))
                segments.append((p_a - perp * scale, p_b - perp * scale))

        self.line_segments_by_depth.append(segments)

    # UNIFIED RENDERER
    def render(self, surface):
        surface.fill((25, 26, 35))

        if self.mode == "ESCAPE_TIME" and self.fractal_surface is not None:
            surface.blit(self.fractal_surface, (0, 0))

        elif self.mode in ["IFS", "ATTRACTOR", "RANDOM_DLA"]:
            cx, cy = self.width / 2.0, self.height / 2.0
            for depth, pts in enumerate(self.points_by_depth):
                transformed = (pts - [cx, cy]) * self.zoom + [cx + self.offset_x, cy + self.offset_y]
                valid = (
                    (transformed[:, 0] >= 0)
                    & (transformed[:, 0] < self.width)
                    & (transformed[:, 1] >= 0)
                    & (transformed[:, 1] < self.height)
                )
                vis_pts = transformed[valid].astype(int)

                color = (255, 180, 50) if self.mode != "ATTRACTOR" else (100, 220, 255)
                for pt in vis_pts:
                    pygame.draw.circle(surface, color, (pt[0], pt[1]), 1)

        elif self.mode in ["LSYSTEM", "SUBDIVISION", "SUBDIVISION_LINKS"]:
            cx, cy = self.width / 2.0, self.height / 2.0
            for segments in self.line_segments_by_depth:
                for seg_a, seg_b in segments:
                    p_a = (seg_a - [cx, cy]) * self.zoom + [cx + self.offset_x, cy + self.offset_y]
                    p_b = (seg_b - [cx, cy]) * self.zoom + [cx + self.offset_x, cy + self.offset_y]
                    pygame.draw.aaline(surface, (120, 220, 180), p_a, p_b, 1)

    # NAVIGATION HANDLERS
    def handle_mouse_down(self, pos, button, user_points):
        if button == 1:
            self.is_panning = True
            self.pan_start = pos
        elif button in [4, 5]:
            factor = 0.8 if button == 4 else 1.25
            if self.mode == "ESCAPE_TIME":
                self.scale *= factor
                self.generate_escape_time(user_points)
            else:
                self.zoom /= factor

    def handle_mouse_up(self, button, user_points):
        if button == 1 and self.is_panning:
            self.is_panning = False
            if self.mode == "ESCAPE_TIME":
                self.generate_escape_time(user_points)

    def handle_mouse_motion(self, pos):
        if self.is_panning:
            dx, dy = pos[0] - self.pan_start[0], pos[1] - self.pan_start[1]
            if self.mode == "ESCAPE_TIME":
                self.center_x -= (dx / self.width) * self.scale
                self.center_y -= (dy / self.height) * (self.scale * self.height / self.width)
            else:
                self.offset_x += dx
                self.offset_y += dy
            self.pan_start = pos