import io
import os
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
import requests
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

    @staticmethod
    def extract_text_from_bytes(file_data: bytes) -> str:
        """
        PDF 파일 데이터에서 모든 텍스트를 추출합니다.

        Args:
            file_data: PDF 파일 데이터 (bytes)

        Returns:
            str: 추출된 텍스트. 실패 시 빈 문자열
        """
        try:
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            text = ""

            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                text += f"====={page_num + 1}=====\n{page_text}\n"

            pdf_document.close()
            return text.strip()

        except Exception as e:
            print(f"Failed to extract text from PDF: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_url(url: str, timeout: int = 30) -> str:
        """
        URL에서 PDF를 다운로드하고 텍스트를 추출합니다.

        Args:
            url: PDF 파일 URL
            timeout: 다운로드 타임아웃 (초)

        Returns:
            str: 추출된 텍스트. 실패 시 빈 문자열
        """
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            return PDFUtils.extract_text_from_bytes(response.content)

        except Exception as e:
            print(f"Failed to download or extract text from PDF URL: {str(e)}")
            return ""

    @staticmethod
    def extract_images_from_bytes(
        file_data: bytes, output_dir: str
    ) -> List[Tuple[int, str]]:
        """
        PDF 파일 데이터에서 모든 이미지를 추출하여 파일로 저장합니다.

        Args:
            file_data: PDF 파일 데이터 (bytes)
            output_dir: 이미지를 저장할 디렉토리 경로

        Returns:
            List[Tuple[int, str]]: [(페이지 번호, 이미지 파일 경로), ...] 리스트. 실패 시 빈 리스트
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)

            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            extracted_images = []

            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                image_list = page.get_images(full=True)

                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]

                    # 이미지 추출
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # 이미지 파일명 생성
                    image_filename = (
                        f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                    )
                    image_path = os.path.join(output_dir, image_filename)

                    # 이미지 저장
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    extracted_images.append((page_num + 1, image_path))

            pdf_document.close()
            return extracted_images

        except Exception as e:
            print(f"Failed to extract images from PDF: {str(e)}")
            return []

    @staticmethod
    def extract_images_from_url(
        url: str, output_dir: str, timeout: int = 30
    ) -> List[Tuple[int, str]]:
        """
        URL에서 PDF를 다운로드하고 모든 이미지를 추출하여 파일로 저장합니다.

        Args:
            url: PDF 파일 URL
            output_dir: 이미지를 저장할 디렉토리 경로
            timeout: 다운로드 타임아웃 (초)

        Returns:
            List[Tuple[int, str]]: [(페이지 번호, 이미지 파일 경로), ...] 리스트. 실패 시 빈 리스트
        """
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            return PDFUtils.extract_images_from_bytes(response.content, output_dir)

        except Exception as e:
            print(f"Failed to download or extract images from PDF URL: {str(e)}")
            return []
