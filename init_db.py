import sqlite3

def init_db():
    conn = sqlite3.connect("school_quiz.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            correct TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)

    # Очищаем старые данные (на случай повторного запуска)
    cursor.execute("DELETE FROM options")
    cursor.execute("DELETE FROM questions")

    questions = [
        {
            "question": "Сколько будет 7 × 8?",
            "options": ["48", "54", "56", "63"],
            "correct": "56"
        },
        {
            "question": "Какая столица Франции?",
            "options": ["Берлин", "Мадрид", "Париж", "Рим"],
            "correct": "Париж"
        },
        {
            "question": "Какой газ выделяют растения в процессе фотосинтеза?",
            "options": ["Азот", "Кислород", "Углекислый газ", "Водород"],
            "correct": "Кислород"
        },
        {
            "question": "Кто написал «Войну и мир»?",
            "options": ["Достоевский", "Толстой", "Чехов", "Пушкин"],
            "correct": "Толстой"
        },
        {
            "question": "Чему равна сумма углов треугольника?",
            "options": ["90°", "180°", "270°", "360°"],
            "correct": "180°"
        }
    ]

    for q in questions:
        cursor.execute(
            "INSERT INTO questions (question, correct) VALUES (?, ?)",
            (q["question"], q["correct"])
        )
        question_id = cursor.lastrowid
        for option in q["options"]:
            cursor.execute(
                "INSERT INTO options (question_id, text) VALUES (?, ?)",
                (question_id, option)
            )

    conn.commit()
    conn.close()
    print("База данных создана, вопросы добавлены!")

if __name__ == "__main__":
    init_db()
