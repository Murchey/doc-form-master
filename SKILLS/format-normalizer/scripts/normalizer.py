import json
from pathlib import Path


class FormatNormalizer:
    def __init__(self, ast_path, config_path=None):

        self.ast_path = Path(ast_path)
        self.config_path = config_path

        self.ast = self.load_ast()

        self.fix_report = {
            "paragraph_fixes": 0,
            "font_fixes": 0,
            "heading_fixes": 0,
            "table_fixes": 0
        }

    def load_ast(self):

        with open(
            self.ast_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    def normalize_paragraphs(self):

        for paragraph in self.ast.get("paragraphs", []):

            paragraph["alignment"] = "JUSTIFY"

            paragraph["line_spacing"] = 1.5

            paragraph["first_line_indent"] = 2

            self.fix_report["paragraph_fixes"] += 1

    def normalize_fonts(self):

        for paragraph in self.ast.get("paragraphs", []):

            for run in paragraph.get("runs", []):

                text = run.get("text", "")

                if self.contains_chinese(text):
                    run["font_name"] = "宋体"
                else:
                    run["font_name"] = "Times New Roman"

                run["font_size"] = "12pt"

                self.fix_report["font_fixes"] += 1

    def normalize_headings(self):

        for paragraph in self.ast.get("paragraphs", []):

            style = paragraph.get("style", "")

            if "Heading" in style:

                paragraph["bold"] = True

                paragraph["alignment"] = "CENTER"

                self.fix_report["heading_fixes"] += 1

    def normalize_tables(self):

        for table in self.ast.get("tables", []):

            table["alignment"] = "CENTER"

            table["auto_fit"] = True

            self.fix_report["table_fixes"] += 1

    @staticmethod
    def contains_chinese(text):

        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True

        return False

    def export_normalized_ast(self):

        output_dir = Path(
            "workspace/normalized"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_dir / "normalized_ast.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.ast,
                f,
                ensure_ascii=False,
                indent=2
            )

    def export_fix_report(self):

        report_dir = Path("workspace/reports")

        report_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            report_dir / "fix_report.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.fix_report,
                f,
                ensure_ascii=False,
                indent=2
            )

    def run(self):

        self.normalize_paragraphs()

        self.normalize_fonts()

        self.normalize_headings()

        self.normalize_tables()

        self.export_normalized_ast()

        self.export_fix_report()

        print(
            "[INFO] Format normalization completed"
        )


if __name__ == "__main__":

    normalizer = FormatNormalizer(
        "workspace/parsed/document_ast.json"
    )

    normalizer.run()