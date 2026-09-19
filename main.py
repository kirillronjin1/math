from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DB_NAME = "school_quiz.db"


def get_questions():
    """Достаёт все вопросы и варианты ответов из базы."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    questions = []
    for row in cursor.execute("SELECT * FROM questions").fetchall():
        q_id = row["id"]
        options = [
            r["text"]
            for r in cursor.execute(
                "SELECT text FROM options WHERE question_id = ?", (q_id,)
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
        for q in questions:
            answer = request.form.get(f"q{q['id']}")
            answers[q["id"]] = answer
            if answer == q["correct"]:
                score += 1

        # Передаём correct_answers, чтобы подсветить в шаблоне
        correct_map = {q["id"]: q["correct"] for q in questions}
        return render_template(
            "index.html",
            questions=questions,
            score=score,
            total=len(questions),
            answers=answers,
            correct_map=correct_map
        )

    return render_template(
        "index.html",
        questions=questions,
        score=None,
        total=len(questions),
        answers={},
        correct_map={}
    )


if __name__ == "__main__":
    app.run(debug=True)
