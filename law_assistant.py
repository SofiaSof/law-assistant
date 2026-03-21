"""
Legal Assistant for Russian Federal Law "On Advertising" (38-FZ)
Interactive mode for answering questions about the law
"""

from law_data import (
    get_article, 
    get_chapter, 
    search_in_law, 
    get_law_structure,
    semantic_search,
    get_best_match,
    LAW_CONTENT
)
from ocr_module import OCRProcessor, analyze_image, extract_text
import re
import sys
import os


def parse_question(question: str) -> str:
    question = question.lower()
    
    if "glava" in question:
        match = re.search(r'glava\s*(\d+)', question)
        if match:
            chapter_num = match.group(1)
            chapter_data = get_chapter(chapter_num)
            if chapter_data:
                articles = [get_article(a) for a in chapter_data.get("articles", [])]
                return format_chapter_response(chapter_num, chapter_data, articles)
    
    if "statya" in question or re.search(r'st\.\s*\d+|statyey\s*\d+', question):
        match = re.search(r'(?:statya|st\.|statyey)\s*(\d+(?:\.\d+)?)', question)
        if match:
            art_num = match.group(1)
            article_data = get_article(art_num)
            if article_data:
                return format_article_response(art_num, article_data)
    
    keywords_map = {
        "shtraf": "38",
        "otvetstvennost": "38",
        "alkogol": "21",
        "internet": "18.1",
        "televizor": "14",
        "teleprogramm": "14",
        "naruzhn": "19",
        "sms": "18",
        "telefon": "18",
        "finans": "28",
        "lekarstv": "24",
        "meditsin": "24",
        "nesovershennoletn": "6",
        "deti": "6",
        "fas": "33",
        "antimonopoln": "33",
        "sponsor": "10",
        "sotsialn": "10",
    }
    
    for keyword, art_num in keywords_map.items():
        if keyword in question:
            article_data = get_article(art_num)
            if article_data:
                return format_article_response(art_num, article_data)
    
    if "chto takoe" in question or "opredelenie" in question:
        results = search_in_law("reklama ponyatie")
        if results:
            return format_search_results(results, "opredeleniyu reklamy")
    
    if "zapret" in question or "nelzya" in question:
        article_data = get_article("5")
        if article_data:
            return format_article_response("5", article_data)
    
    best_match = get_best_match(question)
    if best_match and best_match["score"] >= 3:
        return format_semantic_result(best_match)
    
    return "Ne udalos opredelit temu voprosa. Poprobujte utochnit zapros ili ispolzuyte nomer statyi (naprimer: statya 15)."


def format_semantic_result(result: dict) -> str:
    matched_info = ""
    if result.get("matched"):
        matched_info = f"\nNaidenno po klyuchevym slovam: {', '.join(result['matched'][:5])}"
    
    return f"""
SEMANTICHESKIY POISK NAYDEN:

=== STATYA {result['article']}: {result['title']} ==={matched_info}

{result['content']}

---
Istochnik: FZ 38-FZ "O reklame"
"""


def format_article_response(art_num: str, article_data: dict) -> str:
    return f"""
=== STATYA {art_num}: {article_data['title']} ===

{article_data['content']}

---
Istochnik: FZ 38-FZ "O reklame"
"""


def format_chapter_response(ch_num: str, chapter_data: dict, articles: list) -> str:
    articles_text = []
    for art in articles:
        if art:
            articles_text.append(f"  - Statya {art['article']}: {art['title']}")
    
    return f"""
=== GLAVA {ch_num}: {chapter_data['name']} ===

Soderzhanie:
{chr(10).join(articles_text)}

---
Istochnik: FZ 38-FZ "O reklame"
"""


def format_search_results(results: list, topic: str) -> str:
    if not results:
        return f"Po teme '{topic}' informatsiya ne najdena v lokalnoy baze."
    
    text = f"\nRezultaty poiska po teme: {topic}\n\n"
    
    for i, result in enumerate(results[:3], 1):
        text += f"{i}. Statya {result['article']}: {result['title']}\n"
        text += f"   {result['content'][:300]}...\n\n"
    
    text += "---"
    return text


def answer_question(question: str) -> str:
    answer = parse_question(question)
    return answer


def handle_image_command(args: list) -> str:
    """Obrabotka komandy analiz izobrazheniya"""
    if not args:
        return "Ukazhite put k izobrazheniyu: /image <put_k_faylu>"
    
    image_path = " ".join(args)
    
    if not os.path.exists(image_path):
        return f"Fayl ne najden: {image_path}"
    
    result = analyze_image(image_path)
    
    output = "\n" + "=" * 60 + "\n"
    output += "ANALIZ IZOBRAZHENIYA (OCR + PROVERKA NA NARUSHENIYA)\n"
    output += "=" * 60 + "\n\n"
    
    output += "Raspoznannyy tekst:\n"
    output += "-" * 40 + "\n"
    output += result["recognized_text"] + "\n\n"
    
    if result["found_keywords"]:
        output += "Naydennye kategorii:\n"
        output += "-" * 40 + "\n"
        for cat, kw in result["found_keywords"]:
            output += f"  - {cat}: {kw}\n"
        output += "\n"
    
    if result["potential_issues"]:
        output += "POTENTSIALNYE NARUSHENIYA:\n"
        output += "-" * 40 + "\n"
        for issue in result["potential_issues"]:
            output += f"  ! {issue}\n"
        
        for issue in result["potential_issues"]:
            if "statya" in issue.lower():
                match = re.search(r'statya\s*(\d+(?:\.\d+)?)', issue.lower())
                if match:
                    art_data = get_article(match.group(1))
                    if art_data:
                        output += f"\n--- Rekomendatsiya (Statya {match.group(1)}) ---\n"
                        output += art_data["content"][:500] + "...\n"
    else:
        output += "Narusheniy ne vyyavleno.\n"
    
    return output


def main():
    if len(sys.argv) > 1:
        first_arg = sys.argv[1].lower()
        
        if first_arg == "/image" or first_arg == "/img":
            result = handle_image_command(sys.argv[2:])
            print(result)
            return
        
        question = " ".join(sys.argv[1:])
        answer = answer_question(question)
        print(answer)
        return
    
    print("=" * 60)
    print("Legal Assistant - FZ 'O reklame' (38-FZ)")
    print("=" * 60)
    print()
    print("Dostupnye komandy:")
    print("  statya N        - statya zakona (naprimer: statya 5)")
    print("  glava N         - struktura glavy (naprimer: glava 3)")
    print("  shtrafy         - otvetstvennost i shtrafy")
    print("  alkogol         - reklama alkogolya")
    print("  internet        - reklama v internete")
    print("  finans          - reklama finansovyh uslug")
    print("  lekarstv        - reklama lekarstv")
    print("  /image <fayl>   - analiz izobrazheniya (OCR)")
    print("  pomoshch        - spisok dostupnyh statey")
    print("  vihod           - vyhod iz programmy")
    print()
    print("Vvedite vash vopros:")
    print("-" * 60)
    
    while True:
        try:
            question = input("\nVy: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ["vyhod", "exit", "quit"]:
                print("Dosvidaniya!")
                break
            
            if question.lower() == "pomosch":
                print("\nDostupnye temy:")
                print("  statya 5      - Obshchie trebovaniya k reklame")
                print("  statya 14     - Reklama v televidenii")
                print("  statya 18     - Reklama po SMS i email")
                print("  statya 18.1   - Reklama v internete")
                print("  statya 19     - Naruzhnaya reklama")
                print("  statya 21     - Reklama alkogolya")
                print("  statya 24     - Reklama lekarstv")
                print("  statya 28     - Reklama finansovyh uslug")
                print("  statya 33     - Polnomochiya FAS")
                print("  statya 38     - Shtrafy i otvetstvennost")
                print("  glava 3       - Vse statyi glavy 3")
                print()
                print("Analiz izobrazheniy:")
                print("  /image put/k/faylu.png - raspoznat tekst i proverit na narusheniya")
                continue
            
            if question.startswith("/image ") or question.startswith("/img "):
                parts = question.split(" ", 1)
                image_result = handle_image_command([parts[1]])
                print(image_result)
                continue
            
            print()
            answer = answer_question(question)
            print(answer)
            
        except KeyboardInterrupt:
            print("\n\nDosvidaniya!")
            break


if __name__ == "__main__":
    main()
