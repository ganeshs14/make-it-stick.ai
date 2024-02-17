from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import pdfplumber
import json
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

GOOGLE_API_KEY = 'AIzaSyD2_BY1YIYvhxEw7lMk0XuDzA3pwHV4nYU'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        text = ''
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        session['extracted_text'] = text
        session['current_question_index'] = 0
        
        # Generate questions and answers from extracted text
        prompt = f"""generate 2 question and there answers in json format from the given context delimited by triple backtick ```{text}```"""
        response = model.generate_content(prompt)
        response_json = json.loads(response.text.split("```")[1][4:])
        print(response_json)
        questions_answers = response_json["questions"]
        session['questions_answers'] = questions_answers

        return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    wrongAns = []
    if 'current_question_index' not in session or 'questions_answers' not in session:
        return redirect(url_for('index'))

    questions_answers = session['questions_answers']

    def generate_summary(wrongAns):
        response = model.generate_content(f"provided list of answers user got wrong delimided by tripple backtik generate a summary for the user about  ```{wrongAns}``` only generate a summary in normal words don't use any special characters or numbers. and also use provide proper feed back on the topics that user needs to study again")
        return response.text
    
    def check_answer(question, answer, correct_answer):
        response = model.generate_content(f"given the system question, system answer and the user answer provided by the user if the user answer is similar to system answer return true else return false give only one word output system question={question}, system answer={correct_answer}, user answer={answer} ")
        print(response.text)
        if response.text == "true" or response.text == "True" or response.text == "TRUE":
            return False
        return True

    if request.method == 'POST':
        answered = request.form.get('answer')
        question = questions_answers[session['current_question_index']]['question']
        correct_answer = questions_answers[session['current_question_index']]['answer']

        if not answered:
            error = "Please provide an answer."
        elif check_answer(question, answered, correct_answer):
            
            error = "Wrong answer. The correct answer is: {}".format(correct_answer)
            wrongAns.append(questions_answers[session['current_question_index']]['answer'])
        else:
            session['current_question_index'] += 1

            if session['current_question_index'] < len(questions_answers):
                return redirect(url_for('quiz'))
            else:
                session.clear()
                return render_template('quiz_completed.html', summ=generate_summary(wrongAns))
        
        return render_template('quiz.html', question=questions_answers[session['current_question_index']]['question'], empty_error=error if not answered else None, wrong_answer_error=error if answered else None)

    if session['current_question_index'] < len(questions_answers):
        question = questions_answers[session['current_question_index']]['question']
        return render_template('quiz.html', question=question)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

