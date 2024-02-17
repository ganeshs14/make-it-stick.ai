from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Sample quiz questions
questions = [
    {
        'question': 'What is the capital of France?',
        'correct_answer': 'Paris'
    },
    {
        'question': 'What is 2 + 2?',
        'correct_answer': '4'
    }
]

def is_valid_answer(answer, correct_answer):
    return answer and answer.strip().lower() == correct_answer.lower()

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'current_question_index' not in session:
        session['current_question_index'] = 0
        session['score'] = 0

    if request.method == 'POST':
        answered = request.form.get('answer')
        correct_answer = questions[session['current_question_index']]['correct_answer']

        if not answered:
            error = "Please provide an answer."
        elif not is_valid_answer(answered, correct_answer):
            error = "Wrong answer. The correct answer is: {}".format(correct_answer)
        else:
            session['score'] += 1
            session['current_question_index'] += 1

            if session['current_question_index'] < len(questions):
                return redirect(url_for('quiz'))
            else:
                score = session['score']
                total_questions = len(questions)
                session.clear()
                return f'Quiz completed! Your score is {score}/{total_questions}'
        
        return render_template('quiz.html', question=questions[session['current_question_index']], empty_error=error if not answered else None, wrong_answer_error=error if answered else None)

    if session['current_question_index'] < len(questions):
        question = questions[session['current_question_index']]
        return render_template('quiz.html', question=question)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
