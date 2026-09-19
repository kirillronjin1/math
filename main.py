from flask import Flask, render_template, request, Response
import sqlite3

app = Flask(__name__)
DB_NAME = "school_quiz.db"

# Простой пароль для админки (поменяй на свой)
ADMIN_PASSWORD = "1"


def get_questions():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    questions = []
    for row in cursor.execute("SELECT * FROM questions ORDER BY id").fetchall():
        q_id = row["id"]
        options = [
            r["text"]
            for r in cursor.execute(
                "SELECT text FROM options WHERE question_id = ? ORDER BY id", (q_id,)
            ).fetchall()
        ]
        questions.append({
            "id": q_id,
            "question": row["question"],
            "options": options,
            "correct": row["correct"]
        })

    conn.close()
    return questions


@app.route("/", methods=["GET", "POST"])
def index():
    questions = get_questions()

    if request.method == "POST":
        score = 0
        answers = {}
        negations = {}

        # Собираем ответы и отрицания
        for q in questions:
            answer = request.form.get(f"q{q['id']}")
            negation = request.form.get(f"negation{q['id']}", "").strip()
            answers[q["id"]] = answer
            negations[q["id"]] = negation

            if answer == q["correct"]:
                score += 1

        # Сохраняем в базу
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        for q in questions:
            cursor.execute(
                "INSERT INTO submissions (question_id, selected_option, negation_text) VALUES (?, ?, ?)",
                (q["id"], answers.get(q["id"]), negations.get(q["id"]))
            )
        conn.commit()
        conn.close()

        correct_map = {q["id"]: q["correct"] for q in questions}
        return render_template(
            "index.html",
            questions=questions,
            score=score,
            total=len(questions),
            answers=answers,
            negations=negations,
            correct_map=correct_map
        )

    return render_template(
        "index.html",
        questions=questions,
        score=None,
        total=len(questions),
        answers={},
        negations={},
        correct_map={}
    )


@app.route("/admin")
def admin():
    password = request.args.get("password", "")
    if password != ADMIN_PASSWORD:
        return "Доступ запрещён. Укажите ?password=...", 403

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT s.id, s.question_id, q.question, s.selected_option,
               q.correct, s.negation_text, s.submitted_at
        FROM submissions s
        JOIN questions q ON s.question_id = q.id
        ORDER BY s.submitted_at DESC
    """).fetchall()

    conn.close()
    return render_template("admin.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
