# ==========================================
# PORTABLE USER FILE RESOLVER
# ==========================================
def get_user_file_path(relative_path):
    import sys
    import os
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))


import sqlite3
import os
import random
import re
from datetime import datetime

# ==========================================
# DATABASE MANAGER (WITH DYNAMIC GIF REWARDS)
# ==========================================
class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = get_user_file_path("sprint_data.db")
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initializes database schema with speed performance PRAGMAs and indexes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # Settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time_limit_sec INTEGER DEFAULT 60,
                    zoom_percent INTEGER DEFAULT 100,
                    animations_enabled INTEGER DEFAULT 1
                )
            """)
            
            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO settings (time_limit_sec, zoom_percent, animations_enabled) VALUES (60, 100, 1)")
                
            cursor.execute("PRAGMA table_info(settings)")
            settings_cols = [info[1] for info in cursor.fetchall()]
            if "zoom_percent" not in settings_cols:
                cursor.execute("ALTER TABLE settings ADD COLUMN zoom_percent INTEGER DEFAULT 100")
            if "animations_enabled" not in settings_cols:
                cursor.execute("ALTER TABLE settings ADD COLUMN animations_enabled INTEGER DEFAULT 1")
            if "yandex_token" not in settings_cols:
                cursor.execute("ALTER TABLE settings ADD COLUMN yandex_token TEXT DEFAULT NULL")
            if "last_auto_backup" not in settings_cols:
                cursor.execute("ALTER TABLE settings ADD COLUMN last_auto_backup TEXT DEFAULT NULL")
                
            # Classes/Sections Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    sort_order INTEGER DEFAULT 0
                )
            """)
            
            # Seed default classes (from 10-11 down to 1)
            default_classes = [
                "10-11 класс", "9 класс", "8 класс", "7 класс", "6 класс", 
                "5 класс", "4 класс", "3 класс", "2 класс", "1 класс"
            ]
            for cl_name in default_classes:
                cursor.execute("SELECT COUNT(*) FROM classes WHERE name = ?", (cl_name,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO classes (name) VALUES (?)", (cl_name,))
                
            # Topics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
                    sort_order INTEGER DEFAULT 0
                )
            """)
            
            cursor.execute("PRAGMA table_info(topics)")
            topic_cols = [info[1] for info in cursor.fetchall()]
            if "class_id" not in topic_cols:
                cursor.execute("ALTER TABLE topics ADD COLUMN class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE")
            
            # Questions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    question_type TEXT DEFAULT 'text',
                    image_path TEXT DEFAULT NULL,
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("PRAGMA table_info(questions)")
            cols = [info[1] for info in cursor.fetchall()]
            if "question_type" not in cols:
                cursor.execute("ALTER TABLE questions ADD COLUMN question_type TEXT DEFAULT 'text'")
            if "image_path" not in cols:
                cursor.execute("ALTER TABLE questions ADD COLUMN image_path TEXT DEFAULT NULL")
                
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_topic_id ON questions(topic_id);")
                
            # History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_name TEXT NOT NULL,
                    score TEXT NOT NULL,
                    time_spent INTEGER NOT NULL,
                    date_time TEXT NOT NULL,
                    student_name TEXT DEFAULT 'Ученик'
                )
            """)
            
            cursor.execute("PRAGMA table_info(history)")
            hist_cols = [info[1] for info in cursor.fetchall()]
            if "student_name" not in hist_cols:
                cursor.execute("ALTER TABLE history ADD COLUMN student_name TEXT DEFAULT 'Ученик'")
                
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_topic_name ON history(topic_name);")
            
            cursor.execute("PRAGMA table_info(history)")
            history_cols = [info[1] for info in cursor.fetchall()]
            if "time_limit" not in history_cols:
                cursor.execute("ALTER TABLE history ADD COLUMN time_limit INTEGER DEFAULT 60")
            
            # NEW: Reward GIFs Table with Multi-Attribute capabilities!
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reward_gifs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    old_1 INTEGER DEFAULT 0,
                    old_2 INTEGER DEFAULT 0,
                    old_3 INTEGER DEFAULT 0
                )
            """)
            
            # --- POST-CREATION MIGRATIONS FOR SORT ORDER ---
            cursor.execute("PRAGMA table_info(classes)")
            classes_cols = [info[1] for info in cursor.fetchall()]
            if "sort_order" not in classes_cols:
                cursor.execute("ALTER TABLE classes ADD COLUMN sort_order INTEGER DEFAULT 0")
                
            cursor.execute("PRAGMA table_info(topics)")
            topics_cols = [info[1] for info in cursor.fetchall()]
            if "sort_order" not in topics_cols:
                cursor.execute("ALTER TABLE topics ADD COLUMN sort_order INTEGER DEFAULT 0")
                
            # If default sorting orders are all 0, assign them
            cursor.execute("SELECT COUNT(*) FROM classes WHERE sort_order != 0")
            if cursor.fetchone()[0] == 0:
                cursor.execute("SELECT id, name FROM classes")
                classes_rows = cursor.fetchall()
                def get_cl_num(row):
                    import re
                    name_str = row[1]
                    digits = re.findall(r'\d+', name_str)
                    return max(int(d) for d in digits) if digits else 0
                classes_rows.sort(key=get_cl_num, reverse=True)
                for idx, (cid, name_str) in enumerate(classes_rows):
                    cursor.execute("UPDATE classes SET sort_order = ? WHERE id = ?", ((idx + 1) * 10, cid))
                    
            cursor.execute("SELECT COUNT(*) FROM topics WHERE sort_order != 0")
            if cursor.fetchone()[0] == 0:
                cursor.execute("SELECT id, name, class_id FROM topics")
                for idx, (tid, name_str, cid) in enumerate(cursor.fetchall()):
                    cursor.execute("UPDATE topics SET sort_order = ? WHERE id = ?", ((idx + 1) * 10, tid))
                    
            conn.commit()
            
        self.seed_default_data()

    def seed_default_data(self):
        """Seeds default classes, topics, questions, and parses existing GIFs into the database."""
        # Setup helper resolver
        # Importing lazily here to prevent circular dependency
        from assets_manager import get_asset_path
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Retrieve class IDs
            cursor.execute("SELECT id, name FROM classes")
            class_map = {name: cid for cid, name in cursor.fetchall()}
            
            # Comprehensive academic math curriculum mapping (FGOS standard)
            math_seed_data = {
                "1 класс": [
                    {
                        "topic": "Сложение и вычитание до 20",
                        "questions": [
                            ("5 + 3 = ?", "8", "text"),
                            ("10 - 4 = ?", "6", "text"),
                            ("12 + 5 = ?", "17", "text"),
                            ("18 - 6 = ?", "12", "text"),
                            ("9 + 6 = ?", "15", "text"),
                            ("15 - 7 = ?", "8", "text"),
                            ("14 + 4 = ?", "18", "text"),
                            ("20 - 9 = ?", "11", "text"),
                            ("8 + 7 = ?", "15", "text"),
                            ("13 - 5 = ?", "8", "text")
                        ]
                    },
                    {
                        "topic": "Текстовые задачи 1 класс",
                        "questions": [
                            ("У Вани было 6 яблок, а у Маши на 3 больше. Сколько яблок у Маши?", "9", "text"),
                            ("В коробке лежало 10 карандашей. 4 карандаша достали. Сколько осталось?", "6", "text"),
                            ("На ветке сидело 5 птиц. Прилетело еще 4. Сколько птиц стало?", "9", "text"),
                            ("У Юры было 8 марок. Он подарил другу 3 марки. Сколько марок осталось у Юры?", "5", "text"),
                            ("На столе стояло 7 чашек. Поставили еще 5 чашек. Сколько чашек стало на столе?", "12", "text")
                        ]
                    }
                ],
                "2 класс": [
                    {
                        "topic": "Умножение и деление (базовое)",
                        "questions": [
                            ("2 * 4 = ?", "8", "text"),
                            ("3 * 5 = ?", "15", "text"),
                            ("12 : 2 = ?", "6", "text"),
                            ("15 : 3 = ?", "5", "text"),
                            ("4 * 3 = ?", "12", "text"),
                            ("10 : 2 = ?", "5", "text"),
                            ("5 * 4 = ?", "20", "text"),
                            ("18 : 3 = ?", "6", "text"),
                            ("2 * 9 = ?", "18", "text"),
                            ("16 : 4 = ?", "4", "text")
                        ]
                    },
                    {
                        "topic": "Сложение и вычитание в пределах 100",
                        "questions": [
                            ("32 + 15 = ?", "47", "text"),
                            ("58 - 24 = ?", "34", "text"),
                            ("45 + 26 = ?", "71", "text"),
                            ("72 - 38 = ?", "34", "text"),
                            ("64 + 18 = ?", "82", "text"),
                            ("90 - 45 = ?", "45", "text")
                        ]
                    }
                ],
                "3 класс": [
                    {
                        "topic": "Внетиповое умножение и деление",
                        "questions": [
                            ("12 * 4 = ?", "48", "text"),
                            ("15 * 3 = ?", "45", "text"),
                            ("48 : 3 = ?", "16", "text"),
                            ("60 : 4 = ?", "15", "text"),
                            ("13 * 5 = ?", "65", "text"),
                            ("72 : 6 = ?", "12", "text"),
                            ("14 * 3 = ?", "42", "text"),
                            ("96 : 8 = ?", "12", "text")
                        ]
                    },
                    {
                        "topic": "Простые уравнения 3 класс",
                        "questions": [
                            ("x + 15 = 40 (найдите x)", "25", "text"),
                            ("x - 12 = 18 (найдите x)", "30", "text"),
                            ("50 - x = 23 (найдите x)", "27", "text"),
                            ("4 * x = 36 (найдите x)", "9", "text"),
                            ("x : 3 = 15 (найдите x)", "45", "text"),
                            ("32 : x = 8 (найдите x)", "4", "text")
                        ]
                    }
                ],
                "4 класс": [
                    {
                        "topic": "Вычисления с большими числами",
                        "questions": [
                            ("150 + 230 = ?", "380", "text"),
                            ("500 - 180 = ?", "320", "text"),
                            ("25 * 4 = ?", "100", "text"),
                            ("120 : 5 = ?", "24", "text"),
                            ("360 : 6 = ?", "60", "text"),
                            ("15 * 6 = ?", "90", "text"),
                            ("1000 - 350 = ?", "650", "text")
                        ]
                    },
                    {
                        "topic": "Задачи на движение и время",
                        "questions": [
                            ("Поезд идет со скоростью 60 км/ч. Какое расстояние он проедет за 3 часа (в км)?", "180", "text"),
                            ("Велосипедист проехал 48 км за 4 часа. С какой скоростью он ехал (в км/ч)?", "12", "text"),
                            ("Пешеход идет со скоростью 5 км/ч. За сколько часов он пройдет 25 км?", "5", "text"),
                            ("Автомобиль проехал 120 км со скоростью 40 км/ч. Сколько времени занял путь (в часах)?", "3", "text")
                        ]
                    }
                ],
                "5 класс": [
                    {
                        "topic": "Таблица умножения",
                        "questions": [
                            ("2 * 2 = ?", "4", "text"),
                            ("3 * 4 = ?", "12", "text"),
                            ("5 * 6 = ?", "30", "text"),
                            ("7 * 8 = ?", "56", "text"),
                            ("9 * 9 = ?", "81", "text"),
                            ("6 * 7 = ?", "42", "text"),
                            ("4 * 8 = ?", "32", "text"),
                            ("3 * 9 = ?", "27", "text"),
                            ("8 * 6 = ?", "48", "text"),
                            ("7 * 7 = ?", "49", "text")
                        ]
                    },
                    {
                        "topic": "Уравнения 5 класс",
                        "questions": [
                            ("x + 12 = 20 (найдите x)", "8", "text"),
                            ("x - 5 = 15 (найдите x)", "20", "text"),
                            ("30 - x = 12 (найдите x)", "18", "text"),
                            ("4 * x = 24 (найдите x)", "6", "text"),
                            ("x : 5 = 7 (найдите x)", "35", "text"),
                            ("42 : x = 6 (найдите x)", "7", "text")
                        ]
                    }
                ],
                "6 класс": [
                    {
                        "topic": "Дроби 6 класс (LaTeX)",
                        "questions": [
                            (r"\frac{1}{2} + \frac{1}{4} = ?", "3/4", "latex"),
                            (r"\frac{1}{3} + \frac{1}{6} = ?", "1/2", "latex"),
                            (r"\frac{3}{4} - \frac{1}{2} = ?", "1/4", "latex"),
                            (r"\frac{2}{5} + \frac{1}{5} = ?", "3/5", "latex"),
                            (r"1 - \frac{2}{3} = ?", "1/3", "latex"),
                            (r"\frac{1}{2} \cdot \frac{1}{3} = ?", "1/6", "latex"),
                            (r"\frac{3}{5} \cdot \frac{5}{3} = ?", "1", "latex"),
                            (r"\frac{1}{2} : \frac{1}{4} = ?", "2", "latex"),
                            (r"2 : \frac{1}{2} = ?", "4", "latex"),
                            (r"\frac{3}{8} + \frac{1}{8} = ?", "1/2", "latex")
                        ]
                    },
                    {
                        "topic": "Положительные и отрицательные числа",
                        "questions": [
                            ("-5 + 8 = ?", "3", "text"),
                            ("-12 - 7 = ?", "-19", "text"),
                            ("10 - (-4) = ?", "14", "text"),
                            ("-6 * 3 = ?", "-18", "text"),
                            ("-20 : (-4) = ?", "5", "text"),
                            ("15 + (-22) = ?", "-7", "text"),
                            ("-8 - (-12) = ?", "4", "text")
                        ]
                    }
                ],
                "7 класс": [
                    {
                        "topic": "Линейные уравнения",
                        "questions": [
                            ("2x + 5 = 15 (найдите x)", "5", "text"),
                            ("3x - 7 = 11 (найдите x)", "6", "text"),
                            ("10 - 2x = 4 (найдите x)", "3", "text"),
                            ("5x + 3 = 3x + 11 (найдите x)", "4", "text"),
                            ("12 - 4x = 2x (найдите x)", "2", "text"),
                            ("4x - 8 = 0 (найдите x)", "2", "text")
                        ]
                    },
                    {
                        "topic": "Формулы сокращенного умножения (ФСУ)",
                        "questions": [
                            ("Разложите (x-2)^2. Какое число будет на конце выражения без x?", "4", "text"),
                            ("Вычислите 49^2 - 51^2 = ?", "-200", "text"),
                            ("Упростите (a-3)(a+3) + 9. Чему равно выражение при a=5?", "25", "text"),
                            ("Разложите (x+4)^2. Чему равен коэффициент перед x?", "8", "text")
                        ]
                    }
                ],
                "8 класс": [
                    {
                        "topic": "Квадратные корни",
                        "questions": [
                            (r"\sqrt{64} = ?", "8", "latex"),
                            (r"\sqrt{121} = ?", "11", "latex"),
                            (r"\sqrt{2} \cdot \sqrt{8} = ?", "4", "latex"),
                            (r"\frac{\sqrt{75}}{\sqrt{3}} = ?", "5", "latex"),
                            (r"\sqrt{49} - \sqrt{9} = ?", "4", "latex"),
                            (r"(\sqrt{13})^2 = ?", "13", "latex")
                        ]
                    },
                    {
                        "topic": "Квадратные уравнения",
                        "questions": [
                            ("x^2 - 5x + 6 = 0 (найдите бОльший корень)", "3", "text"),
                            ("x^2 - 4x + 4 = 0 (найдите единственный корень)", "2", "text"),
                            ("x^2 - 9 = 0 (найдите положительный корень)", "3", "text"),
                            ("Найдите дискриминант уравнения: x^2 - 6x + 5 = 0", "16", "text"),
                            ("x^2 - 7x + 12 = 0 (найдите меньший корень)", "3", "text"),
                            ("2x^2 - 5x + 2 = 0 (найдите дискриминант)", "9", "text")
                        ]
                    }
                ],
                "9 класс": [
                    {
                        "topic": "Прогрессии",
                        "questions": [
                            ("Арифметическая прогрессия: a_1=3, d=4. Найдите a_5", "19", "text"),
                            ("Арифметическая прогрессия: a_1=10, d=-2. Найдите a_6", "0", "text"),
                            ("Найдите сумму первых 5 членов прогрессии, где a_1=2, d=3", "40", "text"),
                            ("Геометрическая прогрессия: b_1=2, q=3. Найдите b_4", "54", "text"),
                            ("Геометрическая прогрессия: b_1=16, q=1/2. Найдите b_5", "1", "text")
                        ]
                    },
                    {
                        "topic": "Квадратные неравенства",
                        "questions": [
                            ("При каких целых положительных x верно неравенство: x^2 - 4 < 0?", "1", "text"),
                            (r"Найдите количество целых решений неравенства x^2 - 5x + 4 \le 0", "4", "text")
                        ]
                    }
                ],
                "10-11 класс": [
                    {
                        "topic": "Тригонометрия",
                        "questions": [
                            (r"\sin^2(x) + \cos^2(x) = ?", "1", "latex"),
                            (r"\cos(2\pi) = ?", "1", "latex"),
                            (r"\sin(\frac{\pi}{6}) = ?", "1/2", "latex"),
                            (r"\cos(\frac{\pi}{3}) = ?", "1/2", "latex"),
                            (r"\tan(x) \cdot \cot(x) = ?", "1", "latex"),
                            (r"\sin(-\frac{\pi}{2}) = ?", "-1", "latex")
                        ]
                    },
                    {
                        "topic": "Производная и логарифмы",
                        "questions": [
                            ("Чему равна производная функции f(x) = x^2 - 5x в точке x=3?", "1", "text"),
                            ("Чему равна производная функции f(x) = 3x^3 в точке x=1?", "9", "text"),
                            (r"\log_2(8) = ?", "3", "latex"),
                            (r"\log_3(81) = ?", "4", "latex"),
                            (r"\log_5(1) = ?", "0", "latex"),
                            (r"2^{\log_2(5)} = ?", "5", "latex"),
                            (r"\log_6(2) + \log_6(3) = ?", "1", "latex")
                        ]
                    }
                ]
            }
            
            # Seed topics and questions safely and non-destructively
            for cl_name, topics_list in math_seed_data.items():
                class_id = class_map.get(cl_name)
                if not class_id:
                    continue
                    
                for t_data in topics_list:
                    topic_name = t_data["topic"]
                    
                    # Ensure topic exists
                    cursor.execute("SELECT id FROM topics WHERE name = ? AND class_id = ?", (topic_name, class_id))
                    topic_row = cursor.fetchone()
                    if not topic_row:
                        cursor.execute("INSERT INTO topics (name, class_id) VALUES (?, ?)", (topic_name, class_id))
                        topic_id = cursor.lastrowid
                    else:
                        topic_id = topic_row[0]
                        
                    # Seed questions if missing
                    cursor.execute("SELECT COUNT(*) FROM questions WHERE topic_id = ?", (topic_id,))
                    if cursor.fetchone()[0] == 0:
                        for q, a, t in t_data["questions"]:
                            cursor.execute("INSERT INTO questions (topic_id, question_text, correct_answer, question_type) VALUES (?, ?, ?, ?)",
                                           (topic_id, q, a, t))
            conn.commit()

            # Pre-seed history with simple integer score results (only if empty)
            cursor.execute("SELECT COUNT(*) FROM history")
            if cursor.fetchone()[0] == 0:
                history_seeds = [
                    ('Дроби 6 класс (LaTeX)', '15', 60, 'Алексей Смирнов'),
                    ('Дроби 6 класс (LaTeX)', '12', 60, 'Мария Иванова'),
                    ('Дроби 6 класс (LaTeX)', '9', 60, 'Даниил Попов'),
                    ('Таблица умножения', '28', 60, 'Александр Козлов'),
                    ('Таблица умножения', '25', 60, 'Екатерина Морозова'),
                    ('Таблица умножения', '22', 60, 'Дмитрий Соколов'),
                    ('Уравнения 5 класс', '14', 60, 'Никита Васильев'),
                    ('Уравнения 5 класс', '11', 60, 'Анна Кузнецова')
                ]
                now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
                for topic, score, spent, student in history_seeds:
                    cursor.execute("INSERT INTO history (topic_name, score, time_spent, date_time, student_name) VALUES (?, ?, ?, ?, ?)",
                                   (topic, score, spent, now_str, student))
                conn.commit()

            # Seed/parse the reward_gifs table on first launch!
            cursor.execute("SELECT COUNT(*) FROM reward_gifs")
            if cursor.fetchone()[0] == 0:
                assets_dir = get_asset_path("assets")
                if os.path.exists(assets_dir):
                    for fname in os.listdir(assets_dir):
                        if not fname.endswith('.gif'):
                            continue
                        name_lower = fname.lower()
                        
                        event_type = None
                        for et in ['score_3', 'score_5', 'score_10', 'unscore_3', 'unscore_5', 'unscore_10']:
                            if et in name_lower:
                                event_type = et
                                break
                                
                        if not event_type:
                            if 'unscore_10' in name_lower or 'unscore_5' in name_lower:
                                event_type = 'unscore_5'
                            elif 'score_10' in name_lower:
                                event_type = 'score_10'
                            else:
                                if fname == "ronaldo.gif":
                                    event_type = "score_10"
                                else:
                                    continue
                                    
                        gender = 'all'
                        if 'boys' in name_lower:
                            gender = 'boys'
                        elif 'girl' in name_lower:
                            gender = 'girl'
                            
                        old_1 = 1 if 'old_1' in name_lower else 0
                        old_2 = 1 if 'old_2' in name_lower else 0
                        old_3 = 1 if 'old_3' in name_lower else 0
                        
                        if fname == "ronaldo.gif" or 'old_unscore_3' in name_lower:
                            old_1 = old_2 = old_3 = 1
                            gender = 'all'
                            
                        try:
                            cursor.execute("""
                                INSERT INTO reward_gifs (filename, event_type, gender, old_1, old_2, old_3)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (fname, event_type, gender, old_1, old_2, old_3))
                        except sqlite3.IntegrityError:
                            pass
                conn.commit()

    # Settings
    def get_settings(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT time_limit_sec, zoom_percent, animations_enabled FROM settings LIMIT 1")
            row = cursor.fetchone()
            return row if row else (60, 100, 1)

    def update_settings(self, seconds, zoom_percent, animations_enabled=1):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE settings SET time_limit_sec = ?, zoom_percent = ?, animations_enabled = ? WHERE id = 1", 
                           (seconds, zoom_percent, animations_enabled))
            conn.commit()

    # Classes Management
    def get_classes(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM classes ORDER BY sort_order ASC, id ASC")
            return cursor.fetchall()

    def add_class(self, name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COALESCE(MAX(sort_order), 0) FROM classes")
                max_order = cursor.fetchone()[0]
                cursor.execute("INSERT INTO classes (name, sort_order) VALUES (?, ?)", (name.strip(), max_order + 10))
                conn.commit()
                return cursor.lastrowid, None
        except sqlite3.IntegrityError:
            return None, "Класс с таким названием уже существует!"

    def delete_class(self, class_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
            conn.commit()
    # Topics Management
    def get_topics(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, class_id FROM topics ORDER BY class_id ASC, sort_order ASC, id ASC")
            return cursor.fetchall()

    def get_topics_by_class(self, class_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM topics WHERE class_id = ? ORDER BY sort_order ASC, id ASC", (class_id,))
            return cursor.fetchall()

    def add_topic(self, name, class_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COALESCE(MAX(sort_order), 0) FROM topics WHERE class_id = ?", (class_id,))
                max_order = cursor.fetchone()[0]
                cursor.execute("INSERT INTO topics (name, class_id, sort_order) VALUES (?, ?, ?)", (name.strip(), class_id, max_order + 10))
                conn.commit()
                return cursor.lastrowid, None
        except sqlite3.IntegrityError:
            return None, "Тема с таким названием уже существует!" 
    # Questions
    def get_questions(self, topic_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, question_text, correct_answer, question_type, image_path FROM questions WHERE topic_id = ?", (topic_id,))
            return cursor.fetchall()

    def get_all_questions_by_class(self, class_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.id, q.question_text, q.correct_answer, q.question_type, q.image_path 
                FROM questions q 
                INNER JOIN topics t ON q.topic_id = t.id 
                WHERE t.class_id = ?
            """, (class_id,))
            return cursor.fetchall()

    # History & Leaderboards
    def get_history(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT topic_name, score, time_spent, date_time, student_name FROM history ORDER BY id DESC")
            return cursor.fetchall()

    def get_leaderboard(self, topic_name, time_limit=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if time_limit is not None and time_limit != "any":
                cursor.execute("SELECT student_name, score, time_spent, date_time FROM history WHERE topic_name = ? AND time_limit = ?", (topic_name, time_limit))
            else:
                cursor.execute("SELECT student_name, score, time_spent, date_time FROM history WHERE topic_name = ?", (topic_name,))
            records = cursor.fetchall()
            
        parsed_records = []
        for student, score, spent, date_time in records:
            numeric_score = 0
            try:
                if '/' in score:
                    numeric_score = int(score.split('/')[0])
                else:
                    numeric_score = int(score)
            except Exception:
                pass
            parsed_records.append((student, str(numeric_score), spent, date_time, numeric_score))
            
        parsed_records.sort(key=lambda x: (-x[4], x[2], x[3]))
        return [(r[0], r[1], r[2], r[3]) for r in parsed_records]

    def add_history(self, topic_name, score, time_spent, student_name, time_limit=60):
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO history (topic_name, score, time_spent, date_time, student_name, time_limit) VALUES (?, ?, ?, ?, ?, ?)",
                           (topic_name, score, time_spent, now_str, student_name, time_limit))
            conn.commit()

    def clear_history(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()

    # ==========================================
    # REWARD GIFS DATABASE MANAGEMENT METHODS
    # ==========================================
    def get_reward_gifs(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, event_type, gender, old_1, old_2, old_3 FROM reward_gifs ORDER BY id DESC")
            return cursor.fetchall()

    def add_reward_gif(self, filename, event_type, gender, old_1=0, old_2=0, old_3=0):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reward_gifs (filename, event_type, gender, old_1, old_2, old_3)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (filename.strip(), event_type, gender, old_1, old_2, old_3))
                conn.commit()
                return cursor.lastrowid, None
        except sqlite3.IntegrityError:
            return None, "Гифка с таким именем файла уже добавлена!"

    def update_reward_gif(self, gif_id, event_type, gender, old_1, old_2, old_3):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reward_gifs 
                SET event_type = ?, gender = ?, old_1 = ?, old_2 = ?, old_3 = ?
                WHERE id = ?
            """, (event_type, gender, old_1, old_2, old_3, gif_id))
            conn.commit()

    def delete_reward_gif(self, gif_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reward_gifs WHERE id = ?", (gif_id,))
            conn.commit()

    def get_yandex_token(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT yandex_token FROM settings LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else None

    def update_yandex_token(self, token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE settings SET yandex_token = ? WHERE id = 1", (token,))
            conn.commit()

    def get_last_auto_backup(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_auto_backup FROM settings LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else None

    def update_last_auto_backup(self, date_str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE settings SET last_auto_backup = ? WHERE id = 1", (date_str,))
            conn.commit()

    def add_question(self, topic_id, question_text, correct_answer, question_type='text', image_path=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO questions (topic_id, question_text, correct_answer, question_type, image_path)
                VALUES (?, ?, ?, ?, ?)
            """, (topic_id, question_text.strip(), correct_answer.strip(), question_type, image_path))
            conn.commit()

    def delete_question(self, question_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()

    def swap_class_order(self, class_id_1, class_id_2):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT sort_order FROM classes WHERE id = ?", (class_id_1,))
            order_1 = cursor.fetchone()[0]
            cursor.execute("SELECT sort_order FROM classes WHERE id = ?", (class_id_2,))
            order_2 = cursor.fetchone()[0]
            
            if order_1 == order_2:
                cursor.execute("SELECT id FROM classes ORDER BY id ASC")
                for idx, (cid,) in enumerate(cursor.fetchall()):
                    cursor.execute("UPDATE classes SET sort_order = ? WHERE id = ?", ((idx + 1) * 10, cid))
                cursor.execute("SELECT sort_order FROM classes WHERE id = ?", (class_id_1,))
                order_1 = cursor.fetchone()[0]
                cursor.execute("SELECT sort_order FROM classes WHERE id = ?", (class_id_2,))
                order_2 = cursor.fetchone()[0]
                
            cursor.execute("UPDATE classes SET sort_order = ? WHERE id = ?", (order_2, class_id_1))
            cursor.execute("UPDATE classes SET sort_order = ? WHERE id = ?", (order_1, class_id_2))
            conn.commit()

    def swap_topic_order(self, topic_id_1, topic_id_2):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT sort_order FROM topics WHERE id = ?", (topic_id_1,))
            order_1 = cursor.fetchone()[0]
            cursor.execute("SELECT sort_order FROM topics WHERE id = ?", (topic_id_2,))
            order_2 = cursor.fetchone()[0]
            
            if order_1 == order_2:
                cursor.execute("SELECT class_id FROM topics WHERE id = ?", (topic_id_1,))
                class_id = cursor.fetchone()[0]
                cursor.execute("SELECT id FROM topics WHERE class_id = ? ORDER BY id ASC", (class_id,))
                for idx, (tid,) in enumerate(cursor.fetchall()):
                    cursor.execute("UPDATE topics SET sort_order = ? WHERE id = ?", ((idx + 1) * 10, tid))
                cursor.execute("SELECT sort_order FROM topics WHERE id = ?", (topic_id_1,))
                order_1 = cursor.fetchone()[0]
                cursor.execute("SELECT sort_order FROM topics WHERE id = ?", (topic_id_2,))
                order_2 = cursor.fetchone()[0]
                
            cursor.execute("UPDATE topics SET sort_order = ? WHERE id = ?", (order_2, topic_id_1))
            cursor.execute("UPDATE topics SET sort_order = ? WHERE id = ?", (order_1, topic_id_2))
            conn.commit()


    def update_question(self, question_id, topic_id, question_text, correct_answer, question_type='text', image_path=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE questions 
                SET topic_id = ?, question_text = ?, correct_answer = ?, question_type = ?, image_path = ?
                WHERE id = ?
            """, (topic_id, question_text.strip(), correct_answer.strip(), question_type, image_path, question_id))
            conn.commit()

    def rename_class(self, class_id, new_name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE classes SET name = ? WHERE id = ?", (new_name.strip(), class_id))
                conn.commit()
                return True, None
        except sqlite3.IntegrityError:
            return False, "Класс с таким названием уже существует!"

    def rename_topic(self, topic_id, new_name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE topics SET name = ? WHERE id = ?", (new_name.strip(), topic_id))
                conn.commit()
                return True, None
        except sqlite3.IntegrityError:
            return False, "Тема с таким названием уже существует!" 
