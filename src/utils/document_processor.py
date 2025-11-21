"""
Document processor for extracting text from various file formats.
Supports: PDF, Word (DOCX), CSV, Excel (XLSX), and plain text.
"""

import io
import logging
from typing import Optional
from pathlib import Path
from src.utils.exception_handler import DocumentProcessingError, log_exception
from src.utils.logger import setup_logger

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import pandas as pd
except ImportError:
    pd = None

logger = setup_logger(__name__)


class DocumentProcessor:
    """Process various document formats and extract text."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file."""
        if PdfReader is None:
            error_msg = "PyPDF2 is required for PDF processing. Install with: pip install pypdf2"
            logger.error(error_msg)
            raise DocumentProcessingError(error_msg, details={"file_type": "PDF", "missing_dependency": "PyPDF2"})

        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)

            if len(pdf_reader.pages) == 0:
                logger.warning("PDF file has no pages")
                return ""

            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"--- Page {page_num} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue

            if not text_parts:
                logger.warning("No text could be extracted from PDF")
                return ""

            logger.info(f"Successfully extracted text from {len(text_parts)} pages")
            return "\n\n".join(text_parts)

        except DocumentProcessingError:
            raise
        except Exception as e:
            log_exception(e, context="DocumentProcessor.extract_text_from_pdf")
            raise DocumentProcessingError(
                f"Failed to process PDF: {str(e)}",
                details={"file_type": "PDF", "error": str(e)}
            )
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from Word DOCX file."""
        if Document is None:
            error_msg = "python-docx is required for Word processing. Install with: pip install python-docx"
            logger.error(error_msg)
            raise DocumentProcessingError(error_msg, details={"file_type": "DOCX", "missing_dependency": "python-docx"})

        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)

            text_parts = []

            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)

            # Also extract text from tables
            for table in doc.tables:
                try:
                    for row in table.rows:
                        row_text = " | ".join(cell.text.strip() for cell in row.cells)
                        if row_text.strip():
                            text_parts.append(row_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from table: {e}")
                    continue

            if not text_parts:
                logger.warning("No text could be extracted from DOCX")
                return ""

            logger.info(f"Successfully extracted text from DOCX ({len(text_parts)} elements)")
            return "\n".join(text_parts)

        except DocumentProcessingError:
            raise
        except Exception as e:
            log_exception(e, context="DocumentProcessor.extract_text_from_docx")
            raise DocumentProcessingError(
                f"Failed to process Word document: {str(e)}",
                details={"file_type": "DOCX", "error": str(e)}
            )
    
    @staticmethod
    def extract_text_from_csv(file_content: bytes) -> str:
        """Extract text from CSV file."""
        if pd is None:
            error_msg = "pandas is required for CSV processing. Install with: pip install pandas"
            logger.error(error_msg)
            raise DocumentProcessingError(error_msg, details={"file_type": "CSV", "missing_dependency": "pandas"})

        try:
            csv_file = io.BytesIO(file_content)
            df = pd.read_csv(csv_file)

            if df.empty:
                logger.warning("CSV file is empty")
                return "CSV Data (0 rows, 0 columns)"

            # Convert DataFrame to readable text format
            text_parts = [f"CSV Data ({len(df)} rows, {len(df.columns)} columns)\n"]
            text_parts.append("Columns: " + ", ".join(str(col) for col in df.columns))
            text_parts.append("\n--- Data ---")

            # Convert to string representation
            text_parts.append(df.to_string(index=False))

            logger.info(f"Successfully extracted CSV data ({len(df)} rows, {len(df.columns)} columns)")
            return "\n".join(text_parts)

        except DocumentProcessingError:
            raise
        except Exception as e:
            log_exception(e, context="DocumentProcessor.extract_text_from_csv")
            raise DocumentProcessingError(
                f"Failed to process CSV: {str(e)}",
                details={"file_type": "CSV", "error": str(e)}
            )
    
    @staticmethod
    def extract_text_from_excel(file_content: bytes) -> str:
        """Extract text from Excel XLSX file."""
        if pd is None:
            error_msg = "pandas is required for Excel processing. Install with: pip install pandas openpyxl"
            logger.error(error_msg)
            raise DocumentProcessingError(error_msg, details={"file_type": "XLSX", "missing_dependency": "pandas, openpyxl"})

        try:
            excel_file = io.BytesIO(file_content)
            # Read all sheets
            excel_data = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')

            if not excel_data:
                logger.warning("Excel file has no sheets")
                return "Excel Data (0 sheets)"

            text_parts = []
            for sheet_name, df in excel_data.items():
                try:
                    text_parts.append(f"\n=== Sheet: {sheet_name} ===")
                    text_parts.append(f"({len(df)} rows, {len(df.columns)} columns)")
                    text_parts.append("Columns: " + ", ".join(str(col) for col in df.columns))
                    text_parts.append("\n--- Data ---")
                    text_parts.append(df.to_string(index=False))
                except Exception as e:
                    logger.warning(f"Failed to extract data from sheet '{sheet_name}': {e}")
                    continue

            logger.info(f"Successfully extracted Excel data ({len(excel_data)} sheets)")
            return "\n".join(text_parts)

        except DocumentProcessingError:
            raise
        except Exception as e:
            log_exception(e, context="DocumentProcessor.extract_text_from_excel")
            raise DocumentProcessingError(
                f"Failed to process Excel file: {str(e)}",
                details={"file_type": "XLSX", "error": str(e)}
            )
    
    @staticmethod
    def process_file(filename: str, file_content: bytes) -> str:
        """
        Process a file and extract text based on file extension.

        Args:
            filename: Name of the file
            file_content: Binary content of the file

        Returns:
            Extracted text content
        """
        try:
            if not filename:
                raise DocumentProcessingError("Filename is required", details={"filename": filename})

            if not file_content:
                raise DocumentProcessingError("File content is empty", details={"filename": filename})

            file_ext = Path(filename).suffix.lower()

            logger.info(f"Processing file: {filename} (type: {file_ext})")

            if file_ext == '.pdf':
                return DocumentProcessor.extract_text_from_pdf(file_content)
            elif file_ext in ['.docx', '.doc']:
                return DocumentProcessor.extract_text_from_docx(file_content)
            elif file_ext == '.csv':
                return DocumentProcessor.extract_text_from_csv(file_content)
            elif file_ext in ['.xlsx', '.xls']:
                return DocumentProcessor.extract_text_from_excel(file_content)
            elif file_ext == '.txt':
                try:
                    text = file_content.decode('utf-8')
                    logger.info(f"Successfully extracted text from TXT file ({len(text)} chars)")
                    return text
                except UnicodeDecodeError as e:
                    log_exception(e, context="DocumentProcessor.process_file (TXT)")
                    raise DocumentProcessingError(
                        f"Failed to decode text file: {str(e)}",
                        details={"filename": filename, "file_type": "TXT"}
                    )
            else:
                error_msg = f"Unsupported file format: {file_ext}. Supported formats: PDF, DOCX, CSV, XLSX, TXT"
                logger.error(error_msg)
                raise DocumentProcessingError(
                    error_msg,
                    details={"filename": filename, "file_ext": file_ext, "supported_formats": ["PDF", "DOCX", "CSV", "XLSX", "TXT"]}
                )

        except DocumentProcessingError:
            raise
        except Exception as e:
            log_exception(e, context="DocumentProcessor.process_file")
            raise DocumentProcessingError(
                f"Unexpected error processing file: {str(e)}",
                details={"filename": filename, "error": str(e)}
            )

