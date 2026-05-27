import json
import re
import zipfile
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


class ZeroFormatNormalizer:
    def __init__(self, source_docx_path, template_config_path=None):
        self.source_docx_path = Path(source_docx_path)
        self.template_config = self._load_template_config(template_config_path)
        self.doc = None
        self.ast = {
            "paragraphs": [],
            "tables": [],
            "images": []
        }
        self._image_counter = 0

    def _load_template_config(self, config_path):
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._get_default_config()

    def _get_default_config(self):
        return {
            "fonts": {
                "chinese": {"family": "宋体", "size": 12},
                "english": {"family": "Times New Roman", "size": 12}
            },
            "heading": {
                "level1": {"font": "黑体", "size": 14, "bold": True, "alignment": "center", "spacing_before": 24, "spacing_after": 18},
                "level2": {"font": "黑体", "size": 12, "bold": True, "alignment": "left", "spacing_before": 18, "spacing_after": 12},
                "level3": {"font": "宋体", "size": 12, "bold": True, "alignment": "left", "spacing_before": 12, "spacing_after": 6}
            },
            "paragraph": {
                "alignment": "justify",
                "line_spacing": 1.5,
                "first_indent": 2,
                "paragraph_spacing": False
            },
            "toc": {
                "enabled": True,
                "title": "目  录",
                "title_font": "黑体",
                "title_size": 16,
                "max_level": 3
            },
            "header": {
                "enabled": True,
                "text": "",
                "font": "宋体",
                "size": 9,
                "alignment": "center",
                "separator_line": True
            },
            "footer": {
                "enabled": True,
                "page_number_format": "arabic",
                "font": "宋体",
                "size": 9,
                "alignment": "center"
            },
            "image": {
                "max_width_percent": 80
            }
        }

    def extract_content(self):
        source_doc = Document(str(self.source_docx_path))

        image_rels = self._build_image_relationship_map()

        for para in source_doc.paragraphs:
            para_data = {
                "text": para.text,
                "style": para.style.name if para.style else "Normal",
                "runs": []
            }

            for run in para.runs:
                run_data = {
                    "text": run.text,
                    "bold": run.bold,
                    "italic": run.italic,
                    "font_name": run.font.name,
                    "font_size": str(run.font.size) if run.font.size else None
                }
                para_data["runs"].append(run_data)

            self.ast["paragraphs"].append(para_data)

        for table in source_doc.tables:
            table_data = {"rows": []}
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text)
                table_data["rows"].append(row_data)
            self.ast["tables"].append(table_data)

        self._extract_images_from_docx(image_rels)

    def _build_image_relationship_map(self):
        image_rels = {}
        try:
            with zipfile.ZipFile(self.source_docx_path, "r") as zip_ref:
                if "word/_rels/document.xml.rels" in zip_ref.namelist():
                    rels_xml = zip_ref.read("word/_rels/document.xml.rels")
                    from lxml import etree
                    rels_root = etree.fromstring(rels_xml)
                    for rel in rels_root:
                        rel_id = rel.get('Id')
                        target = rel.get('Target', '')
                        if target.startswith('media/'):
                            image_rels[rel_id] = f'word/{target}'
        except Exception as e:
            print(f"[WARNING] Failed to build image relationship map: {e}")
        return image_rels

    def _extract_images_from_docx(self, image_rels):
        try:
            with zipfile.ZipFile(self.source_docx_path, "r") as zip_ref:
                media_files = [f for f in zip_ref.namelist() if f.startswith("word/media/")]
                for idx, image_path in enumerate(media_files):
                    self.ast["images"].append({
                        "id": idx,
                        "path": image_path,
                        "data": zip_ref.read(image_path)
                    })
        except Exception as e:
            print(f"[WARNING] Failed to extract images: {e}")

    def _detect_structure(self):
        paras = self.ast["paragraphs"]
        cover_end = 0
        toc_start = -1
        toc_end = -1

        toc_keywords = ["目录", "目 录", "目  录", "table of contents", "contents"]

        for i, p in enumerate(paras):
            text = (p.get("text") or "").strip()
            text_lower = text.lower()

            if any(kw in text_lower for kw in toc_keywords):
                toc_start = i

            if re.match(r'^\d+(\.\d+)*\s+\S', text):
                if cover_end == 0:
                    cover_end = i
                if toc_start >= 0 and toc_end < 0:
                    toc_end = i
                break

        if cover_end == 0:
            for i, p in enumerate(paras):
                text = (p.get("text") or "").strip()
                if text and len(text) > 5:
                    cover_end = i
                    break

        if toc_start >= 0 and toc_end < 0:
            for i in range(toc_start + 1, len(paras)):
                text = (paras[i].get("text") or "").strip()
                if re.match(r'^\d+(\.\d+)*\s+\S', text):
                    toc_end = i
                    break
            if toc_end < 0:
                toc_end = min(toc_start + 20, len(paras))

        for i, p in enumerate(paras):
            if toc_start >= 0 and toc_start <= i < toc_end:
                p["section"] = "toc"
            elif i < cover_end:
                p["section"] = "cover"
            else:
                p["section"] = "body"

        self.ast["section_regions"] = {
            "cover_end": cover_end,
            "toc_start": toc_start,
            "toc_end": toc_end
        }

    def _detect_heading_level(self, text):
        if re.match(r'^\d+\s+\S', text):
            return 1
        elif re.match(r'^\d+\.\d+\s+\S', text):
            return 2
        elif re.match(r'^\d+\.\d+\.\d+\s+\S', text):
            return 3
        return None

    def create_formatted_document(self):
        self.doc = Document()

        section = self.doc.sections[0]
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)

        page_cfg = self.template_config.get("page", {})
        section.top_margin = Cm(page_cfg.get("margin_top", 2.54))
        section.bottom_margin = Cm(page_cfg.get("margin_bottom", 2.54))
        section.left_margin = Cm(page_cfg.get("margin_left", 3.17))
        section.right_margin = Cm(page_cfg.get("margin_right", 2.54))

        self._detect_structure()

        self._add_cover_page()
        self._add_toc_page()
        self._add_body_content()
        self._add_references_section()
        self._create_sections()
        self._add_header_footer()

    def _add_cover_page(self):
        cover_paras = [p for p in self.ast["paragraphs"] if p.get("section") == "cover"]

        for para_data in cover_paras:
            text = para_data.get("text", "").strip()
            if not text:
                para = self.doc.add_paragraph()
                continue

            para = self.doc.add_paragraph()
            run = para.add_run(text)

            if len(text) < 30 and not any(c in text for c in ['。', '，', '；']):
                run.bold = True
                run.font.size = Pt(16)
                self._set_run_font(run, "黑体", True)
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                run.font.size = Pt(12)
                self._set_run_font(run, "宋体", True)

    def _add_toc_page(self):
        toc_cfg = self.template_config.get("toc", {})
        if not toc_cfg.get("enabled", False):
            return

        title = toc_cfg.get("title", "目  录")
        title_font = toc_cfg.get("title_font", "黑体")
        title_size = toc_cfg.get("title_size", 16)
        max_level = toc_cfg.get("max_level", 3)

        para = self.doc.add_paragraph()
        run = para.add_run(title)
        run.bold = True
        run.font.size = Pt(title_size)
        run.font.color.rgb = RGBColor(0, 0, 0)
        self._set_run_font(run, title_font, True)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_after = Pt(20)

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
        r_ph.append(rph_rpr)
        t_ph = OxmlElement('w:t')
        t_ph.set(qn('xml:space'), 'preserve')
        t_ph.text = '（目录将在 Word 中自动更新）'
        r_ph.append(t_ph)
        toc_field_elem.append(r_ph)

        r_end = OxmlElement('w:r')
        fld_end = OxmlElement('w:fldChar')
        fld_end.set(qn('w:fldCharType'), 'end')
        r_end.append(fld_end)
        toc_field_elem.append(r_end)

        self.doc.element.body.append(toc_field_elem)

        self._enable_auto_update_fields()

        pb_elem = OxmlElement('w:p')
        pb_r = OxmlElement('w:r')
        pb_br = OxmlElement('w:br')
        pb_br.set(qn('w:type'), 'page')
        pb_r.append(pb_br)
        pb_elem.append(pb_r)
        self.doc.element.body.append(pb_elem)

    def _add_body_content(self):
        body_paras = [p for p in self.ast["paragraphs"] if p.get("section") == "body"]

        for para_data in body_paras:
            text = para_data.get("text", "").strip()
            if not text:
                continue

            heading_level = self._detect_heading_level(text)

            if heading_level:
                self._add_heading(text, heading_level)
            else:
                self._add_normal_paragraph(text)

    def _add_heading(self, text, level):
        heading_cfg = self.template_config.get("heading", {})
        level_key = f"level{level}"
        cfg = heading_cfg.get(level_key, {})

        font_name = cfg.get("font", "黑体")
        font_size = cfg.get("size", 14 if level == 1 else 12)
        bold = cfg.get("bold", True)
        alignment_str = cfg.get("alignment", "center" if level == 1 else "left")
        spacing_before = cfg.get("spacing_before", 24 if level == 1 else 18)
        spacing_after = cfg.get("spacing_after", 18 if level == 1 else 12)

        para = self.doc.add_paragraph()
        run = para.add_run(text)
        run.bold = bold
        run.font.size = Pt(font_size)
        run.font.color.rgb = RGBColor(0, 0, 0)
        self._set_run_font(run, font_name, True)

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

    def _add_normal_paragraph(self, text):
        para_cfg = self.template_config.get("paragraph", {})
        fonts_cfg = self.template_config.get("fonts", {})

        chinese_font = fonts_cfg.get("chinese", {}).get("family", "宋体")
        body_size = fonts_cfg.get("chinese", {}).get("size", 12)
        alignment = para_cfg.get("alignment", "justify").upper()
        line_spacing = para_cfg.get("line_spacing", 1.5)
        first_indent = para_cfg.get("first_indent", 2)

        para = self.doc.add_paragraph()
        run = para.add_run(text)

        is_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
        font_name = chinese_font if is_chinese else fonts_cfg.get("english", {}).get("family", "Times New Roman")
        self._set_run_font(run, font_name, is_chinese)
        run.font.size = Pt(body_size)

        if alignment == "JUSTIFY":
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif alignment == "CENTER":
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif alignment == "LEFT":
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif alignment == "RIGHT":
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        para.paragraph_format.line_spacing = line_spacing
        para.paragraph_format.first_line_indent = Pt(int(first_indent * body_size))

    def _add_references_section(self):
        ref_keywords = ["参考文献", "references", "bibliography"]
        ref_start = -1

        for i, p in enumerate(self.ast["paragraphs"]):
            text = (p.get("text") or "").strip().lower()
            if any(kw in text for kw in ref_keywords):
                ref_start = i
                break

        if ref_start < 0:
            return

        para = self.doc.add_paragraph()
        run = para.add_run("参考文献")
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)
        self._set_run_font(run, "黑体", True)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(24)
        para.paragraph_format.space_after = Pt(18)

        for p in self.ast["paragraphs"][ref_start + 1:]:
            text = p.get("text", "").strip()
            if not text:
                continue

            para = self.doc.add_paragraph()
            run = para.add_run(text)
            run.font.size = Pt(10.5)
            self._set_run_font(run, "宋体", True)
            para.paragraph_format.line_spacing = 1.5

    def _create_sections(self):
        doc_body = self.doc.element.body

        cover_paras = [p for p in self.ast["paragraphs"] if p.get("section") == "cover"]
        if cover_paras:
            cover_end_idx = len(cover_paras)
            if cover_end_idx < len(self.doc.paragraphs):
                cover_last = self.doc.paragraphs[cover_end_idx - 1]._element
                ppr = cover_last.find(qn('w:pPr'))
                if ppr is None:
                    ppr = OxmlElement('w:pPr')
                    cover_last.insert(0, ppr)
                sect_pr = OxmlElement('w:sectPr')
                self._set_section_properties(sect_pr, is_cover=True)
                ppr.append(sect_pr)

        toc_paras = [p for p in self.ast["paragraphs"] if p.get("section") == "toc"]
        if toc_paras:
            toc_end_idx = len(cover_paras) + len(toc_paras) + 1
            if toc_end_idx < len(self.doc.paragraphs):
                toc_last = self.doc.paragraphs[toc_end_idx - 1]._element
                ppr = toc_last.find(qn('w:pPr'))
                if ppr is None:
                    ppr = OxmlElement('w:pPr')
                    toc_last.insert(0, ppr)
                sect_pr = OxmlElement('w:sectPr')
                self._set_section_properties(sect_pr, is_toc=True)
                ppr.append(sect_pr)

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
            if not is_ref:
                pg_num_type.set(qn('w:start'), '1')
            sect_pr.append(pg_num_type)

    def _add_header_footer(self):
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
                    self._set_run_font(hr, header_font, is_chinese=True)

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
                        self._set_run_font(r, footer_font, is_chinese=True)

    def _enable_auto_update_fields(self):
        settings_part = self.doc.settings.element
        update_fields = settings_part.find(qn('w:updateFields'))
        if update_fields is None:
            update_fields = OxmlElement('w:updateFields')
            settings_part.append(update_fields)
        update_fields.set(qn('w:val'), 'true')

    @staticmethod
    def _set_run_font(run, font_name, is_chinese=False):
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

    def save(self, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(output_path))
        print(f"[INFO] Formatted DOCX saved to: {output_path}")

    def run(self, output_path):
        print(f"[INFO] Loading source DOCX: {self.source_docx_path}")
        self.extract_content()

        print(f"[INFO] Extracted {len(self.ast['paragraphs'])} paragraphs")
        print(f"[INFO] Extracted {len(self.ast['tables'])} tables")
        print(f"[INFO] Extracted {len(self.ast['images'])} images")

        print("[INFO] Creating formatted document...")
        self.create_formatted_document()

        print("[INFO] Saving formatted document...")
        self.save(output_path)

        print("[INFO] Zero format normalization completed!")
        return {
            "paragraphs": len(self.ast['paragraphs']),
            "tables": len(self.ast['tables']),
            "images": len(self.ast['images']),
            "output_path": str(output_path)
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python zero_format_normalizer.py <input.docx> <output.docx> [template.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    template_path = sys.argv[3] if len(sys.argv) > 3 else None

    normalizer = ZeroFormatNormalizer(input_path, template_path)
    result = normalizer.run(output_path)
    print(f"[INFO] Result: {json.dumps(result, indent=2)}")
