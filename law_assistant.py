"""
Legal Assistant for FZ "O Reklame" (38-FZ)
Interactive mode for questions about the law and text checking
"""

from law_data import (
    get_article,
    get_chapter,
    search_in_law,
    semantic_search,
    get_best_match,
    LAW_CONTENT
)
from check_text import check_text_simple, check_text
import re
import sys


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
    
    best_match = get_best_match(question)
    if best_match and best_match["score"] >= 3:
        return format_semantic_result(best_match)
    
    return "Ne udalos opredelit temu. Ispolzuyte /check <tekst> dlya proverki teksta na FZ."


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


def format_semantic_result(result: dict) -> str:
    matched_info = ""
    if result.get("matched"):
        matched_info = f"\nNaidenno po: {', '.join(result['matched'][:5])}"
    
    return f"""
SEMANTICHESKIY POISK:

=== STATYA {result['article']}: {result['title']} ==={matched_info}

{result['content']}

---
Istochnik: FZ 38-FZ "O reklame"
"""


def handle_check_command(text: str) -> str:
    """Proverka teksta na sootvetstvie FZ"""
    return check_text_simple(text)


def answer_question(question: str) -> str:
    return parse_question(question)


def main():
    if len(sys.argv) > 1:
        first_arg = sys.argv[1].lower()
        
        if first_arg == "/check":
            text = " ".join(sys.argv[2:])
            if text:
                return handle_check_command(text)
            return "Ukazhite tekst dlya proverki: /check <tekst>"
        
        if first_arg == "/help":
            return get_help()
        
        if first_arg.startswith("/"):
            return f"Neponyatnaya komanda: {first_arg}. Ispolzuyte /help"
        
        answer = answer_question(" ".join(sys.argv[1:]))
        print(answer)
        return
    
    print("=" * 60)
    print("Legal Assistant - FZ 'O Reklame' (38-FZ)")
    print("=" * 60)
    print()
    print("Dostupnye komandy:")
    print("  /check <tekst>     - Proverka teksta na narusheniya FZ")
    print("  statya N           - Tekst statyi (primer: statya 5)")
    print("  glava N            - Struktura glavy (primer: glava 3)")
    print("  shtrafy, alkogol   - Temu zakona")
    print("  /help              - Spisok komand")
    print()
    print("Vvedite /check <tekst> dlya proverki reklama na FZ:")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nVy: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["vyhod", "exit", "quit"]:
                print("Dosvidaniya!")
                break
            
            if user_input.lower() == "/help":
                print(get_help())
                continue
            
            if user_input.startswith("/check "):
                text = user_input[7:]
                print(handle_check_command(text))
            elif user_input.startswith("/"):
                print(f"Neponyatnaya komanda. Ispolzuyte /help")
            else:
                print(parse_question(user_input))
            
        except KeyboardInterrupt:
            print("\n\nDosvidaniya!")
            break


def get_help() -> str:
    return """
=== POMOSCH ===

Komandy:
  /check <tekst>  - Proverit tekst na narusheniya FZ
                    Primer: /check Kupite vodku so skidkoy!

  statya N        - Pokazat tekst statyi
                    Primer: statya 21

  glava N          - Pokazat strukturu glavy
                    Primer: glava 3

Temy (vvedite slovo):
  shtrafy          - Shtrafy za narusheniya
  alkogol          - Pravila reklamy alkogolya
  internet         - Reklama v internete
  finans           - Reklama finansovyh uslug
  lekarstv         - Reklama lekarstv
  deti             - Zashchita nesovershennoletnih

Primer proverki teksta:
  /check Besplatnye lekarstva tolko u nas!
"""


if __name__ == "__main__":
    main()
