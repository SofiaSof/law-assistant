"""
Legal Assistant for FZ "O Reklame" (38-FZ)
Proverka teksta na sootvetstvie zakonu o reklame
"""

from law_data import (
    get_article,
    get_chapter,
    search_in_law,
    semantic_search,
    get_best_match,
    LAW_CONTENT
)
import re


def check_text(text: str) -> dict:
    """
    Proverka teksta na narusheniya FZ o reklame
    """
    result = {
        "checked_text": text[:200] + "..." if len(text) > 200 else text,
        "found_categories": [],
        "potential_issues": [],
        "related_articles": [],
        "recommendations": []
    }
    
    text_lower = text.lower()
    
    categories = {
        "alkogol": {
            "keywords": ["водка", "виски", "коньяк", "пиво", "шампанское", "алкоголь", "спирт", "wine", "beer", "whisky", "vodka", "brandy", "шампанское"],
            "article": "21",
            "name": "Alkogol"
        },
        "lekarstvo": {
            "keywords": ["лекарство", "таблетка", "аптека", "препарат", "бад", "витамин", "medicine", "pharmacy", "drug", "tablet", "капли", "мазь", "сироп"],
            "article": "24",
            "name": "Lekarstva"
        },
        "deti": {
            "keywords": ["дети", "ребенок", "малыш", "kids", "детский", "child", "children", "несовершеннолетние"],
            "article": "6",
            "name": "Deti"
        },
        "finansy": {
            "keywords": ["кредит", "вклад", "инвестиция", "банк", "займ", "микрозайм", "credit", "loan", "investment", "ставка", "percent", "деньги"],
            "article": "28",
            "name": "Finansy"
        },
        "tabak": {
            "keywords": ["сигареты", "сигара", "табак", "cigarette", "tobacco", "курение", "сигарет", "vape", "вейп"],
            "article": "7",
            "name": "Tabachnye izdeliya"
        },
        "crypto": {
            "keywords": ["криптовалюта", "биткоин", "crypto", "bitcoin", "торговля криптовалютой"],
            "article": "28",
            "name": "Kriptovalyuta"
        },
        "super_ceny": {
            "keywords": ["бесплатно", "gratis", "-50%", "-70%", "-90%", "-99%", "99%", "распродажа", "скидка", "скидки", "бесплатный", "бесплатная", "акция", "скидок"],
            "article": "5",
            "name": "Super ceny"
        },
        "obman": {
            "keywords": ["100%", "гарантия", "только сегодня", "успейте", "ограниченное предложение", "осталось"],
            "article": "5",
            "name": "Potencialny obman"
        }
    }
    
    found = set()
    
    for cat_id, cat_data in categories.items():
        for keyword in cat_data["keywords"]:
            if keyword.lower() in text_lower:
                found.add(cat_id)
                result["found_categories"].append({
                    "category": cat_id,
                    "name": cat_data["name"],
                    "keyword": keyword,
                    "article": cat_data["article"]
                })
                break
    
    if "alkogol" in found:
        result["potential_issues"].append("Reklama alkogolya - trebuetsya proverka Statya 21")
        art = get_article("21")
        if art:
            result["recommendations"].append({
                "article": "21",
                "title": art["title"],
                "text": art["content"]
            })
    
    if "lekarstvo" in found:
        result["potential_issues"].append("Reklama lekarstv - trebuetsya proverka Statya 24")
        art = get_article("24")
        if art:
            result["recommendations"].append({
                "article": "24",
                "title": art["title"],
                "text": art["content"]
            })
    
    if "deti" in found:
        if "alkogol" in found or "tabak" in found:
            result["potential_issues"].append("OBLADATELNO! Obrashchenie k detyam v reklame zapreshchennyh tovarov - Statya 6")
            art = get_article("6")
            if art:
                result["recommendations"].append({
                    "article": "6",
                    "title": art["title"],
                    "text": art["content"]
                })
    
    if "finansy" in found:
        result["potential_issues"].append("Reklama finansovyh uslug - proverka Statya 28")
        art = get_article("28")
        if art:
            result["recommendations"].append({
                "article": "28",
                "title": art["title"],
                "text": art["content"]
            })
        
        if "обман" in text_lower or "100%" in text_lower or "гарантия" in text_lower:
            result["potential_issues"].append("Podozritelnaya finansovaya reklama - garantii dohodnosti zapreshcheny")
    
    if "tabak" in found:
        result["potential_issues"].append("Reklama tabachnyh izdeliy - proverka Statya 7")
        art = get_article("7")
        if art:
            result["recommendations"].append({
                "article": "7",
                "title": art["title"],
                "text": art["content"]
            })
    
    if "obman" in found:
        result["potential_issues"].append("Potencialny obman v reklame - trebuetsya proverka Statya 5")
        art = get_article("5")
        if art:
            result["recommendations"].append({
                "article": "5",
                "title": art["title"],
                "text": art["content"]
            })
    
    return result


def check_text_simple(text: str) -> str:
    """Prostoy proverka teksta - vozvrashchaet tekstovyy otvet"""
    result = check_text(text)
    
    output = "\n" + "=" * 60 + "\n"
    output += "PROVERKA TEKSTA NA FZ O REKLAME\n"
    output += "=" * 60 + "\n\n"
    
    output += f"Proveryaemy tekst: {result['checked_text']}\n\n"
    
    if result["found_categories"]:
        output += "NAYDENNYE KATEGORII:\n"
        output += "-" * 40 + "\n"
        for cat in result["found_categories"]:
            output += f"  - {cat['name']} (klyuchevoe slovo: '{cat['keyword']}')\n"
        output += "\n"
    
    if result["potential_issues"]:
        output += "POTENTSIALNYE NARUSHENIYA:\n"
        output += "-" * 40 + "\n"
        for issue in result["potential_issues"]:
            output += f"  ! {issue}\n"
        output += "\n"
    else:
        output += "Narusheniy ne vyyavleno.\n\n"
    
    if result["recommendations"]:
        output += "REKOMENDATSII (STATYI FZ):\n"
        output += "-" * 40 + "\n"
        for rec in result["recommendations"]:
            output += f"\nStatya {rec['article']}: {rec['title']}\n"
            output += rec["text"][:400] + "...\n"
    
    return output


if __name__ == "__main__":
    import sys
    
    print("Proverka teksta na FZ o Reklame")
    print("-" * 40)
    
    test_texts = [
        "Kupite vodku po specialnoy tsene! Tolko segodnya skidka 50%!",
        "Lechite gripp lekarstvom NOVOGRAM!",
        "Besplatnye dengi v kredite! 100% garantiya!",
        "Krasivye deti s nashim tovarom!",
        "Sberbank predlagaet vklad pod 20% godovyh!"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. {text}")
        result = check_text(text)
        if result["potential_issues"]:
            for issue in result["potential_issues"]:
                print(f"   ! {issue}")
