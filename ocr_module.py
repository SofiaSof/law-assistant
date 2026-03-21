"""
OCR Module for Law Assistant
Modul analiziruet izobrazheniya dlya poiska narusheniy v reklame
"""

import os
import sys
from PIL import Image
import io


class OCRProcessor:
    def __init__(self):
        self.ocr_available = False
        self._check_ocr()
    
    def _check_ocr(self):
        """Proverit dostupnost OCR"""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self.ocr_available = True
            print("Tesseract OCR: OK")
            return
        except Exception:
            pass
        
        try:
            import easyocr
            print("Zagruzka EasyOCR modeley...")
            self.easyocr_reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)
            self.ocr_available = True
            print("EasyOCR: OK")
            return
        except Exception as e:
            print(f"EasyOCR ne dostupen: {e}")
        
        self.ocr_available = False
        print("OCR ne ustanovlen. Tekst ne budet raspoznan.")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Izвлечь текст iz izobrazheniya"""
        if not os.path.exists(image_path):
            return f"Fayl ne najden: {image_path}"
        
        try:
            if not self.ocr_available:
                return self._get_install_instructions()
            
            try:
                import pytesseract
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image, lang='rus+eng', config='--psm 6')
                return text.strip()
            except Exception:
                pass
            
            try:
                import easyocr
                if not hasattr(self, 'easyocr_reader'):
                    self.easyocr_reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)
                
                results = self.easyocr_reader.readtext(image_path)
                texts = [text for (bbox, text, confidence) in results if confidence > 0.3]
                return "\n".join(texts) if texts else "[Tekst ne najden]"
            except Exception as e:
                return f"Oshibka OCR: {str(e)}"
            
        except Exception as e:
            return f"Oshibka: {str(e)}"
    
    def _get_install_instructions(self) -> str:
        """Poluchit instrukcii po ustanovke OCR"""
        return """
[OCR ne ustanovlen]

Dlya raspoznavaniya teksta ustanovite Tesseract OCR:

1. Skachayte: https://github.com/UB-Mannheim/tesseract/wiki
2. Ustanovite s russkim yazykovym paketom
3. Dobavte v sistemnyy PATH

Ili v Windows:
  winget install Google.TesseractOCR

Posle ustanovki perezapustite programmu.
"""
    
    def analyze_advertisement(self, image_path: str) -> dict:
        """Analiz reklamy na izobrazhenii"""
        text = self.extract_text_from_image(image_path)
        
        result = {
            "recognized_text": text,
            "found_keywords": [],
            "potential_issues": [],
            "recommendations": []
        }
        
        text_lower = text.lower()
        
        categories = {
            "alkogol": ["водка", "виски", "коньяк", "пиво", "шампанское", "алкоголь", "спирт", "spirto", "whisky", "vodka", "brandy", "wine", "beer", "champagne"],
            "lekarstvo": ["лекарство", "таблетка", "аптека", "medicine", "препарат", "бад", "витамин", "tablet", "pharmacy", "drug"],
            "deti": ["дети", "ребенок", "малыш", "kids", "nesovershennoletnie", "детский", "child", "children"],
            "finansy": ["кредит", "вклад", "инвестиция", "банк", "займ", "микрозайм", "ставка", "percent", "credit", "loan", "investment"],
            "tabak": ["сигареты", "сигара", "табак", "cigarette", "tobacco", "smoking", "курение"],
            "super_ceny": ["бесплатно", "gratis", "-50%", "-70%", "-90%", "скидка 70%", "распродажа"]
        }
        
        found = set()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found.add(category)
                    result["found_keywords"].append((category, keyword))
                    break
        
        if "alkogol" in found:
            result["potential_issues"].append("Reklama alkogolya (Statya 21)")
        
        if "lekarstvo" in found:
            result["potential_issues"].append("Reklama lekarstv (Statya 24)")
        
        if "deti" in found and ("alkogol" in found or "tabak" in found):
            result["potential_issues"].append("Obrashchenie k detyam! (Statya 6)")
        
        if "finansy" in found and "super_ceny" in found:
            result["potential_issues"].append("Podozritelnaya finansovaya reklama (Statya 28)")
        
        return result


def analyze_image(image_path: str) -> dict:
    """Glavnaya funktsiya"""
    ocr = OCRProcessor()
    return ocr.analyze_advertisement(image_path)


def extract_text(image_path: str) -> str:
    """Izвleчь tekst"""
    ocr = OCRProcessor()
    return ocr.extract_text_from_image(image_path)


if __name__ == "__main__":
    print("OCR Module - Pravila reklamy")
    print("-" * 40)
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Analiz: {image_path}")
        
        ocr = OCRProcessor()
        result = ocr.analyze_advertisement(image_path)
        
        print("\nTekst:", result["recognized_text"][:500])
        print("\nKategorii:", result["found_keywords"])
        print("Problemy:", result["potential_issues"])
