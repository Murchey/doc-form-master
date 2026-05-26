import json
import zipfile
from pathlib import Path

from docx import Document
from lxml import etree


class DocxParser:
    def __init__(self, docx_path):
        self.docx_path = Path(docx_path)
        self.document = Document(docx_path)

        self.ast = {
            "metadata": {},
            "paragraphs": [],
            "tables": [],
            "images": [],
            "formulas": [],
            "styles": [],
            "sections": []
        }

    def validate_docx(self):
        if not self.docx_path.exists():
            raise FileNotFoundError(
                f"File not found: {self.docx_path}"
            )

        if self.docx_path.suffix.lower() != ".docx":
            raise ValueError(
                "Only .docx files are supported"
            )

    def parse_metadata(self):
        core = self.document.core_properties

        self.ast["metadata"] = {
            "author": core.author,
            "title": core.title,
            "created": str(core.created),
            "modified": str(core.modified)
        }

    def parse_styles(self):
        for style in self.document.styles:
            self.ast["styles"].append({
                "name": style.name,
                "type": str(style.type)
            })

    def parse_paragraphs(self):
        for idx, para in enumerate(self.document.paragraphs):

            paragraph_data = {
                "id": idx,
                "type": "paragraph",
                "text": para.text,
                "style": para.style.name if para.style else None,
                "alignment": str(para.alignment),
                "runs": []
            }

            for run in para.runs:
                run_data = {
                    "text": run.text,
                    "bold": run.bold,
                    "italic": run.italic,
                    "underline": run.underline,
                    "font_name": run.font.name,
                    "font_size": (
                        str(run.font.size)
                        if run.font.size
                        else None
                    )
                }

                paragraph_data["runs"].append(run_data)

            self.ast["paragraphs"].append(paragraph_data)

    def parse_tables(self):
        for table_idx, table in enumerate(self.document.tables):

            table_data = {
                "id": table_idx,
                "rows": []
            }

            for row in table.rows:
                row_data = []

                for cell in row.cells:
                    row_data.append(cell.text)

                table_data["rows"].append(row_data)

            self.ast["tables"].append(table_data)

    def extract_images(self):
        with zipfile.ZipFile(self.docx_path, "r") as zip_ref:

            media_files = [
                f for f in zip_ref.namelist()
                if f.startswith("word/media/")
            ]

            for idx, image_path in enumerate(media_files):

                self.ast["images"].append({
                    "id": idx,
                    "path": image_path
                })

    def parse_formulas(self):

        with zipfile.ZipFile(self.docx_path, "r") as zip_ref:
            xml_content = zip_ref.read("word/document.xml")

        root = etree.fromstring(xml_content)

        namespaces = {
            "m": (
                "http://schemas.openxmlformats.org/"
                "officeDocument/2006/math"
            )
        }

        formulas = root.xpath(
            "//m:oMath",
            namespaces=namespaces
        )

        for idx, formula in enumerate(formulas):

            self.ast["formulas"].append({
                "id": idx,
                "xml": etree.tostring(
                    formula
                ).decode("utf-8")
            })

    def export_ast(self, output_path):

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.ast,
                f,
                ensure_ascii=False,
                indent=2
            )

    def run(self):

        self.validate_docx()

        self.parse_metadata()

        self.parse_styles()

        self.parse_paragraphs()

        self.parse_tables()

        self.extract_images()

        self.parse_formulas()

        self.export_ast(
            "workspace/parsed/document_ast.json"
        )

        print(
            "[INFO] AST exported successfully"
        )


if __name__ == "__main__":

    parser = DocxParser(
        "workspace/input/《智能体平台应用》课程作业.docx"
    )

    parser.run()