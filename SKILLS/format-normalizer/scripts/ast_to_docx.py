import json
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


class ASTToDocxConverter:
    def __init__(self, ast_path, template_config_path=None):
        self.ast_path = Path(ast_path)
        self.template_config_path = template_config_path
        self.ast = self.load_ast()
        self.template_config = self.load_template_config()
        self.doc = Document()

    def load_ast(self):
        with open(self.ast_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_template_config(self):
        if self.template_config_path and Path(self.template_config_path).exists():
            with open(self.template_config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def setup_document(self):
        section = self.doc.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.18)
        section.right_margin = Cm(3.18)

    def convert_paragraphs(self):
        for para_data in self.ast.get("paragraphs", []):
            text = para_data.get("text", "")
            if not text.strip():
                continue

            para = self.doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

            for run_data in para_data.get("runs", []):
                run = para.add_run(run_data.get("text", ""))
                if run_data.get("bold"):
                    run.bold = True
                if run_data.get("italic"):
                    run.italic = True
                if run_data.get("font_name"):
                    run.font.name = run_data["font_name"]
                if run_data.get("font_size"):
                    try:
                        size = int(run_data["font_size"].replace("pt", ""))
                        run.font.size = Pt(size)
                    except:
                        pass

    def convert_tables(self):
        for table_data in self.ast.get("tables", []):
            rows = table_data.get("rows", [])
            if not rows:
                continue

            table = self.doc.add_table(rows=len(rows), cols=len(rows[0]))
            for i, row_data in enumerate(rows):
                for j, cell_text in enumerate(row_data):
                    table.cell(i, j).text = cell_text

    def save(self, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(output_path))
        print(f"[INFO] DOCX saved to: {output_path}")

    def run(self, output_path):
        self.setup_document()
        self.convert_paragraphs()
        self.convert_tables()
        self.save(output_path)


if __name__ == "__main__":
    converter = ASTToDocxConverter(
        "workspace/normalized/normalized_ast.json",
        "workspace/validated/template_config.json"
    )
    converter.run("workspace/output/final.docx")