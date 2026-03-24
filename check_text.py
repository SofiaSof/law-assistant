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
        "recommendations": [],
        "fix_recommendations": []
    }
    
    text_lower = text.lower()
    
    categories = {
        "alkogol": {
            "keywords": ["водк", "виски", "коньяк", "пив", "шампанск", "алкогол", "спирт", "wine", "beer", "whisky", "vodka", "brandy", "сидр", "медов", "настойк", "вин", "текил", "ром", "ликёр", "бренди", "абсент"],
            "article": "21",
            "name": "Alkogol"
        },
        "lekarstvo": {
            "keywords": ["лекарств", "таблетк", "аптек", "препарат", "бад", "витамин", "medicine", "pharmacy", "drug", "tablet", "капл", "мазь", "сироп", "микстур", "инъекц", "укол"],
            "article": "24",
            "name": "Lekarstva"
        },
        "deti": {
            "keywords": ["детям", "ребенку", "малышу", "несовершеннолетн", "молодеж", "молодёж", "teenager", "подросток", "от 14", "от 12", "от 10", "до 18", "малолетн", "твой", "твоя", "твое", "ты ", " тебе", " для вас"],
            "article": "6",
            "name": "Deti"
        },
        "finansy": {
            "keywords": ["кредит", "вклад", "инвестиция", "банк", "займ", "микрозайм", "credit", "loan", "investment", "ставка", "percent", "деньги", "депозит", "накоплен", "домклик", "сбербанк", "ипотек", "карту", "карта", "кешбэк", "кешбек", "счет", "платеж"],
            "article": "28",
            "name": "Finansy"
        },
        "nedvizhimost": {
            "keywords": ["жк", "жилой комплекс", "квартир", "застройщик", "новостройк", "строительство", "дом", "жилье", "апартамент", "квадратный метр", "м2", "кв.м", "сдача", "дольщик", "долевое строительство", "отзывы", "отзыв"],
            "article": "28",
            "name": "Nedvizhimost"
        },
        "tabak": {
            "keywords": ["сигареты", "сигара", "табак", "cigarette", "tobacco", "курение", "сигарет", "vape", "вейп"],
            "article": "7",
            "name": "Tabachnye izdeliya"
        },
        "energetik": {
            "keywords": ["энергетик", "энергетические напитки", "энергетик", "energy drink", "tonic"],
            "article": "7",
            "name": "Energeticheskie napitki"
        },
        "crypto": {
            "keywords": ["криптовалюта", "биткоин", "crypto", "bitcoin", "торговля криптовалютой"],
            "article": "28",
            "name": "Kriptovalyuta"
        },
        "super_ceny": {
            "keywords": ["бесплатно", "gratis", "-50%", "-70%", "-90%", "-99%", "99%", "распродажа", "скидка", "скидки", "скидкой", "бесплатный", "бесплатная", "акция", "скидок", "подарок", "подарки", "подарки", "подарочный", "бесплатные", "скидочн", "скидочн", "кешбэк", "кешбек", "кэшбэк", "кэшбек", "cashback", "бонус", "бонусы"],
            "article": "5",
            "name": "Super ceny i podarki"
        },
        "obman": {
            "keywords": ["100%", "гарантия", "только сегодня", "успейте", "ограниченное предложение", "осталось"],
            "article": "5",
            "name": "Potencialny obman"
        },
        "inozemny_yazyk": {
            "keywords": ["holland", "park", "premium", "luxury", "family", "city", "home", "club", "view", "green", "city", "vip", "business", "elite", "comfort", "design", "room", "studio", "flat", "apartment", "house", "villa", "real estate", "development", "complex", "residential", "living", "loft", "penthouse", "suite", "space", "life", "park", "green", "water", "sky", "sun", "sea", "ocean", "river", "lake", "forest", "hill", "hill", "avenue", "boulevard", "plaza", "square", "territory", "terrace", "balcony", "window", "panorama", "view", "renovation", "smart", "climate", "auto", "control", "system", "security", "video", "intercom", "internet", "wi-fi", "fiber", "optic", "parking", "garage", "basketball", "football", "gym", "fitness", "spa", "sauna", "pool", "children", "kids", "playground", "school", "kindergarten", "shop", "mall", "center", "hypermarket", "supermarket", "hospital", "clinic", "pharmacy", "metro", "transport", "highway", "road", "center", "downtown", "outskirts", "zone", "area", "quarter", "sector", "block", "street", "lane", "road", "avenue", "drive", "way", "place", "square", "embankment", "bulvar", "prospekt"],
            "article": "5",
            "name": "Inozemny yazyk"
        },
        "ocenochnye_suzhdeniya": {
            "keywords": ["лучш", "уникальн", "единственн", "самый", "номер 1", "номер1", "#1", "первый", "лидер", "лидер рынка", "ведущий", "высочайш", "высококачествен", "превосходн", "безупречн", "идеальн", "новейш", "инновационн", "революционн", "ультативн", "эффективн", "гарантиров", "проверенн", "безопасн", "экологичн", "натуральн", "orgаник", "premium", "exclusive", "best", "top", "leading", "unique", "first", "only", " №1", "winner", " champion", "fastest", "cheapest", "most popular", "number one"],
            "article": "5",
            "name": "Otsenochnye suzhdeniya (trebuet dokazatelstv)"
        },
        "dostovernost": {
            "keywords": ["документ", "подтвержден", "сертификат", "лицензи", "одобрено", "рекомендован", "проверен", "клинически", "научно", "исследование", "статистик", "факт", "результат", "тест", "отзыв", "отзывы"],
            "article": "5",
            "name": "Dostovernost"
        }
    }
    
    found = set()
    
    def is_english_word(word):
        """Проверяет, что слово состоит только из английских букв"""
        return all(ord(c) < 128 for c in word)
    
    for cat_id, cat_data in categories.items():
        for keyword in cat_data["keywords"]:
            # Для иностранных языков - только английские слова
            if cat_id == "inozemny_yazyk":
                if is_english_word(keyword) and keyword.lower() in text_lower:
                    found.add(cat_id)
                    result["found_categories"].append({
                        "category": cat_id,
                        "name": cat_data["name"],
                        "keyword": keyword,
                        "article": cat_data["article"]
                    })
                    break
            else:
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
        result["potential_issues"].append("Реклама алкоголя - требуется проверка Статья 21")
        result["fix_recommendations"].append({
            "issue": "Реклама алкоголя",
            "fix": "Убедитесь, что: 1) Нет обращения к несовершеннолетним; 2) Указано предупреждение о вреде алкоголя; 3) Нет информации о превосходстве продукта; 4) Нет сравнений с конкурентами"
        })
        art = get_article("21")
        if art:
            result["recommendations"].append({
                "article": "21",
                "title": art["title"],
                "text": art["content"]
            })
        
        if "deti" in found:
            result["potential_issues"].append("ОГРАНИЧЕНИЕ! Реклама алкоголя для несовершеннолетних - ЗАПРЕТ Статья 6")
    
    if "lekarstvo" in found:
        result["potential_issues"].append("Реклама лекарств - требуется проверка Статья 24")
        result["fix_recommendations"].append({
            "issue": "Реклама лекарств",
            "fix": "Обязательно: 1) Указать номер регистрационного удостоверения; 2) Разместить предуждение 'Имеются противопоказания'; 3) Указать возрастные ограничения; 4) Не давать советов по лечению конкретных заболеваний; 5) Не использовать оценочные суждения без доказательств"
        })
        art = get_article("24")
        if art:
            result["recommendations"].append({
                "article": "24",
                "title": art["title"],
                "text": art["content"]
            })
        
        if "deti" in found:
            result["potential_issues"].append("ВНИМАНИЕ! Реклама лекарств для детей - требуется проверка по специальным правилам")
    
    if "deti" in found:
        result["potential_issues"].append("ОГРАНИЧЕНИЕ! Обращение к несовершеннолетним - Статья 6")
        result["fix_recommendations"].append({
            "issue": "Обращение к несовершеннолетним",
            "fix": "Проверьте: 1) Нет ли прямого обращения к детям ('ты', 'тебе', 'для тебя'); 2) Нет ли изображения детей в рекламе запрещённых товаров (алкоголь, табак, энергетики); 3) Указаны ли возрастные ограничения товара/услуги"
        })
        art = get_article("6")
        if art:
            result["recommendations"].append({
                "article": "6",
                "title": art["title"],
                "text": art["content"]
            })
        
        if "alkogol" in found or "tabak" in found:
            result["potential_issues"].append("ОГРАНИЧЕНИЕ! Обращение к детям в рекламе запрещённых товаров - Статья 6")
    
    if "finansy" in found:
        result["potential_issues"].append("Реклама финансовых услуг - проверка Статья 28")
        result["fix_recommendations"].append({
            "issue": "Реклама финансовых услуг",
            "fix": "Обязательно: 1) Указать конкретные условия (процентная ставка, срок); 2) Добавить предупреждение о рисках ('услуга не является гарантией доходности'); 3) Не обещать гарантированную доходность; 4) Указать наименование лицензии ЦБ РФ"
        })
        art = get_article("28")
        if art:
            result["recommendations"].append({
                "article": "28",
                "title": art["title"],
                "text": art["content"]
            })
        
        if "обман" in text_lower or "100%" in text_lower or "гарантия" in text_lower:
            result["potential_issues"].append("Подозрительная финансовая реклама - гарантии доходности запрещены")
        
        if "выгодн" in text_lower or "лучш" in text_lower or "оптимальн" in text_lower or "прибыльн" in text_lower:
            result["potential_issues"].append("ОГРАНИЧЕНИЕ! Гарантии выгоды - Статья 28, ч.2, п.1")
        
        if "высок" in text_lower and "ставк" in text_lower:
            result["potential_issues"].append("ОГРАНИЧЕНИЕ! Гарантии доходности без условий - Статья 28, ч.2, п.1")
        
        if "над" in text_lower and ("жн" in text_lower or "ёжн" in text_lower):
            result["potential_issues"].append("ОГРАНИЧЕНИЕ! Гарантии надёжности - Статья 28, ч.2")
        
        if "гарантиров" in text_lower:
            result["potential_issues"].append("ОГРАНИЧЕНИЕ! Гарантии в финансовой рекламе - Статья 28, ч.2")
        
        if "кредит" in text_lower or "заём" in text_lower or "займ" in text_lower or "карту" in text_lower or "карта" in text_lower:
            if not any(s in text_lower for s in ["изучите", "оценивайте", "риск"]):
                result["potential_issues"].append("ОГРАНИЧЕНИЕ! Нет предупреждения о рисках - Статья 28, ч.3.1")
            
            if not any(s in text_lower for s in ["процент", "ставк", "годов", "%", "рубл"]) and not any(s in text_lower for s in ["кешбэк", "кешбек", "кэшбэк", "кэшбек", "бонус"]):
                result["potential_issues"].append("ОГРАНИЧЕНИЕ! Нет конкретной ставки - Статья 28, ч.2.1")
        
        if "люб" in text_lower and "цел" in text_lower:
            result["potential_issues"].append("ВНИМАНИЕ! 'На любые цели' - требуется конкретизация условий")
        
        if " до " in text_lower or "до ₽" in text_lower or "до руб" in text_lower:
            result["potential_issues"].append("ВНИМАНИЕ! 'До' в финансовой рекламе может вводить в заблуждение")
    
    if "tabak" in found:
        result["potential_issues"].append("Реклама табачных изделий - проверка Статья 7")
        result["fix_recommendations"].append({
            "issue": "Реклама табачных изделий",
            "fix": "С 01.01.2023 реклама табачных изделий ЗАПРЕЩЕНА! Удалите рекламу табака полностью или замените на рекламу альтернатив (-device, бездымные продукты с указанием возрастного ограничения 18+)"
        })
        art = get_article("7")
        if art:
            result["recommendations"].append({
                "article": "7",
                "title": art["title"],
                "text": art["content"]
            })
    
    if "energetik" in found:
        result["potential_issues"].append("Реклама энергетических напитков - ограничения для несовершеннолетних")
        result["fix_recommendations"].append({
            "issue": "Реклама энергетиков",
            "fix": "Обязательно: 1) Указать возрастное ограничение 18+; 2) Добавить предупреждение о вреде для здоровья; 3) Не обращаться к несовершеннолетним; 4) Не использовать образы детей"
        })
        art = get_article("7")
        if art:
            result["recommendations"].append({
                "article": "7",
                "title": art["title"],
                "text": art["content"]
            })
        
        if "deti" in found:
            result["potential_issues"].append("ОГРАНИЧЕНИЕ! Реклама энергетиков несовершеннолетним - Статья 6")
    
    if "deti" in found and ("alkogol" in found or "tabak" in found or "energetik" in found):
        result["potential_issues"].append("ОГРАНИЧЕНИЕ! Обращение к несовершеннолетним в рекламе запрещённых товаров - Статья 6")
    
    if "super_ceny" in found:
        result["potential_issues"].append("ВНИМАНИЕ! Акции, скидки, подарки - проверка на достоверность условий, Статья 5")
        
        if "deti" in found:
            result["potential_issues"].append("ВНИМАНИЕ! Акции для детей - особые требования к рекламе")
    
    if "nedvizhimost" in found:
        result["potential_issues"].append("Реклама недвижимости - проверка Статья 28, ч.6-9")
        result["fix_recommendations"].append({
            "issue": "Реклама недвижимости",
            "fix": "Обязательно: 1) Указать номер проектной декларации; 2) Указать застройщика (ИНН, ОГРН); 3) Ссылка на ЕИСЖС (наш.дом.рф); 4) Не обещать конкретные сроки сдачи без разрешения; 5) Указать реальную площадь и цену (не 'от')"
        })
        
        if "отзыв" in text_lower:
            result["potential_issues"].append("ВНИМАНИЕ! Использование отзывов в рекламе - требуется доказательство достоверности, Статья 5")
            result["fix_recommendations"].append({
                "issue": "Отзывы в рекламе",
                "fix": "Добавьте: 1) Ссылку на источник отзывов; 2) Дату публикации; 3) Подтверждение, что отзывы реальных клиентов"
            })
        
        if "акци" in text_lower and "скидк" in text_lower:
            result["potential_issues"].append("ВНИМАНИЕ! Акции и скидки в рекламе недвижимости - нужно указать конкретные условия")
        
        if "цен" in text_lower and "от" in text_lower:
            result["potential_issues"].append("ВНИМАНИЕ! Указание 'от' в цене может быть недостоверным")
        
        if "срок сдач" in text_lower or ("сдач" in text_lower and "20" in text_lower):
            result["potential_issues"].append("ВНИМАНИЕ! Срок сдачи может измениться - нужна ссылка на разрешение на строительство")
        
        if "от застройщика" in text_lower and "ПИК" in text:
            result["potential_issues"].append("ВНИМАНИЕ! Реклама долевого строительства - нужна ссылка на ЕИСЖС")
        
        if "сбербанк" in text_lower and "домклик" in text_lower:
            if not any(s in text_lower for s in ["ипотек", "кредит", "заём", "ломбард"]):
                result["potential_issues"].append("ВНИМАНИЕ! Упоминание банка - может вводить в заблуждение о связи с банком")
    
    if "inozemny_yazyk" in found:
        result["potential_issues"].append("ОГРАНИЧЕНИЕ! Реклама на иностранном языке - Статья 5, ч.5, п.1 (ЗАПРЕТ с 01.03.2025)")
        result["fix_recommendations"].append({
            "issue": "Иностранный язык в рекламе",
            "fix": "С 01.03.2025 ЗАПРЕЩЕНО использование иностранных слов без перевода! Замените все иностранные слова на русские эквиваленты (premium -> премиум, city -> город, luxury -> роскошь)"
        })
        art = get_article("5")
        if art:
            result["recommendations"].append({
                "article": "5",
                "title": art["title"],
                "text": art["content"]
            })
    
    import re
    age_pattern = re.compile(r'от\s*(\d+)\s*до\s*(\d+)\s*лет|возраст[ау]?\s*от\s*(\d+)|(\d+)\s*-\s*(\d+)\s*лет')
    age_match = age_pattern.search(text_lower)
    if age_match:
        ages = [int(x) for x in age_match.groups() if x and x.isdigit()]
        if ages:
            min_age = min(ages)
            if min_age < 18:
                result["potential_issues"].append(f"ОГРАНИЧЕНИЕ! Реклама для несовершеннолетних (от {min_age} лет) - Статья 6")
    
    if "тебе" in text_lower or "тебя" in text_lower or "ты" in text_lower:
        if "лет" in text_lower or "года" in text_lower:
            result["potential_issues"].append("ВНИМАНИЕ! Прямое обращение к возрастной группе - проверьте возрастные ограничения")
    
    if "obman" in found:
        result["potential_issues"].append("Потенциальный обман в рекламе - требуется проверка Статья 5")
        result["fix_recommendations"].append({
            "issue": "Потенциальный обман",
            "fix": "Проверьте: 1) Нет ли завышенных обещаний ('100% гарантия'); 2) Указаны ли реальные сроки и условия акции; 3) Есть ли подтверждение всех заявленных фактов"
        })
        art = get_article("5")
        if art:
            result["recommendations"].append({
                "article": "5",
                "title": art["title"],
                "text": art["content"]
            })
    
    if "ocenochnye_suzhdeniya" in found:
        result["potential_issues"].append("ТРЕБУЕТСЯ ПОДТВЕРЖДЕНИЕ! Оценочные суждения в рекламе - необходимы доказательства, Статья 5, ч.1")
        result["fix_recommendations"].append({
            "issue": "Оценочные суждения",
            "fix": "Для использования слов 'лучший', 'уникальный', 'номер 1' и т.д. необходимо: 1) Добавить ссылку на подтверждающий документ (сертификат, исследование, рейтинг); 2) Указать источник ('по данным независимого исследования...'); 3) Или заменить на фактические данные"
        })
        
        has_proof = False
        proof_keywords = ["документ", "подтвержден", "сертификат", "лицензи", "одобрено", "рекомендован", "проверен", "клинически", "научно", "исследование", "статистик", "факт", "результат", "тест", "отзыв", "отзывы", "клиенты", "патенты", "награды", "премии", "рейтинг", "сертификат", "декларация", "регистрационное удостоверение"]
        
        for kw in proof_keywords:
            if kw in text_lower:
                has_proof = True
                break
        
        if not has_proof:
            result["potential_issues"].append("ОТКАЗ! Бездоказательные оценочные суждения запрещены - ФЗ-38 Статья 5, ч.1")
        else:
            result["found_categories"].append({
                "category": "dostovernost",
                "name": "Dostovernost podtverzhdena",
                "keyword": "Подтверждающие документы найдены",
                "article": "5"
            })
        
        art = get_article("5")
        if art:
            result["recommendations"].append({
                "article": "5",
                "title": art["title"],
                "text": art["content"]
            })
    
    superlative_patterns = [
        r'\bсамый\s+\w+',
        r'\bлучш\w*\b',
        r'\bуникальн\w*\b',
        r'\bединственн\w*\b',
        r'\bперв\w*\b',
        r'\bлидер\w*\b',
        r'\bведущ\w*\b',
        r'\bномер\s*1\b',
        r'\b#1\b',
        r'\bпревосходн\w*\b',
        r'\bвысочайш\w*\b',
        r'\bидеальн\w*\b',
        r'\bгарантиров\w*\b',
    ]
    
    for pattern in superlative_patterns:
        if re.search(pattern, text_lower):
            result["potential_issues"].append(f"НАРУШЕНИЕ! Найдено превосходное/бездоказательное утверждение: '{pattern}' - требуется подтверждение, ФЗ-38 Ст.5")
            break
    
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
    
    if result["fix_recommendations"]:
        output += "REKOMENDATSII PO ISPRAVLENIYU:\n"
        output += "-" * 40 + "\n"
        for rec in result["fix_recommendations"]:
            output += f"\n[ {rec['issue']} ]\n"
            output += f"   >>> {rec['fix']}\n"
        output += "\n"
    
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
