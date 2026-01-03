class BaseExtractor:
    def extract(self, pdf_path: str) -> dict:
        raise NotImplementedError("Debe implementar extract()")