import time

class SpellStateMachine:
    """Finite‑state machine controlling the four animation stages.

    States:
        IDLE        – no triangle detected.
        ENERGY      – first stage (particles & glow).
        OUTLINE     – drawing triangle edges.
        RUNES       – inner rune formation.
        ACTIVATED   – fully visible, emitting sparks.
        COOLDOWN    – fade‑out after release.
    """

    def __init__(self):
        self.state = "IDLE"
        self.state_start = time.time()
        # Duration of each stage in seconds
        self.durations = {
            "ENERGY": 0.6,
            "OUTLINE": 0.8,
            "RUNES": 1.0,
            "ACTIVATED": 0.0,  # stays until gesture ends
            "COOLDOWN": 0.5,
        }
        self.triangle_vertices = None
        self.gesture_active = False

    def reset(self):
        self.state = "IDLE"
        self.state_start = time.time()
        self.triangle_vertices = None
        self.gesture_active = False

    def update(self, gesture_active, vertices):
        """Update FSM.
        *gesture_active* – bool indicating stable triangle detection.
        *vertices* – list of three (x, y) pixel tuples when stable.
        Returns current state string.
        """
        now = time.time()
        if self.state == "IDLE":
            if gesture_active:
                self.state = "ENERGY"
                self.state_start = now
                self.triangle_vertices = vertices
        else:
            # If gesture lost, move to cooldown after current stage completes
            if not gesture_active and self.state not in ("COOLDOWN", "IDLE"):
                # Force transition to COOLDOWN after current stage duration elapses
                if self.state != "ACTIVATED":
                    # allow current stage to finish then cooldown
                    if now - self.state_start >= self.durations[self.state]:
                        self.state = "COOLDOWN"
                        self.state_start = now
                else:
                    # activated stage: go to cooldown immediately
                    self.state = "COOLDOWN"
                    self.state_start = now
            # Normal progression when gesture kept
            if gesture_active and self.state in ("ENERGY", "OUTLINE", "RUNES"):
                if now - self.state_start >= self.durations[self.state]:
                    # advance to next stage
                    next_state = {
                        "ENERGY": "OUTLINE",
                        "OUTLINE": "RUNES",
                        "RUNES": "ACTIVATED",
                    }[self.state]
                    self.state = next_state
                    self.state_start = now
            # Handle cooldown completion
            if self.state == "COOLDOWN" and now - self.state_start >= self.durations["COOLDOWN"]:
                self.reset()
        return self.state
