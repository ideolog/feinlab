import random
import time

class BelochUX:
    def __init__(self, total: int, writer):
        self.total = max(total, 1)
        self.writer = writer
        self.start_ts = None

        # counters
        self.processed = 0
        self.relevant = 0
        self.not_relevant = 0
        self.created = 0  # json files written

        # final quotes
        self.quotes = [
            "Another spike train archived.",
            "Dimensionality of understanding increased.",
            "Baseline drift corrected.",
            "Noise floor slightly lower than before.",
            "Oscillations continue with improved phase alignment.",
            "A new parameter space has been quietly entered.",
            "Tuning curves shift in meaningful directions.",
            "Decoding accuracy marginally but undeniably improved.",
            "Plasticity event recorded. Magnitude uncertain.",
            "The singularity is now one step closer.",
            "The system exhibits stable attractor behavior.",
            "Homeostasis temporarily achieved.",
        ]

    # ---------- helpers ----------
    @staticmethod
    def _fmt_eta(seconds: float) -> str:
        """Return ETA like '3m 20s' with rounding to 10s."""
        s = max(0, int(round(seconds / 10.0) * 10))
        m, s = divmod(s, 60)
        if m > 0:
            return f"{m}m {s:02d}s"
        return f"{s}s"

    # ---------- public ----------
    def start(self):
        self.start_ts = time.time()
        self.writer(f"\nBeloch 🐿️ starts processing... {self.total} documents to go!\n")

    def tick(self, is_relevant: bool, created_json: bool):
        self.processed += 1
        if is_relevant:
            self.relevant += 1
        else:
            self.not_relevant += 1
        if created_json:
            self.created += 1

        remaining = self.total - self.processed
        if remaining <= 0:
            return  # no progress bar at 100%

        pct = (self.processed / self.total) * 100.0
        elapsed = time.time() - (self.start_ts or time.time())
        eta_seconds = (elapsed / max(1, self.processed)) * remaining
        eta = self._fmt_eta(eta_seconds)

        bar = "🐿️" * int(pct / 10)
        self.writer(f"{bar} {int(pct)}% | {remaining} left ≈{eta}\n")

    def finish(self):
        end_ts = time.time()
        total_time = end_ts - (self.start_ts or end_ts)
        m, s = divmod(int(total_time), 60)
        total_str = f"{m}m {s:02d}s" if m > 0 else f"{s}s"

        quote = random.choice(self.quotes)

        # final flourish

        self.writer(f"\nฅ^•ﻌ•^ฅ\n 🔥 100% processed.\n{quote} 😈\n")

        self.writer(
            f"Total duration: {total_str}\n"
            f"Docs processed: {self.processed}/{self.total}\n"
            f"Relevant: {self.relevant}\n"
            f"Not relevant: {self.not_relevant}\n"
            f"JSON files created: {self.created}\n"
        )
