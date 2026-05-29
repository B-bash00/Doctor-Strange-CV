import cv2
import numpy as np
import time
from hand_tracker import HandTracker
from particles import ParticleSystem
from portal_effect import MagicCircle, Portal
from gesture_recognizer import GestureRecognizer
from spell_state_machine import SpellStateMachine
from effects import TriangleSpellEffects

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    particles = ParticleSystem()
    magic_circle_left = MagicCircle()
    magic_circle_right = MagicCircle()
    portal = Portal()
    gesture_recognizer = GestureRecognizer()
    spell_fsm = SpellStateMachine()
    triangle_effects = TriangleSpellEffects(particles)

    last_portal_center = (320, 240)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)  # Mirror image for webcam interaction
        h, w, _ = frame.shape

        timestamp_ms = int(time.time() * 1000)
        results = tracker.process_frame(frame, timestamp_ms)
        centers = []

        if results.hand_landmarks:
            for hand_landmarks, handedness_list in zip(results.hand_landmarks, results.handedness):
                handedness = handedness_list[0]
                is_open = tracker.is_palm_open(hand_landmarks)
                center = tracker.get_palm_center(hand_landmarks, w, h)
                scale = tracker.get_hand_scale(hand_landmarks)
                centers.append(center)

                # Emit spark trails from fingertips
                fingertips = tracker.get_fingertips(hand_landmarks, w, h)
                for tip in fingertips:
                    particles.emit(tip[0], tip[1], color=(0, 165, 255), count=1)

                # Draw magic circles when palm is open
                if is_open:
                    label = handedness.category_name
                    if label == "Right":
                        magic_circle_right.update()
                        magic_circle_right.draw(frame, center, scale)
                    else:
                        magic_circle_left.update()
                        magic_circle_left.draw(frame, center, scale, color=(0, 200, 100))

        # Portal logic (two hands)
        if len(centers) == 2:
            dist = np.linalg.norm(np.array(centers[0]) - np.array(centers[1]))
            last_portal_center = (
                int((centers[0][0] + centers[1][0]) / 2),
                int((centers[0][1] + centers[1][1]) / 2),
            )
            portal.update(dist)
        else:
            portal.update(0)

        if portal.current_scale > 0.01:
            portal.draw(frame, last_portal_center)

        # Triangle gesture handling and spell effects
        gesture_active, verts = gesture_recognizer.is_triangle(results, w, h)
        state = spell_fsm.update(gesture_active, verts)
        if state != "IDLE" and verts:
            if state == "ENERGY":
                triangle_effects.draw_energy(frame, verts)
            elif state == "OUTLINE":
                triangle_effects.draw_outline(frame, verts)
            elif state == "RUNES":
                triangle_effects.draw_runes(frame, verts)
            elif state == "ACTIVATED":
                triangle_effects.draw_activation(frame, verts)

        # Update and draw particles
        particles.update()
        particles.draw(frame)

        cv2.imshow("Doctor Strange Magic", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
