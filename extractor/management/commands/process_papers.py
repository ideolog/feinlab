from django.core.management.base import BaseCommand
from pathlib import Path
import json
from extractor.ai import analyze_pdf_with_file_search
from extractor.fun import BelochUX

class Command(BaseCommand):
    help = "Process all PDFs in the default ./PDF folder."

    def add_arguments(self, parser):
        parser.add_argument("--folder", type=str, default=None)
        parser.add_argument("--out", type=str, default="./OUT")
        parser.add_argument("--prompt", type=str, default="./PROMPT.txt")
        parser.add_argument("--gate", choices=["rat", "rodent", "any"], default="rat")

    def handle(self, *args, **options):
        folder = Path(options["folder"] or "./PDF").resolve()
        outdir = Path(options["out"]).resolve()
        prompt_path = Path(options["prompt"]).resolve()
        gate = options["gate"]

        folder.mkdir(parents=True, exist_ok=True)
        outdir.mkdir(parents=True, exist_ok=True)

        if not prompt_path.exists():
            self.stderr.write(f"Missing prompt file: {prompt_path}")
            return

        base_prompt = prompt_path.read_text(encoding="utf-8")

        gate_patch = {
            "rat": (
                "STRICT RAT MODE (OVERRIDES):\n"
                "SPECIES SELECTION:\n"
                "- If Title contains 'rat' or 'rats' (case-insensitive), set species='rat'.\n"
                "- Otherwise determine species in order: Title → Abstract → Animals/Subjects/Methods.\n"
                "- If both 'rat' and 'mouse' appear, pick the species actually used for in vivo single-unit/LFP recordings.\n\n"

                "REJECTION EVIDENCE REQUIRED:\n"
                "If relevance = 'no', include a one-line evidence quote (<200 chars) in 'reason'.\n\n"

                "(These species rejection rules apply ONLY IN RAT MODE.)\n"
                "If species is mouse or any non-rat, output exactly:\n"
                "{\"relevance\":\"no\",\"reason\":\"Species is [detected species], not rat.\"}\n\n"

                "If species = rat but NO in vivo single-unit or LFP electrophysiology, output exactly:\n"
                "{\"relevance\":\"no\",\"reason\":\"Not relevant: no in vivo single-unit or LFP electrophysiology in rats.\"}\n\n"

                "Otherwise (species=rat AND electrophysiology present):\n"
                "Set \"relevance\":\"yes\" and fill the full schema.\n"
            ),

            "rodent": (
                "RODENT MODE (OVERRIDES EVERYTHING ABOVE):\n"
                "Species rule:\n"
                "- If species = rat or mouse → allowed.\n"
                "- If any other species → output exactly:\n"
                "{\"relevance\":\"no\",\"reason\":\"Not relevant: species not rat/mouse.\"}\n\n"

                "Electrophysiology rule:\n"
                "- If the paper includes *in vivo* single-unit and/or LFP electrophysiology (in either rat or mouse):\n"
                "  set \"relevance\":\"yes\" and fill the schema.\n"
                "- Otherwise output exactly:\n"
                "{\"relevance\":\"no\",\"reason\":\"Not relevant: no in vivo single-unit or LFP electrophysiology.\"}\n\n"

                "IMPORTANT: Ignore ALL rat-only rejection rules above. "
                "This block fully overrides conflicting instructions.\n"
            ),

            "any": (
                "ANY MODE (OVERRIDES EVERYTHING ABOVE):\n"
                "Species rule:\n"
                "- Ignore species entirely. Still extract species into the JSON, but species MUST NOT affect relevance.\n\n"
                "Electrophysiology rule:\n"
                "- If *in vivo* single-unit or LFP electrophysiology exists (in ANY species), set \"relevance\":\"yes\".\n"
                "- If NOT present → output exactly:\n"
                "{\"relevance\":\"no\",\"reason\":\"Not relevant: no in vivo single-unit or LFP electrophysiology.\"}\n\n"

                "Ignore ALL species-based rejection conditions from earlier text. "
                "This block overrides everything above.\n"
            )
        }[gate]

        combined_prompt = (
            base_prompt
            + "\n\nOVERRIDE RULES — APPLY THESE LAST (MODE: " + gate.upper() + "):\n"
            + gate_patch
            + "\n(If any rule in this section conflicts with earlier text, THIS SECTION WINS.)\n"
            + "\nReturn ONLY valid JSON. No explanations, no markdown, no code fences.\n"
        )

        pdfs = sorted(folder.glob("*.pdf"))
        if not pdfs:
            self.stdout.write("No PDFs found. Put files into ./PDF/")
            return

        ux = BelochUX(len(pdfs), self.stdout.write)
        ux.start()

        for pdf in pdfs:
            self.stdout.write(f"Processing: {pdf.name}")
            result = analyze_pdf_with_file_search(str(pdf), combined_prompt)

            out_file = outdir / f"{pdf.stem}.{gate}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            self.stdout.write(f"→ {out_file}")

            rel = result.get("relevance", None)
            if isinstance(rel, bool):
                is_rel = rel
            elif isinstance(rel, str):
                is_rel = rel.strip().lower() == "yes"
            else:
                is_rel = False

            ux.tick(is_relevant=is_rel, created_json=True)

        ux.finish()
