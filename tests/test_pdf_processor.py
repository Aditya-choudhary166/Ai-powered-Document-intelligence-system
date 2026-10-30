from modules.pdf_processor import extract_pdf

def test_rejects_non_pdf():
    try:
        extract_pdf(b"not a pdf")
    except ValueError:
        assert True
    else:
        assert False
