from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config ['SECRET_KEY'] = "never-tell!"
app.config ['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

current_survey_key = 'current_survey'
responses_key = 'responses'

@app.route("/")
def show_pick_survey_form():
    return render_template("pick-survey.html", survey=surveys)

@app.route("/", methods=["POST"])
def pick_survey():
    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")
    
    survey = surveys[survey_id]
    session[current_survey_key] = survey_id

    return render_template("survey_start.html", surveys=survey)

@app.route("/begin", methods=["POST"])
def start_survey():
    session[responses_key] = []

    return redirect("/questions/0")

@app.route("/answer", methods=["POST"])
def handle_question():
    choice = request.form['answer']
    text = request.form.get("text", "")

    responses = session[responses_key]
    responses.append({"choice": choice, "tetx": text})

    session[responses_key] = responses
    survey_code = session[current_survey_key]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        return redirect("/completed")
    
    else:
        return redirect(f"/questions/{len(responses)}")
    
    @app.route("/questions/<int:qid>")
    def show_question(qid):
        responses = session.get(responses_key)
        survey_code = session[current_survey_key]
        survey = surveys[survey_code]

        if (responses is None):
            return redirect("/")
        
        if (len(responses) == len(survey.questions)):
            return redirect("/completed")
        
        if (len(responses) != qid):
            flash(f"Invalid question ID: {qid}.")
            return redirect(f"/questions/{len(responses)}")
        
        question = survey.quesions[qid]

        return render_template(
            "question.html", question_num=qid, question=question)
    
    @app.route("/complete")
    def say_thanks():
        survey_id = session[current_survey_key]
        survey = surveys[survey_id]
        responses = session[responses_key]

        html = render_template("completion.html",
                               survey=survey,
                               responses=responses)
        
        response = make_response(html)
        response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
        return response
    