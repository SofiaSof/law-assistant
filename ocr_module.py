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
        self.tesseract_path = None
        self.tessdata_dir = None
        self._find_tesseract()
    
    def _find_tesseract(self):
        """Nayti Tesseract na sisteme"""
        import os
        
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR",
            r"C:\Tesseract",
            r"C:\Program Files (x86)\Tesseract-OCR",
        ]
        
        for base_path in possible_paths:
            tesseract_exe = os.path.join(base_path, "tesseract.exe")
            if os.path.exists(tesseract_exe):
                self.tesseract_path = tesseract_exe
                self.tesseract_dir = base_path
                
                self.tessdata_dir = os.path.join(base_path, "tessdata")
                
                tessdata_project = os.path.join(os.path.dirname(__file__), "tessdata")
                if os.path.exists(os.path.join(tessdata_project, "rus.traineddata")):
                    self.tessdata_dir = tessdata_project
                
                os.environ["PATH"] = base_path + os.pathsep + os.environ.get("PATH", "")
                os.environ["TESSDATA_PREFIX"] = self.tessdata_dir
                
                self.ocr_available = True
                print(f"Tesseract found: {tesseract_exe}")
                return
        
        print("Tesseract ne najden. Skachayte: https://github.com/UB-Mannheim/tesseract/releases")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Izвлечь текст iz izobrazheniya"""
        if not os.path.exists(image_path):
            return f"Fayl ne najden: {image_path}"
        
        try:
            if not self.tesseract_path:
                return self._get_install_instructions()
            
            import subprocess
            
            tessdata_dir = self.tessdata_dir.replace("\\", "/") if self.tessdata_dir else ""
            
            cmd = [
                self.tesseract_path,
                image_path.replace("\\", "/"),
                "stdout",
                "--tessdata-dir", tessdata_dir,
                "--oem", "3",
                "--psm", "6",
                "-l", "rus+eng"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ""
                return f"Oshibka Tesseract: {error_msg}"
            
        except Exception as e:
            return f"Oshibka OCR: {str(e)}"
    
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
