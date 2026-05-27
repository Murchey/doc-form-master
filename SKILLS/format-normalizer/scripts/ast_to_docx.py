import json
import base64
import shutil
import tempfile
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None


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

    @staticmethod
    def _validate_heading(para_data, heading_level):
        import re
        text = (para_data.get("text") or "").strip()
        if not text:
            return False

        if len(text) > 80:
            return False

        heading_pattern = r'^\d+(\.\d+)*\s*\S'
        if re.match(heading_pattern, text):
            return True

        if heading_level == 1:
            if len(text) > 30:
                return False
        elif heading_level == 2:
            if len(text) > 50:
                return False
        elif heading_level == 3:
            if len(text) > 60:
                return False

        ending_punctuations = ['。', '，', '；', '！', '？', '、', '.', ',', ';', '!', '?']
        if text and text[-1] in ending_punctuations:
            return False

        return True

    def setup_document(self):
        section = self.doc.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.18)
        section.right_margin = Cm(3.18)

    def _get_available_width(self):
        try:
            section = self.doc.sections[0]
            page_width = section.page_width
            left_margin = section.left_margin
            right_margin = section.right_margin
            return page_width - left_margin - right_margin
        except (IndexError, AttributeError):
            return Cm(21) - Cm(3.18) - Cm(3.18)

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

            image_cfg = self.template_config.get("image", {})
            max_width_percent = image_cfg.get("max_width_percent", 80) / 100.0
            available_width = self._get_available_width()
            max_width = int(available_width * max_width_percent)

            img_width = None
            img_height = None
            if PILImage:
                try:
                    with PILImage.open(tmp_path) as pil_img:
                        img_width, img_height = pil_img.size
                except Exception:
                    pass

            run = para.add_run()
            if img_width and img_height and img_width > max_width:
                ratio = max_width / img_width
                new_height = int(img_height * ratio)
                run.add_picture(tmp_path, width=Emu(max_width), height=Emu(new_height))
            else:
                run.add_picture(tmp_path, width=Emu(max_width))

            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            Path(tmp_path).unlink(missing_ok=True)
            self._image_counter += 1
        except Exception as e:
            import traceback
            print(f"[WARNING] Image processing error: {e}")
            traceback.print_exc()

    @staticmethod
    def _clear_paragraph(para):
        p_elem = para._element
        for child in list(p_elem):
            tag_local = child.tag.split('}')[1] if '}' in child.tag else child.tag
            if tag_local == 'r':
                p_elem.remove(child)

    def _is_protected(self, para_data):
        return para_data.get("section", "") == "cover"

    @staticmethod
    def _normalize_alignment(alignment_str):
        if not alignment_str or alignment_str == "None":
            return None
        alignment_upper = alignment_str.upper()
        if "CENTER" in alignment_upper:
            return "CENTER"
        elif "RIGHT" in alignment_upper:
            return "RIGHT"
        elif "JUSTIFY" in alignment_upper:
            return "JUSTIFY"
        elif "LEFT" in alignment_upper:
            return "LEFT"
        return None

    def convert_paragraphs_in_place(self):
        doc_paras = self.doc.paragraphs
        ast_paras = self.ast.get("paragraphs", [])
        count = min(len(doc_paras), len(ast_paras))

        for i in range(count):
            para_data = ast_paras[i]

            if self._is_protected(para_data):
                continue

            if self._is_code_block(para_data):
                para = doc_paras[i]
                self._clear_paragraph(para)
                para._element.addnext(self._add_code_block_to_table(para_data)._element)
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
                if self._validate_heading(para_data, heading_level):
                    self._apply_heading(para_data, heading_level, para)
                else:
                    self._apply_normal_paragraph(para_data, para)
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

    def _get_default_font(self, is_chinese=True):
        fonts_cfg = self.template_config.get("fonts", {})
        if is_chinese:
            return fonts_cfg.get("chinese", {}).get("family", "宋体")
        return fonts_cfg.get("english", {}).get("family", "Times New Roman")

    @staticmethod
    def _is_code_block(para_data):
        style = (para_data.get("style") or "").lower()
        if "code" in style or "source" in style:
            return True
        runs = para_data.get("runs", [])
        if not runs:
            return False
        code_fonts = ["consolas", "courier new", "monaco", "menlo", "dejavu sans mono", "liberation mono"]
        for run in runs:
            font = (run.get("font_name") or "").lower()
            if font in code_fonts:
                return True
        return False

    def _add_code_block_to_table(self, para_data):
        table = self.doc.add_table(rows=1, cols=1)
        table.style = 'Table Grid'
        cell = table.cell(0, 0)
        cell_para = cell.paragraphs[0]
        
        for run_data in para_data.get("runs", []):
            run = cell_para.add_run(run_data.get("text", ""))
            font_name = run_data.get("font_name") or "Consolas"
            run.font.name = font_name
            rpr = run._element.get_or_add_rPr()
            rFonts = rpr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = OxmlElement('w:rFonts')
                rpr.insert(0, rFonts)
            rFonts.set(qn('w:ascii'), font_name)
            rFonts.set(qn('w:hAnsi'), font_name)
            rFonts.set(qn('w:eastAsia'), font_name)
            if run_data.get("font_size"):
                try:
                    size = int(run_data["font_size"].replace("pt", ""))
                    run.font.size = Pt(size)
                except Exception:
                    run.font.size = Pt(10)
            else:
                run.font.size = Pt(10)

        return table

    def _char_indent(self, char_count):
        body_size = self._get_body_font_size()
        return Pt(int(char_count * body_size))

    def _apply_normal_paragraph(self, para_data, para):
        runs = para_data.get("runs", [])
        has_image = any(r.get("type") == "image" for r in runs)

        self._clear_paragraph(para)

        para_cfg = self.template_config.get("paragraph", {})
        default_align = para_cfg.get("alignment", "justify").upper()

        if has_image:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            if default_align == "JUSTIFY":
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            elif default_align == "CENTER":
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif default_align == "LEFT":
                para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif default_align == "RIGHT":
                para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        first_indent = para_cfg.get("first_indent", 2)
        para.paragraph_format.first_line_indent = self._char_indent(first_indent)

        line_spacing = para_cfg.get("line_spacing", 1.5)
        para.paragraph_format.line_spacing = line_spacing

        if para_cfg.get("paragraph_spacing", False):
            body_size = self._get_body_font_size()
            para.paragraph_format.space_after = Pt(body_size)

        chinese_font = self._get_default_font(True)
        english_font = self._get_default_font(False)
        body_size = self._get_body_font_size()

        for run_data in runs:
            if run_data.get("type") == "image":
                self._add_image_to_paragraph(para, run_data)
                continue

            run = para.add_run(run_data.get("text", ""))
            if run_data.get("bold"):
                run.bold = True
            if run_data.get("italic"):
                run.italic = True

            text_content = run_data.get("text", "")
            is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text_content)
            font_name = chinese_font if is_chinese else english_font
            self.set_run_font(run, font_name, is_chinese)
            run.font.size = Pt(body_size)

    def convert_paragraphs(self):
        para_cfg = self.template_config.get("paragraph", {})
        default_align = para_cfg.get("alignment", "justify").upper()
        chinese_font = self._get_default_font(True)
        english_font = self._get_default_font(False)
        body_size = self._get_body_font_size()

        for para_data in self.ast.get("paragraphs", []):
            if self._is_protected(para_data):
                continue

            if self._is_code_block(para_data):
                self._add_code_block_to_table(para_data)
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

            if heading_level is not None:
                pass
            else:
                has_image = any(r.get("type") == "image" for r in runs)
                if has_image:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    if default_align == "JUSTIFY":
                        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    elif default_align == "CENTER":
                        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    elif default_align == "LEFT":
                        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    elif default_align == "RIGHT":
                        para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

                first_indent = para_cfg.get("first_indent", 2)
                para.paragraph_format.first_line_indent = self._char_indent(first_indent)

                line_spacing = para_cfg.get("line_spacing", 1.5)
                para.paragraph_format.line_spacing = line_spacing

                if para_cfg.get("paragraph_spacing", False):
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

                    text_content = run_data.get("text", "")
                    is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text_content)
                    font_name = chinese_font if is_chinese else english_font
                    self.set_run_font(run, font_name, is_chinese)
                    run.font.size = Pt(body_size)

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
            table.alignment = 1
            for i, row_data in enumerate(rows):
                for j, cell_text in enumerate(row_data):
                    cell = table.cell(i, j)
                    cell.text = cell_text
                    for para in cell.paragraphs:
                        for run in para.runs:
                            font_name = self._get_default_font(True)
                            run.font.name = font_name
                            rpr = run._element.get_or_add_rPr()
                            rFonts = rpr.find(qn('w:rFonts'))
                            if rFonts is None:
                                rFonts = OxmlElement('w:rFonts')
                                rpr.insert(0, rFonts)
                            rFonts.set(qn('w:ascii'), font_name)
                            rFonts.set(qn('w:hAnsi'), font_name)
                            rFonts.set(qn('w:eastAsia'), font_name)
                            if not run.font.size:
                                run.font.size = Pt(self._get_body_font_size())

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

        doc_body = self.doc.element.body
        doc_paras = self.doc.paragraphs

        if body_start_idx >= len(doc_paras):
            return

        insert_before = doc_paras[body_start_idx]._element

        title_elem = OxmlElement('w:p')
        title_ppr = OxmlElement('w:pPr')
        title_jc = OxmlElement('w:jc')
        title_jc.set(qn('w:val'), 'center')
        title_ppr.append(title_jc)
        title_spacing = OxmlElement('w:spacing')
        title_spacing.set(qn('w:before'), '240')
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
        t_ph.text = '（目录将在 Word 中自动更新）'
        r_ph.append(t_ph)
        toc_field_elem.append(r_ph)

        self._enable_auto_update_fields()

        r_end = OxmlElement('w:r')
        fld_end = OxmlElement('w:fldChar')
        fld_end.set(qn('w:fldCharType'), 'end')
        r_end.append(fld_end)
        toc_field_elem.append(r_end)

        pb_elem = OxmlElement('w:p')
        pb_r = OxmlElement('w:r')
        pb_br = OxmlElement('w:br')
        pb_br.set(qn('w:type'), 'page')
        pb_r.append(pb_br)
        pb_elem.append(pb_r)

        insert_before.addprevious(title_elem)
        insert_before.addprevious(toc_field_elem)
        insert_before.addprevious(pb_elem)

    def _enable_auto_update_fields(self):
        settings_part = self.doc.settings.element
        update_fields = settings_part.find(qn('w:updateFields'))
        if update_fields is None:
            update_fields = OxmlElement('w:updateFields')
            settings_part.append(update_fields)
        update_fields.set(qn('w:val'), 'true')

    def _apply_header_footer(self):
        header_cfg = self.template_config.get("header", {})
        footer_cfg = self.template_config.get("footer", {})

        sections = self.doc.sections
        if len(sections) < 1:
            return

        for i, section in enumerate(sections):
            if i == 0:
                section.header.is_linked_to_previous = False
                section.footer.is_linked_to_previous = False
                if header_cfg.get("enabled", False):
                    header = section.header
                    if header.paragraphs:
                        hp = header.paragraphs[0]
                        hp.clear()
                    else:
                        hp = header.add_paragraph()
                    hr = hp.add_run("")
                    hr.font.size = Pt(header_cfg.get("size", 9))
                if footer_cfg.get("enabled", False):
                    footer = section.footer
                    if footer.paragraphs:
                        fp = footer.paragraphs[0]
                        fp.clear()
                    else:
                        fp = footer.add_paragraph()
                    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif i == 1:
                section.header.is_linked_to_previous = False
                section.footer.is_linked_to_previous = False
                if header_cfg.get("enabled", False):
                    header = section.header
                    if header.paragraphs:
                        hp = header.paragraphs[0]
                        hp.clear()
                    else:
                        hp = header.add_paragraph()
                    hr = hp.add_run("")
                    hr.font.size = Pt(header_cfg.get("size", 9))
                if footer_cfg.get("enabled", False):
                    footer = section.footer
                    if footer.paragraphs:
                        fp = footer.paragraphs[0]
                        fp.clear()
                    else:
                        fp = footer.add_paragraph()
                    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                section.header.is_linked_to_previous = False
                section.footer.is_linked_to_previous = False

                if header_cfg.get("enabled", False):
                    header = section.header
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

                    from lxml import etree
                    r_begin = OxmlElement('w:r')
                    fld_begin = OxmlElement('w:fldChar')
                    fld_begin.set(qn('w:fldCharType'), 'begin')
                    r_begin.append(fld_begin)
                    fp._element.append(r_begin)

                    r_instr = OxmlElement('w:r')
                    instr = OxmlElement('w:instrText')
                    instr.set(qn('xml:space'), 'preserve')
                    instr.text = ' PAGE '
                    r_instr.append(instr)
                    fp._element.append(r_instr)

                    r_end = OxmlElement('w:r')
                    fld_end = OxmlElement('w:fldChar')
                    fld_end.set(qn('w:fldCharType'), 'end')
                    r_end.append(fld_end)
                    fp._element.append(r_end)

                    for r in fp.runs:
                        r.font.size = Pt(footer_size)
                        self.set_run_font(r, footer_font, is_chinese=True)

    def _fix_table_fonts_in_place(self):
        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        for run in para.runs:
                            font_name = self._get_default_font(True)
                            run.font.name = font_name
                            rpr = run._element.get_or_add_rPr()
                            rFonts = rpr.find(qn('w:rFonts'))
                            if rFonts is None:
                                rFonts = OxmlElement('w:rFonts')
                                rpr.insert(0, rFonts)
                            rFonts.set(qn('w:ascii'), font_name)
                            rFonts.set(qn('w:hAnsi'), font_name)
                            rFonts.set(qn('w:eastAsia'), font_name)
                            if not run.font.size:
                                run.font.size = Pt(self._get_body_font_size())

    def _insert_page_break_before_references(self):
        ast_paras = self.ast.get("paragraphs", [])
        doc_paras = self.doc.paragraphs
        count = min(len(doc_paras), len(ast_paras))
        for i in range(count):
            para_data = ast_paras[i]
            text = (para_data.get("text") or "").strip()
            style = para_data.get("style", "") or ""
            if "Heading 1" in style and "参考文献" in text:
                para = doc_paras[i]
                p_elem = para._element
                ppr = p_elem.find(qn('w:pPr'))
                if ppr is None:
                    ppr = OxmlElement('w:pPr')
                    p_elem.insert(0, ppr)
                existing_pb = False
                for child in ppr:
                    tag_local = child.tag.split('}')[1] if '}' in child.tag else child.tag
                    if tag_local == 'pageBreakBefore':
                        existing_pb = True
                        break
                if not existing_pb:
                    pb = OxmlElement('w:pageBreakBefore')
                    ppr.append(pb)
                break

    def _remove_all_sections(self):
        doc_body = self.doc.element.body
        sect_prs = doc_body.findall(qn('w:sectPr'))
        for sect_pr in sect_prs:
            doc_body.remove(sect_pr)
        
        for para in self.doc.paragraphs:
            p_elem = para._element
            ppr = p_elem.find(qn('w:pPr'))
            if ppr is not None:
                sect_pr = ppr.find(qn('w:sectPr'))
                if sect_pr is not None:
                    ppr.remove(sect_pr)

    def _normalize_sections(self):
        ast_paras = self.ast.get("paragraphs", [])
        doc_paras = self.doc.paragraphs
        count = min(len(doc_paras), len(ast_paras))

        cover_end = 0
        ref_start = count

        for i, p in enumerate(ast_paras):
            section = p.get("section", "")
            text = (p.get("text") or "").strip()
            style = p.get("style", "") or ""
            if section == "cover":
                cover_end = max(cover_end, i + 1)
            if "Heading 1" in style and "参考文献" in text:
                ref_start = i

        toc_start = cover_end
        toc_end = cover_end
        for i in range(cover_end, count):
            if i < len(ast_paras):
                style = ast_paras[i].get("style", "") or ""
                if "Heading 1" in style:
                    toc_end = i
                    break

        if toc_end <= toc_start:
            toc_end = toc_start

        if cover_end > 0 and cover_end < len(doc_paras):
            cover_last = doc_paras[cover_end - 1]._element
            ppr = cover_last.find(qn('w:pPr'))
            if ppr is None:
                ppr = OxmlElement('w:pPr')
                cover_last.insert(0, ppr)
            sect_pr = OxmlElement('w:sectPr')
            self._set_section_properties(sect_pr, is_cover=True)
            ppr.append(sect_pr)

        if toc_end > toc_start and toc_end < len(doc_paras):
            toc_last = doc_paras[toc_end - 1]._element
            ppr = toc_last.find(qn('w:pPr'))
            if ppr is None:
                ppr = OxmlElement('w:pPr')
                toc_last.insert(0, ppr)
            sect_pr = OxmlElement('w:sectPr')
            self._set_section_properties(sect_pr, is_toc=True)
            ppr.append(sect_pr)

        if ref_start < count and ref_start < len(doc_paras):
            ref_para = doc_paras[ref_start]._element
            ppr = ref_para.find(qn('w:pPr'))
            if ppr is None:
                ppr = OxmlElement('w:pPr')
                ref_para.insert(0, ppr)
            sect_pr = OxmlElement('w:sectPr')
            self._set_section_properties(sect_pr, is_ref=True)
            ppr.append(sect_pr)

        doc_body = self.doc.element.body
        final_sect_pr = OxmlElement('w:sectPr')
        self._set_section_properties(final_sect_pr, is_final=True)
        doc_body.append(final_sect_pr)

    def _set_section_properties(self, sect_pr, is_cover=False, is_toc=False, is_ref=False, is_final=False):
        pg_sz = OxmlElement('w:pgSz')
        pg_sz.set(qn('w:w'), '11906')
        pg_sz.set(qn('w:h'), '16838')
        sect_pr.append(pg_sz)

        pg_mar = OxmlElement('w:pgMar')
        pg_mar.set(qn('w:top'), '1440')
        pg_mar.set(qn('w:right'), '1800')
        pg_mar.set(qn('w:bottom'), '1440')
        pg_mar.set(qn('w:left'), '1800')
        pg_mar.set(qn('w:header'), '851')
        pg_mar.set(qn('w:footer'), '992')
        pg_mar.set(qn('w:gutter'), '0')
        sect_pr.append(pg_mar)

        if not is_cover and not is_toc:
            pg_num_type = OxmlElement('w:pgNumType')
            if is_ref:
                pass
            else:
                pg_num_type.set(qn('w:start'), '1')
            sect_pr.append(pg_num_type)

    def run(self, output_path):
        if self.source_docx_path and self.source_docx_path.exists():
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source_docx_path, output)
            self.doc = Document(str(output))
            self._remove_all_sections()
            self.convert_paragraphs_in_place()
            self._fix_table_fonts_in_place()
            self._generate_toc_page()
            self._normalize_sections()
            self._apply_header_footer()
            self.save(output_path)
        else:
            self.doc = Document()
            self.setup_document()
            self.convert_paragraphs()
            self.convert_tables()
            self._generate_toc_page()
            self._normalize_sections()
            self._apply_header_footer()
            self.save(output_path)


if __name__ == "__main__":
    converter = ASTToDocxConverter(
        "workspace/normalized/normalized_ast.json",
        "workspace/validated/template_config.json",
        "workspace/input/source.docx"
    )
    converter.run("workspace/output/final.docx")
