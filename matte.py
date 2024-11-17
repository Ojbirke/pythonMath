import dash
from dash import html, dcc, Input, Output, State
import random
import pandas as pd
from datetime import datetime

# Initialize the app
app = dash.Dash(__name__)
app.title = "Math Training Program"

# Initialize the CSV file
results_file = "math_results.csv"
# Create the file with headers if it doesn't exist
try:
    with open(results_file, "x") as f:
        f.write("Name,Date,Time,Question,Correct Answer,User Answer,Result\n")
except FileExistsError:
    pass

# App layout
app.layout = html.Div([
    html.H1("Math Training Program", style={"textAlign": "center"}),

    # Name input section
    html.Div(id="name-section", children=[
        html.Label("Enter your name:"),
        dcc.Input(id="name-input", type="text", placeholder="Your name", style={"width": "50%"}),
        html.Button("Start", id="start-btn", n_clicks=0),
        html.Div(id="name-feedback", style={"color": "red", "marginTop": "10px"})
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Training section (hidden initially)
    html.Div(id="training-section", style={"display": "none"}, children=[
        html.H3(id="question", style={"textAlign": "center"}),
        html.Div([
            dcc.Input(id="answer-input", type="number", placeholder="Your answer", style={"marginRight": "10px"}),
            html.Button("Submit", id="submit-btn", n_clicks=0)
        ], style={"textAlign": "center", "marginBottom": "20px"}),
        html.Div(id="feedback", style={"textAlign": "center", "marginTop": "20px"}),
        html.Div(id="score", style={"textAlign": "center", "marginTop": "20px"}),
    ])
])

# Server-side variables to track state
questions = []
current_answer = 0
correct_count = 0
total_count = 0


# Single callback for handling the entire quiz logic
@app.callback(
    [Output("training-section", "style"),
     Output("question", "children"),
     Output("name-section", "style"),
     Output("name-feedback", "children"),
     Output("feedback", "children"),
     Output("score", "children")],
    [Input("start-btn", "n_clicks"),
     Input("submit-btn", "n_clicks")],
    [State("name-input", "value"),
     State("answer-input", "value")]
)
def manage_quiz(start_clicks, submit_clicks, name, user_answer):
    global questions, current_answer, correct_count, total_count

    # Check which button triggered the callback
    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    # Handle "Start" button click
    if triggered_id == "start-btn":
        if not name:
            return {"display": "none"}, "", {"display": "block"}, "Please enter your name to start.", "", ""
        # Initialize the quiz
        questions = [(x, y) for x in [6, 7, 8] for y in range(1, 11)]
        random.shuffle(questions)
        correct_count = 0
        total_count = 0
        question = questions.pop()
        current_answer = question[0] * question[1]
        return {"display": "block"}, f"{question[0]} × {question[1]} = ?", {"display": "none"}, "", "", ""

    # Handle "Submit" button click
    elif triggered_id == "submit-btn":
        if user_answer is not None:
            total_count += 1
            if user_answer == current_answer:
                feedback = "Correct! 🎉"
                correct_count += 1
                result = "Correct"
            else:
                feedback = f"Wrong. The correct answer was {current_answer}. 🙁"
                result = "Wrong"

            # Save the result to CSV
            now = datetime.now()
            question_text = f"{current_answer // user_answer} × {user_answer}" if result == "Wrong" else f"{current_answer // 1} × {1}"
            with open(results_file, "a") as f:
                f.write(f"{name},{now.date()},{now.time().strftime('%H:%M:%S')},{current_answer // 1} × {1},{current_answer},{user_answer},{result}\n")

            # Generate the next question
            if questions:
                question = questions.pop()
                current_answer = question[0] * question[1]
                return {"display": "block"}, f"{question[0]} × {question[1]} = ?", {"display": "none"}, "", feedback, f"Score: {correct_count}/{total_count}"
            else:
                return {"display": "none"}, "No more questions. Quiz over!", {"display": "none"}, "", feedback + " Quiz over!", f"Final Score: {correct_count}/{total_count}"

    # Default state
    return {"display": "none"}, "", {"display": "block"}, "", "", ""


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
