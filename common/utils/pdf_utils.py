import io
from typing import Optional

import fitz  # PyMuPDF
from PIL import Image


class PDFUtils:
    """PDF 관련 유틸리티"""

    @staticmethod
    def get_first_page_thumbnail(
        file_data: bytes, max_width: int = 800
    ) -> Optional[io.BytesIO]:
        """
        PDF 파일의 첫 페이지를 썸네일 이미지로 변환합니다.

        Args:
            file_data: PDF 파일 데이터 (bytes)
            max_width: 썸네일 최대 너비 (기본값: 800px)

        Returns:
            io.BytesIO: 썸네일 이미지 데이터 (PNG 형식). 실패 시 None
        """
        try:
            # PDF 문서 열기
            pdf_document = fitz.open(stream=file_data, filetype="pdf")

            if pdf_document.page_count == 0:
                pdf_document.close()
                return None

            # 첫 페이지 가져오기
            first_page = pdf_document[0]

            # 페이지를 이미지로 변환 (zoom을 사용하여 해상도 조정)
            zoom = 2.0  # 해상도 배율 (2.0 = 144 DPI)
            mat = fitz.Matrix(zoom, zoom)
            pix = first_page.get_pixmap(matrix=mat)

            # PIL Image로 변환
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # 이미지 리사이징 (가로 비율 유지)
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # BytesIO로 변환
            thumbnail_io = io.BytesIO()
            img.save(thumbnail_io, format="PNG", optimize=True)
            thumbnail_io.seek(0)

            pdf_document.close()

            return thumbnail_io

        except Exception as e:
            print(f"Failed to generate PDF thumbnail: {str(e)}")
            return None

    @staticmethod
    def get_page_count(file_data: bytes) -> int:
        """
        PDF 파일의 전체 페이지 수를 반환합니다.

        Args:
            file_data: PDF 파일 데이터 (bytes)

        Returns:
            int: 페이지 수. 실패 시 0
        """
        try:
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            page_count = pdf_document.page_count
            pdf_document.close()
            return page_count

        except Exception as e:
            print(f"Failed to get PDF page count: {str(e)}")
            return 0

    @staticmethod
    def is_pdf_file(filename: str) -> bool:
        """
        파일명이 PDF 확장자인지 확인합니다.

        Args:
            filename: 파일명

        Returns:
            bool: PDF 파일 여부
        """
        return filename.lower().endswith(".pdf")
