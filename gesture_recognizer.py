import collections
import math

class GestureRecognizer:
    """Detect a stable triangle formed by fingertips of both hands.

    The triangle is defined by the index fingertips of the left and right hands
    plus the thumb tip of the hand whose thumb is farthest from the line joining
    the two index fingertips. This heuristic works well for the typical "triangle"
    pose used in many magic‑hand tricks.
    """

    def __init__(self, stable_frames: int = 12, max_angle_deviation: float = 30.0):
        self.stable_frames = stable_frames
        self.buffer = collections.deque(maxlen=stable_frames)
        self.max_angle_deviation = max_angle_deviation  # degrees tolerance for each angle

    @staticmethod
    def _distance(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    @staticmethod
    def _angle(a, b, c):
        """Return angle at point b (in degrees) for triangle a‑b‑c."""
        ab = (a[0] - b[0], a[1] - b[1])
        cb = (c[0] - b[0], c[1] - b[1])
        dot = ab[0] * cb[0] + ab[1] * cb[1]
        mag_ab = math.hypot(*ab)
        mag_cb = math.hypot(*cb)
        if mag_ab * mag_cb == 0:
            return 0.0
        cos_angle = max(-1.0, min(1.0, dot / (mag_ab * mag_cb)))
        return math.degrees(math.acos(cos_angle))

    def _extract_vertices(self, hand_results):
        """Return three vertices (x, y) if possible, otherwise None.

        hand_results must contain two hands (order not guaranteed). For each hand we
        extract the index tip (landmark 8) and thumb tip (landmark 4). The triangle
        vertices are:
            - right hand index tip
            - left hand index tip
            - selected thumb tip (the thumb farthest from the line joining the two
              index tips).
        """
        if not hasattr(hand_results, "hand_landmarks"):
            return None
        if len(hand_results.hand_landmarks) < 2:
            return None
        # Collect fingertips for each detected hand
        fingertips = []  # list of (hand_label, index_pt, thumb_pt)
        for hand_landmarks, handedness in zip(hand_results.hand_landmarks, hand_results.handedness):
            label = handedness[0].category_name  # "Left" or "Right"
            idx = hand_landmarks[8]
            thumb = hand_landmarks[4]
            # MediaPipe provides normalized coordinates (0‑1). The caller will scale to pixel space.
            fingertips.append((label, (idx.x, idx.y), (thumb.x, thumb.y)))
        if len(fingertips) != 2:
            return None
        # Determine right and left hands; if a label is missing, fall back to using the first two detected hands.
        try:
            right = next(p for p in fingertips if p[0] == "Right")
            left = next(p for p in fingertips if p[0] == "Left")
        except StopIteration:
            # Fallback: assign first entry as right and second as left
            right, left = fingertips[0], fingertips[1]
        right_idx = right[1]
        left_idx = left[1]
        # Compute distance of each thumb to the line joining the two index tips
        def point_line_distance(pt, a, b):
            # pt, a, b are (x, y) tuples
            # line AB expressed as vector
            ax, ay = a
            bx, by = b
            px, py = pt
            # |(b-a) x (a-pt)| / |b-a|
            num = abs((bx - ax) * (ay - py) - (ax - px) * (by - ay))
            den = math.hypot(bx - ax, by - ay)
            return num / den if den != 0 else float('inf')
        right_thumb_dist = point_line_distance(right[2], left_idx, right_idx)
        left_thumb_dist = point_line_distance(left[2], left_idx, right_idx)
        thumb_pt = right[2] if right_thumb_dist > left_thumb_dist else left[2]
        # Return vertices in pixel coordinates (the caller will scale later)
        return (right_idx, left_idx, thumb_pt)

    def _validate_triangle(self, verts):
        a, b, c = verts
        # Side lengths
        d_ab = self._distance(a, b)
        d_bc = self._distance(b, c)
        d_ca = self._distance(c, a)
        # Ratio check – avoid extremely skinny triangles
        max_len = max(d_ab, d_bc, d_ca)
        min_len = min(d_ab, d_bc, d_ca)
        if min_len == 0 or max_len / min_len > 1.5:
            return False
        # Angle checks – each angle should be roughly between 30° and 130°
        angles = [self._angle(a, b, c), self._angle(b, c, a), self._angle(c, a, b)]
        for ang in angles:
            if not (30.0 <= ang <= 130.0):
                return False
        return True

    def is_triangle(self, hand_results, frame_width: int, frame_height: int):
        """Return (bool, vertices_px) where *vertices_px* is a list of three (x, y) in pixel space.
        The method also updates the internal stability buffer.
        """
        verts_norm = self._extract_vertices(hand_results)
        if verts_norm is None:
            self.buffer.append(False)
            return False, None
        # Scale normalized coordinates to pixel space
        verts_px = [(int(x * frame_width), int(y * frame_height)) for (x, y) in verts_norm]
        # Validate geometric shape
        ok = self._validate_triangle(verts_norm)
        self.buffer.append(ok)
        stable = len(self.buffer) == self.stable_frames and all(self.buffer)
        return stable, (verts_px if stable else None)
