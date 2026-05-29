import cv2
import numpy as np
import random
import math

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 5.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        # slower decay for longer visible glow
        self.decay = random.uniform(0.01, 0.03)
        self.color = color
        # smaller particles for a finer sparkle
        self.size = random.uniform(1, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

class ParticleSystem:
    def __init__(self):
        self.particles = []
    def emit(self, x, y, color=(0, 165, 255), count=1):
        """Emit count particles at (x, y)."""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))


    def emit_between(self, p1, p2, count=2, color=(0, 165, 255)):
        """Emit particles along the line between p1 and p2.
        p1, p2 are (x, y) tuples.
        """
        for _ in range(count):
            t = random.random()
            x = int(p1[0] + t * (p2[0] - p1[0]))
            y = int(p1[1] + t * (p2[1] - p1[1]))
            self.particles.append(Particle(x, y, color))
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def emit_between(self, p1, p2, count=2, color=(0, 165, 255)):
        """Emit *count* particles evenly spaced along the line segment p1→p2.
        p1 and p2 are (x, y) pixel tuples.
        """
        x1, y1 = p1
        x2, y2 = p2
        for i in range(count):
            t = (i + 1) / (count + 1)
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            self.particles.append(Particle(x, y, color))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, frame):
        overlay = np.zeros_like(frame)
        for p in self.particles:
            if p.life > 0:
                # amplify brightness for a vivid glow (capped at 255)
                r = min(255, int(p.color[0] * (1 + p.life)))
                g = min(255, int(p.color[1] * (1 + p.life)))
                b = min(255, int(p.color[2] * (1 + p.life)))
                color = (r, g, b)
                cv2.circle(overlay, (int(p.x), int(p.y)), int(p.size), color, -1)
        cv2.addWeighted(overlay, 1.0, frame, 1.0, 0, frame)
