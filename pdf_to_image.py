from pdf2image import convert_from_path

class PDFConverter:
    def __init__(self,):
        self.pdf_path = None
        self.image = None
    
    def pdf_to_jpg(self, pdf):
        self.pdf_path = pdf
        self.image = convert_from_path(self.pdf_path, fmt = 'jpeg', dpi=300)  # Apenas a primeira página

        return self.image

