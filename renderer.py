import cv2
import numpy as np

def draw_glowing_circle(frame, center, radius, color, thickness=2, glow_radius=10):
    """Draws a circle with a blur glow effect using additive blending."""
    overlay = np.zeros_like(frame)
    
    # Draw thick blurred circle for glow
    cv2.circle(overlay, center, radius, color, thickness + glow_radius)
    overlay = cv2.GaussianBlur(overlay, (0, 0), glow_radius)
    
    # Draw inner solid circle
    cv2.circle(overlay, center, radius, (255, 255, 255), thickness)
    
    # Additive blend
    cv2.addWeighted(overlay, 1.0, frame, 1.0, 0, frame)

def overlay_transparent_image(bg, img, x, y, scale=1.0, angle=0.0):
    """Overlays a BGRA image onto a BGR background with additive blending and transformation."""
    if img is None:
        return bg

    h, w = img.shape[:2]
    
    # Resize
    new_w, new_h = int(w * scale), int(h * scale)
    if new_w <= 0 or new_h <= 0:
        return bg
    resized = cv2.resize(img, (new_w, new_h))
    
    # Rotate
    center = (new_w // 2, new_h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(resized, M, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    
    # Calculate bounds
    y1, y2 = max(0, y - new_h // 2), min(bg.shape[0], y + new_h // 2)
    x1, x2 = max(0, x - new_w // 2), min(bg.shape[1], x + new_w // 2)
    
    # Coordinates in the overlay image
    img_y1 = max(0, -(y - new_h // 2))
    img_y2 = img_y1 + (y2 - y1)
    img_x1 = max(0, -(x - new_w // 2))
    img_x2 = img_x1 + (x2 - x1)
    
    if y1 >= y2 or x1 >= x2:
        return bg
        
    overlay_crop = rotated[img_y1:img_y2, img_x1:img_x2]
    bg_crop = bg[y1:y2, x1:x2]
    
    # Additive blending using the RGB channels directly
    # Assumes the transparent PNG has a black background where it is transparent, or we use alpha as a mask
    if overlay_crop.shape[2] == 4:
        alpha = overlay_crop[:, :, 3] / 255.0
        for c in range(3):
            bg_crop[:, :, c] = np.clip(bg_crop[:, :, c] + overlay_crop[:, :, c] * alpha, 0, 255)
    else:
        # Simple additive
        bg_crop = cv2.add(bg_crop, overlay_crop)
        bg[y1:y2, x1:x2] = bg_crop
        
    return bg
