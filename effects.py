import cv2
import numpy as np
import math
import time
import random
import numpy as np
import math
import time

# Helper to draw glowing lines (additive blend)
def draw_glowing_line(frame, pt1, pt2, color, thickness=2, glow_radius=6):
    overlay = np.zeros_like(frame)
    cv2.line(overlay, pt1, pt2, color, thickness + glow_radius)
    overlay = cv2.GaussianBlur(overlay, (0, 0), glow_radius)
    cv2.line(overlay, pt1, pt2, color, thickness)
    cv2.addWeighted(overlay, 1.0, frame, 1.0, 0, frame)

class TriangleSpellEffects:
    """Procedural VFX for the triangle‑hand spell.
    The class does not own any state; it receives the current vertices and a
    ParticleSystem instance to emit particles.
    """

    def __init__(self, particles):
        self.particles = particles
        self.start_time = time.time()
        self.rune_angle = 0.0

    def _centroid(self, verts):
        xs, ys = zip(*verts)
        return (int(sum(xs) / 3), int(sum(ys) / 3))

    def draw_energy(self, verts):
        # Small sparks at each vertex and particles along edges
        for v in verts:
            self.particles.emit(v[0], v[1], color=(0, 200, 255), count=1)
        # Emit between each pair of vertices
        pairs = [(verts[0], verts[1]), (verts[1], verts[2]), (verts[2], verts[0])]
        for a, b in pairs:
            self.particles.emit_between(a, b, count=2, color=(0, 180, 255))
        # Subtle pulsing glow at centroid
        cx, cy = self._centroid(verts)
        radius = 10 + int(5 * math.sin(2 * math.pi * (time.time() - self.start_time)))
        draw_glowing_line(frame, (cx - radius, cy), (cx + radius, cy), (255, 220, 120), thickness=1, glow_radius=8)

    def draw_outline(self, verts):
        # Animate line drawing from vertex to vertex based on elapsed time
        elapsed = time.time() - self.start_time
        total_len = sum([self._distance(verts[i], verts[(i + 1) % 3]) for i in range(3)])
        progress = min(1.0, elapsed / 0.8)  # outline stage duration
        # Determine how much of the perimeter to draw
        length_to_draw = total_len * progress
        drawn = 0.0
        for i in range(3):
            a = verts[i]
            b = verts[(i + 1) % 3]
            seg_len = self._distance(a, b)
            if drawn + seg_len < length_to_draw:
                # draw full segment
                draw_glowing_line(frame, a, b, (255, 180, 80), thickness=2, glow_radius=10)
                drawn += seg_len
            else:
                # draw partial segment
                remain = length_to_draw - drawn
                if remain > 0:
                    t = remain / seg_len
                    interim = (int(a[0] + t * (b[0] - a[0])), int(a[1] + t * (b[1] - a[1])))
                    draw_glowing_line(frame, a, interim, (255, 180, 80), thickness=2, glow_radius=10)
                break

    def draw_runes(self, verts):
        # Rotating inner circles that act as runes
        cx, cy = self._centroid(verts)
        radius = 30
        self.rune_angle += 2  # degrees per frame
        for i in range(3):
            angle = math.radians(self.rune_angle + i * 120)
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            cv2.circle(frame, (x, y), 8, (200, 255, 150), -1)
            # fade in with additive blend (simple bright circle)
            overlay = np.zeros_like(frame)
            cv2.circle(overlay, (x, y), 12, (200, 255, 150), -1)
            overlay = cv2.GaussianBlur(overlay, (0, 0), 6)
            cv2.addWeighted(overlay, 0.4, frame, 1.0, 0, frame)

    def draw_activation(self, verts):
        # Full glowing triangle with outward spark burst and screen‑space shimmer
        cx, cy = self._centroid(verts)
        # Glow pulse
        pulse = 5 * math.sin(2 * math.pi * (time.time() - self.start_time))
        radius = 30 + int(pulse)
        draw_glowing_line(frame, (cx - radius, cy), (cx + radius, cy), (255, 220, 80), thickness=3, glow_radius=12)
        # Emit outward particles from centroid
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(20, 40)
            x = int(cx + dist * math.cos(angle))
            y = int(cy + dist * math.sin(angle))
            self.particles.emit(x, y, color=(255, 240, 120), count=1)
        # Simple screen‑space distortion (wave ripple) via per‑pixel offset is heavy;
        # we approximate with a semi‑transparent moving sinusoidal overlay.
        overlay = np.full_like(frame, (30, 30, 80), dtype=np.uint8)
        alpha = 0.08 * (0.5 + 0.5 * math.sin(time.time()))
        cv2.addWeighted(overlay, alpha, frame, 1.0, 0, frame)

    @staticmethod
    def _distance(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])
