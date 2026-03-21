"""
OCR and Image Analysis Module for Law Assistant
Ispolzuet OCR i opisanie izobrazheniy cherez besplatnye API
"""

import os
import sys
import base64
import json
import requests
from PIL import Image
import io


class VisionAnalyzer:
    def __init__(self):
        self.ocr_available = False
        self.tesseract_path = None
        self.tessdata_dir = None
        self._find_tesseract()
    
    def _find_tesseract(self):
        """Nayti Tesseract"""
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR",
            r"C:\Tesseract",
        ]
        
        for base_path in possible_paths:
            tesseract_exe = os.path.join(base_path, "tesseract.exe")
            if os.path.exists(tesseract_exe):
                self.tesseract_path = tesseract_exe
                self.tessdata_dir = os.path.join(base_path, "tessdata")
                
                tessdata_project = os.path.join(os.path.dirname(__file__), "tessdata")
                if os.path.exists(os.path.join(tessdata_project, "rus.traineddata")):
                    self.tessdata_dir = tessdata_project
                
                os.environ["PATH"] = base_path + os.pathsep + os.environ.get("PATH", "")
                os.environ["TESSDATA_PREFIX"] = self.tessdata_dir
                
                self.ocr_available = True
                print(f"Tesseract found: {tesseract_exe}")
                return
        
        print("Tesseract ne najden.")
    
    def extract_text_tesseract(self, image_path: str) -> str:
        """OCR s Tesseract"""
        if not self.ocr_available:
            return "[Tesseract ne dostupen]"
        
        try:
            import subprocess
            
            cmd = [
                self.tesseract_path,
                image_path.replace("\\", "/"),
                "stdout",
                "--tessdata-dir", self.tessdata_dir.replace("\\", "/"),
                "--oem", "3",
                "--psm", "6",
                "-l", "rus+eng"
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
            return ""
        except Exception as e:
            return f"[OCR error: {str(e)}]"
    
    def describe_with_free_api(self, image_path: str) -> str:
        """Opisanie cherez besplatnyy API (ocr.space)"""
        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            
            payload = {
                "language": "rus+eng"
            }
            
            files = {"filename": ("image.png", img_bytes, "image/png")}
            
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files=files,
                data=payload,
                headers={"apikey": "helloworld"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "ParsedResults" in data:
                    texts = []
                    for r in data["ParsedResults"]:
                        if "ParsedText" in r and r["ParsedText"].strip():
                            texts.append(r["ParsedText"].strip())
                    if texts:
                        return "\n".join(texts)
            
            return ""
        except Exception as e:
            return ""
    
    def analyze_advertisement(self, image_path: str) -> dict:
        """Polnyy analiz reklamy"""
        text = self.extract_text_tesseract(image_path)
        if not text or len(text) < 20:
            text = self.describe_with_free_api(image_path)
        
        result = {
            "recognized_text": text,
            "found_categories": [],
            "potential_issues": [],
            "related_articles": []
        }
        
        if not text:
            result["potential_issues"].append("Tekst ne raspoznan. Poprobuyte izobrazhenie luchshego kachestva.")
            return result
        
        text_lower = text.lower()
        
        categories = {
            "alkogol": ["водка", "виски", "коньяк", "пиво", "шампанское", "алкоголь", "спирт", "wine", "beer", "whisky"],
            "lekarstvo": ["лекарство", "таблетка", "аптека", "medicine", "препарат", "бад", "витамин", "pharmacy"],
            "deti": ["дети", "ребенок", "малыш", "kids", "детский"],
            "finansy": ["кредит", "вклад", "инвестиция", "банк", "займ", "микрозайм", "credit", "loan"],
            "tabak": ["сигареты", "сигара", "табак", "cigarette", "tobacco", "курение"],
            "super_ceny": ["бесплатно", "gratis", "-50%", "-70%", "скидка", "распродажа"]
        }
        
        found = set()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found.add(category)
                    result["found_categories"].append(category)
                    break
        
        if "alkogol" in found:
            result["potential_issues"].append("Reklama alkogolya - Statya 21 FZ")
            result["related_articles"].append("21: Reklama alkogolnoy produktsii")
        
        if "lekarstvo" in found:
            result["potential_issues"].append("Reklama lekarstv - Statya 24 FZ")
            result["related_articles"].append("24: Reklama lekarstvennyh sredstv")
        
        if "deti" in found and ("alkogol" in found or "tabak" in found):
            result["potential_issues"].append("Obrashchenie k detyam! - Statya 6 FZ")
            result["related_articles"].append("6: Zashchita nesovershennoletnih")
        
        if "finansy" in found and "super_ceny" in found:
            result["potential_issues"].append("Podozritelnaya finansovaya reklama - Statya 28 FZ")
            result["related_articles"].append("28: Reklama finansovyh uslug")
        
        return result


def analyze_image(image_path: str) -> dict:
    """Glavnaya funktsiya"""
    analyzer = VisionAnalyzer()
    return analyzer.analyze_advertisement(image_path)


if __name__ == "__main__":
    print("OCR + Vision Analyzer")
    print("-" * 40)
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Analiz: {image_path}")
        
        analyzer = VisionAnalyzer()
        result = analyzer.analyze_advertisement(image_path)
        
        print("\n=== RESULT ===")
        print(f"Text: {result['recognized_text'][:200] if result['recognized_text'] else 'NE NAJDEN'}")
        print(f"Categories: {result['found_categories']}")
        print(f"Issues: {result['potential_issues']}")
        print(f"Articles: {result['related_articles']}")
