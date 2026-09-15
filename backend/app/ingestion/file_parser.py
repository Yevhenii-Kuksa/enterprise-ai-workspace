from dataclasses import dataclass
from pathlib import Path

from app.ingestion.parsing import (
    ParsedDocument,
    SupportedDocumentType,
    parse_docx_document,
    parse_pdf_document,
    parse_txt_document,
)

DOCX_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "wordprocessingml.document"
)

SUPPORTED_MIME_TYPES: dict[SupportedDocumentType, str] = {
    SupportedDocumentType.TXT: "text/plain",
    SupportedDocumentType.PDF: "application/pdf",
    SupportedDocumentType.DOCX: DOCX_MIME_TYPE,
}

SUPPORTED_EXTENSIONS: dict[str, SupportedDocumentType] = {
    ".txt": SupportedDocumentType.TXT,
    ".pdf": SupportedDocumentType.PDF,
    ".docx": SupportedDocumentType.DOCX,
}


@dataclass(frozen=True, slots=True)
class FileParseRequest:
    filename: str
    content: bytes
    mime_type: str | None = None


def resolve_document_type(
    filename: str,
) -> SupportedDocumentType:
    normalized_filename = filename.strip()

    if not normalized_filename:
        raise ValueError("Filename must not be empty.")

    extension = Path(normalized_filename).suffix.lower()

    try:
        return SUPPORTED_EXTENSIONS[extension]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported document extension: {extension or '<none>'}."
        ) from exc


def validate_mime_type(
    document_type: SupportedDocumentType,
    mime_type: str | None,
) -> str:
    expected_mime_type = SUPPORTED_MIME_TYPES[document_type]

    if mime_type is None:
        return expected_mime_type

    normalized_mime_type = mime_type.strip().lower()

    if not normalized_mime_type:
        raise ValueError("MIME type must not be empty.")

    if normalized_mime_type != expected_mime_type:
        raise ValueError(
            "MIME type does not match document extension. "
            f"Expected {expected_mime_type}, "
            f"received {normalized_mime_type}."
        )

    return expected_mime_type


def parse_document_file(
    request: FileParseRequest,
) -> ParsedDocument:
    if not request.content:
        raise ValueError("Document content must not be empty.")

    document_type = resolve_document_type(
        request.filename,
    )

    validate_mime_type(
        document_type,
        request.mime_type,
    )

    if document_type is SupportedDocumentType.TXT:
        return parse_txt_document(request.content)

    if document_type is SupportedDocumentType.PDF:
        return parse_pdf_document(request.content)

    if document_type is SupportedDocumentType.DOCX:
        return parse_docx_document(request.content)

    raise RuntimeError(
        f"No parser registered for document type: {document_type}."
    )