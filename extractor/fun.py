import random
import time

class BelochUX:
    def __init__(self, total: int, writer):
        self.total = max(total, 1)
        self.writer = writer
        self.start_ts = None
        self.last_flags = -1  # track % to avoid duplicate prints

        # counters
        self.processed = 0
        self.relevant = 0
        self.not_relevant = 0
        self.created = 0  # json files written

        # short autistic scientific prophecies
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

        # tiny haiku-moments at very specific progress points
        self.poems = {
            13:  "Micro-pattern recognized.",
            27:  "Cortical resonance aligns briefly.",
            44:  "Signal-to-noise ratio shifts.",
            58:  "A latent dimension clarifies.",
            73:  "Stability plateau detected.",
            88:  "Memory trace consolidation underway.",
        }

    # ---------- helpers ----------
    @staticmethod
    def _fmt_eta(seconds: float) -> str:
        """Return ETA like '3m 20s left' with rounding to 10s."""
        s = max(0, int(round(seconds / 10.0) * 10))
        m, s = divmod(s, 60)
        if m > 0:
            return f"{m}m {s:02d}s left"
        return f"{s}s left"

    def _bar_animals(self, pct: float) -> tuple[str, int]:
        """
        Animal progression scale:

        0–20%   -> 🐿️  (20)
        20–40%  -> 🐀  (20)
        40–60%  -> 🐁  (20)
        60–70%  -> 🐈  (10)
        70–80%  -> 🐼  (10)
        80–90%  -> 🐒  (10)
        90–100% -> 🦄  (10)
        """
        flags = int(pct)

        s = []
        s.append("🐿️" * min(flags, 20))
        s.append("🐀"  * min(max(flags - 20, 0), 20))
        s.append("🐁"  * min(max(flags - 40, 0), 10))
        s.append("🐈"  * min(max(flags - 50, 0), 10))
        s.append("🦎" * min(max(flags - 60, 0), 10))
        s.append("🐼"  * min(max(flags - 70, 0), 10))
        s.append("🐒"  * min(max(flags - 80, 0), 10))
        s.append("🦄"  * min(max(flags - 90, 0), 10))

        bar = "".join(s)
        return bar, flags

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
        pct = (self.processed / self.total) * 100.0

        elapsed = time.time() - (self.start_ts or time.time())
        eta_seconds = (elapsed / max(1, self.processed)) * remaining
        eta = self._fmt_eta(eta_seconds)

        # always show progress line
        self.writer(f"🐿️ processed {int(pct)}%. Left: {remaining} document{'s' if remaining != 1 else ''} ≈{eta}\n")

        # animal bar
        bar, flags = self._bar_animals(pct)
        if flags > self.last_flags:
            self.last_flags = flags
            self.writer(bar + "\n")

        # neuro-haiku easter eggs
        if int(pct) in self.poems:
            self.writer(f"🧬 {self.poems[int(pct)]}\n")

        # milestone at 90%
        if flags == 90:
            self.writer("Beloch observes. Beloch understands.\n")

    def finish(self):
        end_ts = time.time()
        total_time = end_ts - (self.start_ts or end_ts)

        t = int(total_time)
        m, s = divmod(t, 60)
        total_str = f"{m}m {s:02d}s" if m > 0 else f"{s}s"

        quote = random.choice(self.quotes)

        # final demonic flourish
        self.writer("ฅ^•ﻌ•^ฅ  < job done\n")

        self.writer(f"🔥 100% processed. The purple satan nods.\n{quote} 😈\n")
        self.writer(
            f"Total duration: {total_str}\n"
            f"Docs processed: {self.processed}/{self.total}\n"
            f"Relevant: {self.relevant}\n"
            f"Not relevant: {self.not_relevant}\n"
            f"JSON files created: {self.created}\n"
        )
