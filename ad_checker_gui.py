import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_text import check_text


class AdCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Проверка рекламы на ФЗ \"О рекламе\"")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_label = ttk.Label(
            main_frame, 
            text="Проверка рекламы на ФЗ \"О рекламе\" (38-ФЗ)",
            font=("Arial", 14, "bold")
        )
        header_label.pack(pady=(0, 15))
        
        # Блок ввода текста
        input_frame = ttk.LabelFrame(main_frame, text="Текст рекламы для проверки:", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Поле ввода с поддержкой Ctrl+V
        self.input_text = tk.Text(
            input_frame, 
            height=3, 
            wrap=tk.WORD,
            font=("Arial", 11)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(input_frame, command=self.input_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.config(yscrollcommand=scrollbar.set)
        
        # Кнопка проверки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.check_btn = ttk.Button(
            btn_frame, 
            text="Проверить текст", 
            command=self.check_ad
        )
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            btn_frame, 
            text="Очистить", 
            command=self.clear_all
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Блок результатов
        result_frame = ttk.LabelFrame(main_frame, text="Результат проверки:", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Статус проверки
        self.status_label = ttk.Label(
            result_frame,
            text="Введите текст и нажмите \"Проверить текст\"",
            font=("Arial", 12, "bold"),
            foreground="gray"
        )
        self.status_label.pack(pady=(0, 10))
        
        # Текст результата - включаем поддержку Ctrl+V
        # Контекстное меню
        self.context_menu = tk.Menu(self.input_text, tearoff=0)
        self.context_menu.add_command(label="Вставить", command=self.paste_text_from_menu)
        self.context_menu.add_command(label="Копировать", command=lambda: self.input_text.event_generate('<<Copy>>'))
        self.context_menu.add_command(label="Вырезать", command=lambda: self.input_text.event_generate('<<Cut>>'))
        self.context_menu.add_command(label="Очистить", command=lambda: self.input_text.delete("1.0", tk.END))
        self.input_text.bind("<Button-3>", self.show_context_menu)
        
        # Закрыть меню при клике
        self.input_text.bind("<Button-1>", lambda e: self.context_menu.unpost())
        
        self.result_text = tk.Text(
            result_frame, 
            height=20, 
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбар для результата
        result_scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=result_scrollbar.set, state=tk.DISABLED)
        
        # Примеры
        examples_frame = ttk.LabelFrame(main_frame, text="Быстрые примеры:", padding="10")
        examples_frame.pack(fill=tk.X, pady=(10, 0))
        
        examples = [
            ("Банк", "Сбер: надёжный банк с высокой ставкой по вкладу"),
            ("Молодёж", "Тебе от 14 до 24 лет? Оформи молодежную карту"),
            ("Недвижимость", "ЖК Holland Park - отзывы и скидки"),
            ("Обувь", "Купите качественную обувь в магазине"),
            ("Алкоголь", "Скидки на водку 50%"),
        ]
        
        for i, (name, text) in enumerate(examples):
            btn = ttk.Button(
                examples_frame, 
                text=name,
                width=12,
                command=lambda t=text: self.load_example(t)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def load_example(self, text):
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", text)
        self.check_ad()
    
    def paste_text_from_menu(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.input_text.insert(tk.INSERT, clipboard_text)
        except:
            pass
    
    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.status_label.config(text="Введите текст и нажмите \"Проверить текст\"", foreground="gray")
    
    def check_ad(self):
        text = self.input_text.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("Внимание", "Введите текст рекламы для проверки!")
            return
        
        # Проверка текста
        result = check_text(text)
        issues = result.get("potential_issues", [])
        fix_recs = result.get("fix_recommendations", [])
        
        # Формируем результат
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        
        if issues:
            self.status_label.config(text="❌ НАРУШЕНИЯ ВЫЯВЛЕНЫ", foreground="red")
            
            self.result_text.insert(tk.END, "⚠️  НАЙДЕННЫЕ ПРОБЛЕМЫ:\n")
            self.result_text.insert(tk.END, "─" * 50 + "\n")
            
            # Группируем по категориям
            categories = {"children": [], "finance": [], "foreign": [], "price": [], "other": []}
            
            for issue in issues:
                issue_lower = issue.lower()
                if "nesovershennoletnim" in issue_lower or "statya 6" in issue_lower:
                    categories["children"].append(issue)
                elif "statya 28" in issue_lower or "finans" in issue_lower:
                    categories["finance"].append(issue)
                elif "inozemny" in issue_lower:
                    categories["foreign"].append(issue)
                elif "skidk" in issue_lower or "akci" in issue_lower or "cen" in issue_lower or "podar" in issue_lower or "bon" in issue_lower:
                    categories["price"].append(issue)
                elif "statya 5" in issue_lower:
                    categories["other"].append(issue)
                else:
                    categories["other"].append(issue)
            
            if categories["children"]:
                self.result_text.insert(tk.END, "👶 ПРОБЛЕМЫ С НЕСОВЕРШЕННОЛЕТНИМИ:\n")
                for issue in categories["children"]:
                    self.result_text.insert(tk.END, f"  • {self.clean_issue(issue)}\n")
                self.result_text.insert(tk.END, "\n")
            
            if categories["finance"]:
                self.result_text.insert(tk.END, "💰 ПРОБЛЕМЫ С ФИНАНСАМИ:\n")
                for issue in categories["finance"]:
                    self.result_text.insert(tk.END, f"  • {self.clean_issue(issue)}\n")
                self.result_text.insert(tk.END, "\n")
            
            if categories["foreign"]:
                self.result_text.insert(tk.END, "🌐 ИНОСТРАННЫЕ СЛОВА:\n")
                for issue in categories["foreign"]:
                    self.result_text.insert(tk.END, f"  • {self.clean_issue(issue)}\n")
                self.result_text.insert(tk.END, "\n")
            
            if categories["price"]:
                self.result_text.insert(tk.END, "💵 ЦЕНЫ И АКЦИИ:\n")
                for issue in categories["price"]:
                    self.result_text.insert(tk.END, f"  • {self.clean_issue(issue)}\n")
                self.result_text.insert(tk.END, "\n")
            
            if categories["other"]:
                self.result_text.insert(tk.END, "📋 ДРУГОЕ:\n")
                for issue in categories["other"]:
                    self.result_text.insert(tk.END, f"  • {self.clean_issue(issue)}\n")
                self.result_text.insert(tk.END, "\n")
            
            # Рекомендации по исправлению из check_text
            self.result_text.insert(tk.END, "\n" + "─" * 50 + "\n")
            self.result_text.insert(tk.END, "💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:\n")
            self.result_text.insert(tk.END, "─" * 50 + "\n")
            
            if fix_recs:
                for rec in fix_recs:
                    self.result_text.insert(tk.END, f"\n[{rec.get('issue', 'Проблема')}]\n")
                    self.result_text.insert(tk.END, f"   {rec.get('fix', '')}\n")
            else:
                recs = self.get_recommendations(issues)
                for i, rec in enumerate(recs, 1):
                    self.result_text.insert(tk.END, f"  {i}. {rec}\n")
            
            # Статьи
            self.result_text.insert(tk.END, "\n" + "─" * 50 + "\n")
            self.result_text.insert(tk.END, "📚 ПРИМЕНИМЫЕ СТАТЬИ ФЗ:\n")
            self.result_text.insert(tk.END, "─" * 50 + "\n")
            
            articles = set()
            for issue in issues:
                if "Статья 6" in issue or "STATYA 6" in issue.upper():
                    articles.add("Статья 6. Защита несовершеннолетних")
                if "Статья 28" in issue or "STATYA 28" in issue.upper():
                    articles.add("Статья 28. Реклама финансовых услуг")
                if "Статья 5" in issue or "STATYA 5" in issue.upper():
                    articles.add("Статья 5. Общие требования к рекламе")
            
            for art in articles:
                self.result_text.insert(tk.END, f"  ⚖️  {art}\n")
        
        else:
            self.status_label.config(text="✅ НАРУШЕНИЙ НЕ ВЫЯВЛЕНО", foreground="green")
            
            self.result_text.insert(tk.END, "✅ Ваш текст соответствует требованиям ФЗ \"О рекламе\"\n\n")
            self.result_text.insert(tk.END, "Тем не менее рекомендуем проверить текст на:\n")
            self.result_text.insert(tk.END, "  • Добросовестность рекламы\n")
            self.result_text.insert(tk.END, "  • Достоверность информации\n")
            self.result_text.insert(tk.END, "  • Соответствие другим статьям закона\n")
        
        self.result_text.config(state=tk.DISABLED)
    
    def clean_issue(self, issue):
        issue = issue.replace("NARUSHENIE! ", "")
        issue = issue.replace("VNIMANIE! ", "")
        issue = issue.replace("STATYA", "Статья")
        issue = issue.replace("CH.", "ч.")
        issue = issue.replace("P.", "п.")
        return issue
    
    def get_recommendations(self, issues):
        recs = []
        issues_text = " ".join(issues).lower()
        
        if "nesovershennoletnim" in issues_text:
            recs.append("Убедитесь, что реклама НЕ обращена к лицам младше 18 лет")
            recs.append("Удалите указание возраста или обращение 'Тебе/ты'")
        
        if "statya 28" in issues_text or "finans" in issues_text:
            if "ставк" in issues_text or "stavk" in issues_text:
                recs.append("Добавьте конкретную процентную ставку (например: 15% годовых)")
            if "риск" in issues_text or "risk" in issues_text:
                recs.append("Добавьте предупреждение: 'Оценивайте свои финансовые возможности и риски'")
            if "надёж" in issues_text or "nadezh" in issues_text or "выгодн" in issues_text:
                recs.append("Уберите слова 'надёжный', 'выгодный', 'лучший' - это гарантии")
            recs.append("Укажите полное наименование банка/финансовой организации")
        
        if "inozemny" in issues_text:
            recs.append("Замените иностранные слова на русские (Holland Park → Парк)")
        
        if "ot " in issues_text and "cen" in issues_text:
            recs.append("Укажите точную цену вместо 'от X рублей'")
        if "skidk" in issues_text or "акци" in issues_text:
            recs.append("Укажите конкретные условия акции/скидки и сроки")
        
        if "otzyv" in issues_text:
            recs.append("Удалите отзывы или укажите их официальный источник")
        
        if "srok" in issues_text:
            recs.append("Добавьте ссылку на ЕИСЖС и реквизиты разрешения на строительство")
        
        return list(dict.fromkeys(recs))


def main():
    root = tk.Tk()
    app = AdCheckerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
