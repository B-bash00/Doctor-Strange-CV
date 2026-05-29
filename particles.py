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
        self.decay = random.uniform(0.02, 0.05)
        self.color = color
        self.size = random.uniform(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color=(0, 165, 255), count=2):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, frame):
        # We will draw particles directly on the frame using additive blending approach
        overlay = np.zeros_like(frame)
        for p in self.particles:
            if p.life > 0:
                color = (int(p.color[0] * p.life), int(p.color[1] * p.life), int(p.color[2] * p.life))
                cv2.circle(overlay, (int(p.x), int(p.y)), int(p.size), color, -1)
        
        # Additive blending
        cv2.addWeighted(overlay, 1.0, frame, 1.0, 0, frame)
