import json
import base64
import shutil
import tempfile
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


class ASTToDocxConverter:
    def __init__(self, ast_path, template_config_path=None, source_docx_path=None):
        self.ast_path = Path(ast_path)
        self.template_config_path = template_config_path
        self.source_docx_path = Path(source_docx_path) if source_docx_path else None
        self.ast = self.load_ast()
        self.template_config = self.load_template_config()
        self.doc = None
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

    @staticmethod
    def _clear_paragraph(para):
        p_elem = para._element
        for child in list(p_elem):
            tag_local = child.tag.split('}')[1] if '}' in child.tag else child.tag
            if tag_local == 'r':
                p_elem.remove(child)

    def _is_protected(self, para_data):
        return para_data.get("section", "") in ("cover", "toc")

    def convert_paragraphs_in_place(self):
        doc_paras = self.doc.paragraphs
        ast_paras = self.ast.get("paragraphs", [])
        count = min(len(doc_paras), len(ast_paras))

        for i in range(count):
            para_data = ast_paras[i]

            if self._is_protected(para_data):
                continue

            runs = para_data.get("runs", [])
            all_image = runs and all(r.get("type") == "image" for r in runs)
            if not all_image:
                text = para_data.get("text", "")
                if not text.strip() and not any(r.get("type") == "image" for r in runs):
                    continue

            style_name = para_data.get("style", "")
            heading_level = self.get_heading_level(style_name)

            para = doc_paras[i]

            if heading_level is not None:
                self._apply_heading(para_data, heading_level, para)
            else:
                self._apply_normal_paragraph(para_data, para)

    def _apply_heading(self, para_data, heading_level, para):
        heading_config = self.template_config.get("heading", {})
        level_key = f"level{heading_level}"
        lvl_cfg = heading_config.get(level_key, {})

        font_name = lvl_cfg.get("font", "黑体")
        font_size = lvl_cfg.get("size", 16 if heading_level == 1 else 14 if heading_level == 2 else 13)
        bold = lvl_cfg.get("bold", True)
        spacing_before = lvl_cfg.get("spacing_before", 24 if heading_level == 1 else 18 if heading_level == 2 else 12)
        spacing_after = lvl_cfg.get("spacing_after", 18 if heading_level == 1 else 12 if heading_level == 2 else 6)
        alignment_str = lvl_cfg.get("alignment", "center" if heading_level == 1 else "left")

        self._clear_paragraph(para)

        runs = para_data.get("runs", [])
        if runs:
            for run_data in runs:
                run = para.add_run(run_data.get("text", ""))
                run.bold = bold
                run.font.size = Pt(font_size)
                run.font.color.rgb = RGBColor(0, 0, 0)
                self.set_run_font(run, font_name, is_chinese=True)
        elif para_data.get("text"):
            run = para.add_run(para_data["text"])
            run.bold = bold
            run.font.size = Pt(font_size)
            run.font.color.rgb = RGBColor(0, 0, 0)
            self.set_run_font(run, font_name, is_chinese=True)

        if alignment_str.upper() == "CENTER":
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif alignment_str.upper() == "LEFT":
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif alignment_str.upper() == "RIGHT":
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        if spacing_before:
            para.paragraph_format.space_before = Pt(spacing_before)
        if spacing_after:
            para.paragraph_format.space_after = Pt(spacing_after)

    def _get_body_font_size(self):
        fonts_cfg = self.template_config.get("fonts", {})
        return fonts_cfg.get("chinese", {}).get("size", 12)

    def _char_indent(self, char_count):
        body_size = self._get_body_font_size()
        return Pt(int(char_count * body_size))

    def _apply_normal_paragraph(self, para_data, para):
        runs = para_data.get("runs", [])
        has_image = any(r.get("type") == "image" for r in runs)

        self._clear_paragraph(para)

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
                para.paragraph_format.first_line_indent = self._char_indent(indent_value)
            except Exception:
                pass

        para_cfg = self.template_config.get("paragraph", {})
        if para_cfg.get("paragraph_spacing", False):
            body_size = self._get_body_font_size()
            para.paragraph_format.space_after = Pt(body_size)

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
                except Exception:
                    pass

    def convert_paragraphs(self):
        for para_data in self.ast.get("paragraphs", []):
            if self._is_protected(para_data):
                continue

            runs = para_data.get("runs", [])
            all_image_para = runs and all(r.get("type") == "image" for r in runs)

            if not all_image_para:
                text = para_data.get("text", "")
                if not text.strip() and not any(r.get("type") == "image" for r in runs):
                    continue

            style_name = para_data.get("style", "")
            heading_level = self.get_heading_level(style_name)

            if heading_level is not None:
                para = self._create_heading(para_data, heading_level)
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
                    para.paragraph_format.first_line_indent = self._char_indent(indent_value)
                except Exception:
                    pass

            para_cfg = self.template_config.get("paragraph", {})
            if para_cfg.get("paragraph_spacing", False) and heading_level is None:
                body_size = self._get_body_font_size()
                para.paragraph_format.space_after = Pt(body_size)

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
                    except Exception:
                        pass

    def _create_heading(self, para_data, heading_level):
        heading_config = self.template_config.get("heading", {})
        level_key = f"level{heading_level}"
        lvl_cfg = heading_config.get(level_key, {})

        font_name = lvl_cfg.get("font", "黑体")
        font_size = lvl_cfg.get("size", 16 if heading_level == 1 else 14 if heading_level == 2 else 13)
        bold = lvl_cfg.get("bold", True)
        spacing_before = lvl_cfg.get("spacing_before", 24 if heading_level == 1 else 18 if heading_level == 2 else 12)
        spacing_after = lvl_cfg.get("spacing_after", 18 if heading_level == 1 else 12 if heading_level == 2 else 6)
        alignment_str = lvl_cfg.get("alignment", "center" if heading_level == 1 else "left")

        para = self.doc.add_paragraph()

        for run_data in para_data.get("runs", []):
            run = para.add_run(run_data.get("text", ""))
            run.bold = bold
            run.font.size = Pt(font_size)
            run.font.color.rgb = RGBColor(0, 0, 0)
            self.set_run_font(run, font_name, is_chinese=True)

        if para_data.get("text") and not para_data.get("runs"):
            run = para.add_run(para_data["text"])
            run.bold = bold
            run.font.size = Pt(font_size)
            run.font.color.rgb = RGBColor(0, 0, 0)
            self.set_run_font(run, font_name, is_chinese=True)

        if alignment_str.upper() == "CENTER":
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif alignment_str.upper() == "LEFT":
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif alignment_str.upper() == "RIGHT":
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        if spacing_before:
            para.paragraph_format.space_before = Pt(spacing_before)
        if spacing_after:
            para.paragraph_format.space_after = Pt(spacing_after)

        return para

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

    def _generate_toc_page(self):
        toc_cfg = self.template_config.get("toc", {})
        if not toc_cfg.get("enabled", False):
            return

        title = toc_cfg.get("title", "目  录")
        title_font = toc_cfg.get("title_font", "黑体")
        title_size = toc_cfg.get("title_size", 16)
        max_level = toc_cfg.get("max_level", 3)

        body_start_idx = 0
        ast_paras = self.ast.get("paragraphs", [])
        for i, p in enumerate(ast_paras):
            if p.get("section") == "body":
                body_start_idx = i
                break

        toc_elements = []

        title_elem = OxmlElement('w:p')
        title_ppr = OxmlElement('w:pPr')
        title_jc = OxmlElement('w:jc')
        title_jc.set(qn('w:val'), 'center')
        title_ppr.append(title_jc)
        title_spacing = OxmlElement('w:spacing')
        title_spacing.set(qn('w:after'), '400')
        title_ppr.append(title_spacing)
        title_elem.append(title_ppr)
        title_r = OxmlElement('w:r')
        title_rpr = OxmlElement('w:rPr')
        title_b = OxmlElement('w:b')
        title_rpr.append(title_b)
        title_bcs = OxmlElement('w:bCs')
        title_rpr.append(title_bcs)
        title_sz = OxmlElement('w:sz')
        title_sz.set(qn('w:val'), str(title_size * 2))
        title_rpr.append(title_sz)
        title_szcs = OxmlElement('w:szCs')
        title_szcs.set(qn('w:val'), str(title_size * 2))
        title_rpr.append(title_szcs)
        title_rfonts = OxmlElement('w:rFonts')
        title_rfonts.set(qn('w:ascii'), title_font)
        title_rfonts.set(qn('w:hAnsi'), title_font)
        title_rfonts.set(qn('w:eastAsia'), title_font)
        title_rpr.insert(0, title_rfonts)
        title_color = OxmlElement('w:color')
        title_color.set(qn('w:val'), '000000')
        title_rpr.append(title_color)
        title_r.append(title_rpr)
        title_t = OxmlElement('w:t')
        title_t.set(qn('xml:space'), 'preserve')
        title_t.text = title
        title_r.append(title_t)
        title_elem.append(title_r)
        toc_elements.append(title_elem)

        toc_field_elem = OxmlElement('w:p')
        toc_ppr = OxmlElement('w:pPr')
        toc_field_elem.append(toc_ppr)

        r_begin = OxmlElement('w:r')
        fld_begin = OxmlElement('w:fldChar')
        fld_begin.set(qn('w:fldCharType'), 'begin')
        r_begin.append(fld_begin)
        toc_field_elem.append(r_begin)

        r_instr = OxmlElement('w:r')
        instr = OxmlElement('w:instrText')
        instr.set(qn('xml:space'), 'preserve')
        instr.text = f' TOC \\o "1-{max_level}" \\h \\z \\u '
        r_instr.append(instr)
        toc_field_elem.append(r_instr)

        r_sep = OxmlElement('w:r')
        fld_sep = OxmlElement('w:fldChar')
        fld_sep.set(qn('w:fldCharType'), 'separate')
        r_sep.append(fld_sep)
        toc_field_elem.append(r_sep)

        r_ph = OxmlElement('w:r')
        rph_rpr = OxmlElement('w:rPr')
        rph_color = OxmlElement('w:color')
        rph_color.set(qn('w:val'), '808080')
        rph_rpr.append(rph_color)
        rph_sz = OxmlElement('w:sz')
        rph_sz.set(qn('w:val'), '18')
        rph_rpr.append(rph_sz)
        r_ph.append(rph_rpr)
        t_ph = OxmlElement('w:t')
        t_ph.set(qn('xml:space'), 'preserve')
        t_ph.text = '（请在 Word 中按 Ctrl+A 全选后按 F9 更新域以生成目录）'
        r_ph.append(t_ph)
        toc_field_elem.append(r_ph)

        r_end = OxmlElement('w:r')
        fld_end = OxmlElement('w:fldChar')
        fld_end.set(qn('w:fldCharType'), 'end')
        r_end.append(fld_end)
        toc_field_elem.append(r_end)

        toc_elements.append(toc_field_elem)

        pb_elem = OxmlElement('w:p')
        pb_r = OxmlElement('w:r')
        pb_br = OxmlElement('w:br')
        pb_br.set(qn('w:type'), 'page')
        pb_r.append(pb_br)
        pb_elem.append(pb_r)
        toc_elements.append(pb_elem)

        doc_body = self.doc.element.body
        doc_paras = self.doc.paragraphs
        if body_start_idx < len(doc_paras):
            insert_before = doc_paras[body_start_idx]._element
            for elem in reversed(toc_elements):
                insert_before.addprevious(elem)
        else:
            for elem in toc_elements:
                doc_body.append(elem)

    def _apply_header_footer(self):
        header_cfg = self.template_config.get("header", {})
        footer_cfg = self.template_config.get("footer", {})

        for section in self.doc.sections:
            if header_cfg.get("enabled", False):
                header = section.header
                header.is_linked_to_previous = False
                if header.paragraphs:
                    hp = header.paragraphs[0]
                    hp.clear()
                else:
                    hp = header.add_paragraph()

                header_text = header_cfg.get("text", "")
                header_font = header_cfg.get("font", "宋体")
                header_size = header_cfg.get("size", 9)
                header_align = header_cfg.get("alignment", "center")
                header_sep = header_cfg.get("separator_line", True)

                hr = hp.add_run(header_text)
                hr.font.size = Pt(header_size)
                self.set_run_font(hr, header_font, is_chinese=True)

                if header_align == "center":
                    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif header_align == "left":
                    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif header_align == "right":
                    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

                if header_sep:
                    ppr = hp._element.get_or_add_pPr()
                    pbdr = OxmlElement('w:pBdr')
                    bottom = OxmlElement('w:bottom')
                    bottom.set(qn('w:val'), 'single')
                    bottom.set(qn('w:sz'), '4')
                    bottom.set(qn('w:space'), '1')
                    bottom.set(qn('w:color'), '000000')
                    pbdr.append(bottom)
                    ppr.append(pbdr)

            if footer_cfg.get("enabled", False):
                footer = section.footer
                footer.is_linked_to_previous = False
                if footer.paragraphs:
                    fp = footer.paragraphs[0]
                    fp.clear()
                else:
                    fp = footer.add_paragraph()

                footer_font = footer_cfg.get("font", "宋体")
                footer_size = footer_cfg.get("size", 9)
                footer_align = footer_cfg.get("alignment", "center")

                if footer_align == "center":
                    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif footer_align == "left":
                    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
                elif footer_align == "right":
                    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

                pn_fmt = footer_cfg.get("page_number_format", "arabic")
                if pn_fmt == "arabic":
                    field_xml = (
                        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
                        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
                    )
                elif pn_fmt == "roman":
                    field_xml = (
                        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                        '<w:r><w:instrText xml:space="preserve"> PAGE  \\*ROMAN </w:instrText></w:r>'
                        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
                    )
                else:
                    field_xml = (
                        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
                        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
                    )

                fp._element.append(
                    OxmlElement('w:r')
                )
                from lxml import etree
                for fragment in field_xml.split('</w:r>'):
                    fragment = fragment.strip()
                    if not fragment:
                        continue
                    if not fragment.endswith('>'):
                        fragment += '>'
                    try:
                        elem = etree.fromstring(fragment)
                        r_elem = fp._element.findall(qn('w:r'))[-1] if fp._element.findall(qn('w:r')) else fp._element
                        r_elem.append(elem) if elem.tag == qn('w:r') else fp._element.append(elem)
                    except Exception:
                        pass

                for r in fp.runs:
                    r.font.size = Pt(footer_size)
                    self.set_run_font(r, footer_font, is_chinese=True)

    def run(self, output_path):
        if self.source_docx_path and self.source_docx_path.exists():
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source_docx_path, output)
            self.doc = Document(str(output))
            self.convert_paragraphs_in_place()
            self._generate_toc_page()
            self._apply_header_footer()
            self.save(output_path)
        else:
            self.doc = Document()
            self.setup_document()
            self.convert_paragraphs()
            self.convert_tables()
            self._generate_toc_page()
            self._apply_header_footer()
            self.save(output_path)


if __name__ == "__main__":
    converter = ASTToDocxConverter(
        "workspace/normalized/normalized_ast.json",
        "workspace/validated/template_config.json",
        "workspace/input/source.docx"
    )
    converter.run("workspace/output/final.docx")
