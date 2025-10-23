from common.utils.pdf_utils import PDFUtils


class TestExtractPDFTexts:
    def test_extract_pdf_texts(self):
        # PDF URL에서 텍스트 추출
        url = "https://talktor.file.wasso.kr/materials/cc609f5f-18e6-4d70-b037-4123ed0d556f/3_memory_virtualization.pdf"
        text = PDFUtils.extract_text_from_url(url)

        # 텍스트가 정상적으로 추출되었는지 확인
        assert text is not None
        assert len(text) > 0

        # 파일로 저장
        output_file = "llm/tests/extracted_text.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"추출된 텍스트 길이: {len(text)}")
        print(f"텍스트 파일 저장 완료: {output_file}")

        # 이미지 추출
        images_output_dir = "llm/tests/extracted_images"
        extracted_images = PDFUtils.extract_images_from_url(url, images_output_dir)

        print(f"추출된 이미지 개수: {len(extracted_images)}")
        for page_num, image_path in extracted_images:
            print(f"  페이지 {page_num}: {image_path}")
