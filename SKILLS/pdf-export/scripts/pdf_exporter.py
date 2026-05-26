import json
import platform
import subprocess
from pathlib import Path

from PyPDF2 import PdfReader


class PDFExporter:

    def __init__(self, docx_path):

        self.docx_path = Path(docx_path)

        self.output_dir = Path(
            "workspace/exported"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.report = {
            "export_engine": None,
            "pdf_pages": 0,
            "export_success": False,
            "errors": []
        }

    def detect_export_engine(self):

        system = platform.system()

        if system == "Windows":
            self.report[
                "export_engine"
            ] = "Word COM"

            return "word"

        else:
            self.report[
                "export_engine"
            ] = "LibreOffice"

            return "libreoffice"

    def export_with_libreoffice(self):

        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            str(self.docx_path),
            "--outdir",
            str(self.output_dir)
        ])

    def export_with_word(self):

        from docx2pdf import convert

        convert(
            str(self.docx_path),
            str(self.output_dir / "final.pdf")
        )

    def validate_pdf(self):

        pdf_path = (
            self.output_dir / "final.pdf"
        )

        if not pdf_path.exists():

            raise FileNotFoundError(
                "PDF export failed"
            )

        reader = PdfReader(
            str(pdf_path)
        )

        self.report["pdf_pages"] = (
            len(reader.pages)
        )

    def export_report(self):

        report_dir = Path(
            "workspace/reports"
        )

        report_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            report_dir /
            "pdf_export_report.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.report,
                f,
                ensure_ascii=False,
                indent=2
            )

    def run(self):

        try:

            engine = (
                self.detect_export_engine()
            )

            if engine == "word":
                self.export_with_word()

            else:
                self.export_with_libreoffice()

            self.validate_pdf()

            self.report[
                "export_success"
            ] = True

            self.export_report()

            print(
                "[INFO] PDF export completed"
            )

        except Exception as e:

            self.report["errors"].append(
                str(e)
            )

            self.export_report()

            print(
                f"[ERROR] {e}"
            )


if __name__ == "__main__":

    exporter = PDFExporter(
        "workspace/output/final.docx"
    )

    exporter.run()