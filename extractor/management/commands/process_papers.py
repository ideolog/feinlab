from django.core.management.base import BaseCommand
from pathlib import Path
import json
from extractor.ai import analyze_pdf_with_file_search
from extractor.fun import BelochUX

class Command(BaseCommand):
    help = "Process all PDFs in the default ./PDF folder (no animal logic, only electrophysiology check)."

    def add_arguments(self, parser):
        parser.add_argument("--folder", type=str, default=None)
        parser.add_argument("--out", type=str, default="./OUT")
        parser.add_argument("--prompt", type=str, default="./PROMPT.txt")

    def handle(self, *args, **options):
        folder = Path(options["folder"] or "./PDF").resolve()
        outdir = Path(options["out"]).resolve()
        prompt_path = Path(options["prompt"]).resolve()

        folder.mkdir(parents=True, exist_ok=True)
        outdir.mkdir(parents=True, exist_ok=True)

        if not prompt_path.exists():
            self.stderr.write(f"Missing prompt file: {prompt_path}")
            return

        base_prompt = prompt_path.read_text(encoding="utf-8")

        # no gates, one consistent instruction override
        combined_prompt = (
            base_prompt
            + "\n\nOVERRIDE RULES — APPLY THESE LAST:\n"
            + "If the paper does not contain in vivo electrophysiology with single-unit or LFP recordings, "
              "reply only: \"Not relevant: no electrophysiology or neural recordings.\"\n"
              "Otherwise, set relevance='yes' and fill the schema.\n"
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

            out_file = outdir / f"{pdf.stem}.json"
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