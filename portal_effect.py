import math
import numpy as np
from renderer import draw_glowing_circle

class MagicCircle:
    def __init__(self):
        self.angle = 0
        
    def update(self):
        self.angle += 5 # rotation speed
        
    def draw(self, frame, center, scale, color=(0, 165, 255)):
        radius = int(50 * scale)
        draw_glowing_circle(frame, center, radius, color, thickness=2, glow_radius=15)
        # Add dynamic inner parts based on angle
        inner_r = int(radius * 0.7)
        x = int(center[0] + inner_r * math.cos(math.radians(self.angle)))
        y = int(center[1] + inner_r * math.sin(math.radians(self.angle)))
        draw_glowing_circle(frame, (x, y), int(10*scale), (255, 255, 255), thickness=-1, glow_radius=5)

class Portal:
    def __init__(self):
        self.current_scale = 0.0
        self.target_scale = 0.0
        self.angle = 0
        
    def update(self, distance):
        # Easing function for smooth scaling
        # Portal opens when hands are further than 150px apart
        self.target_scale = max(0, (distance - 150) / 200.0) 
        self.current_scale += (self.target_scale - self.current_scale) * 0.1
        self.angle -= 3
        
    def draw(self, frame, center, color=(0, 140, 255)):
        if self.current_scale > 0.01:
            radius = int(150 * self.current_scale)
            draw_glowing_circle(frame, center, radius, color, thickness=4, glow_radius=30)
            draw_glowing_circle(frame, center, int(radius * 0.9), (200, 200, 255), thickness=1, glow_radius=10)
