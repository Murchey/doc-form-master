import json
import base64
import tempfile
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


class ASTToDocxConverter:
    def __init__(self, ast_path, template_config_path=None):
        self.ast_path = Path(ast_path)
        self.template_config_path = template_config_path
        self.ast = self.load_ast()
        self.template_config = self.load_template_config()
        self.doc = Document()
        self._image_counter = 0

    def load_ast(self):
        with open(self.ast_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_template_config(self):
        if self.template_config_path and Path(self.template_config_path).exists():
            with open(self.template_config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def set_run_font(run, font_name, is_chinese=False):
        if not font_name:
            return
        run.font.name = font_name
        rpr = run._element.get_or_add_rPr()
        rFonts = rpr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rpr.insert(0, rFonts)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        if is_chinese:
            rFonts.set(qn('w:eastAsia'), font_name)

    @staticmethod
    def get_heading_level(style_name):
        if not style_name:
            return None
        style_lower = style_name.lower()
        if 'heading 1' in style_lower or 'heading1' in style_lower:
            return 1
        elif 'heading 2' in style_lower or 'heading2' in style_lower:
            return 2
        elif 'heading 3' in style_lower or 'heading3' in style_lower:
            return 3
        return None

    def setup_document(self):
        section = self.doc.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.18)
        section.right_margin = Cm(3.18)

    def _add_image_to_paragraph(self, para, run_data):
        img_data_b64 = run_data.get("image_data", "")
        img_format = run_data.get("image_format", "png")
        if not img_data_b64:
            return
        try:
            img_bytes = base64.b64decode(img_data_b64)
            suffix = '.png' if img_format == 'png' else '.jpg' if img_format in ('jpg', 'jpeg') else '.gif' if img_format == 'gif' else '.bmp' if img_format == 'bmp' else '.png'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            run = para.add_run()
            run.add_picture(tmp_path)
            Path(tmp_path).unlink(missing_ok=True)
            self._image_counter += 1
        except Exception:
            pass

    def convert_paragraphs(self):
        for para_data in self.ast.get("paragraphs", []):
            runs = para_data.get("runs", [])
            all_image_para = runs and all(r.get("type") == "image" for r in runs)

            if not all_image_para:
                text = para_data.get("text", "")
                if not text.strip() and not any(r.get("type") == "image" for r in runs):
                    continue

            style_name = para_data.get("style", "")
            heading_level = self.get_heading_level(style_name)

            if heading_level is not None:
                para = self.doc.add_heading(text, level=heading_level)
            else:
                para = self.doc.add_paragraph()

            alignment_str = para_data.get("alignment", "")
            if alignment_str == "CENTER":
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif alignment_str == "LEFT":
                para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif alignment_str == "RIGHT":
                para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            elif alignment_str == "JUSTIFY":
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

            if para_data.get("first_line_indent"):
                try:
                    indent_value = float(para_data["first_line_indent"])
                    from docx.shared import Cm as IndentCm
                    para.paragraph_format.first_line_indent = IndentCm(indent_value)
                except:
                    pass

            if heading_level is not None:
                continue

            for run_data in runs:
                if run_data.get("type") == "image":
                    self._add_image_to_paragraph(para, run_data)
                    continue

                run = para.add_run(run_data.get("text", ""))
                if run_data.get("bold"):
                    run.bold = True
                if run_data.get("italic"):
                    run.italic = True
                if run_data.get("font_name"):
                    font_name = run_data["font_name"]
                    text_content = run_data.get("text", "")
                    is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text_content)
                    self.set_run_font(run, font_name, is_chinese)
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