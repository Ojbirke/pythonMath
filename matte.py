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
        f.write("Name,Date,Time,Question,Correct Answer,User Answer,Result,Score\n")
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
    ]),

    # Leaderboard section
    html.Div(id="leaderboard-section", children=[
        html.H2("Leaderboard", style={"textAlign": "center"}),
        html.Div(id="leaderboard", style={"textAlign": "center", "marginTop": "20px"})
    ])
])

# Server-side variables to track state
questions = []
current_answer = 0
correct_count = 0
total_count = 0


# Callback for handling quiz logic
@app.callback(
    [Output("training-section", "style"),
     Output("question", "children"),
     Output("name-section", "style"),
     Output("name-feedback", "children"),
     Output("feedback", "children"),
     Output("score", "children"),
     Output("leaderboard", "children"),
     Output("answer-input", "value")],  # Clear the input field
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
            return {"display": "none"}, "", {"display": "block"}, "Please enter your name to start.", "", "", "", None
        # Initialize the quiz
        questions = [(x, y) for x in [6, 7, 8] for y in range(1, 11)]
        random.shuffle(questions)
        correct_count = 0
        total_count = 0
        question = questions.pop()
        current_answer = question[0] * question[1]
        return {"display": "block"}, f"{question[0]} × {question[1]} = ?", {"display": "none"}, "", "", "", generate_leaderboard(), None

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

            # Save each question result to CSV
            now = datetime.now()
            with open(results_file, "a") as f:
                f.write(f"{name},{now.date()},{now.time().strftime('%H:%M:%S')},{current_answer // user_answer if user_answer else 0} × {user_answer if user_answer else 0},{current_answer},{user_answer},{result},\n")

            # Generate the next question
            if questions:
                question = questions.pop()
                current_answer = question[0] * question[1]
                return {"display": "block"}, f"{question[0]} × {question[1]} = ?", {"display": "none"}, "", feedback, f"Score: {correct_count}/{total_count}", generate_leaderboard(), None
            else:
                # Add the total score at the end of the quiz
                with open(results_file, "a") as f:
                    f.write(f"{name},{now.date()},{now.time().strftime('%H:%M:%S')},,,,Final Score,{correct_count}\n")
                return {"display": "none"}, "No more questions. Quiz over!", {"display": "none"}, "", feedback + " Quiz over!", f"Final Score: {correct_count}/{total_count}", generate_leaderboard(), None

    # Default state
    return {"display": "none"}, "", {"display": "block"}, "", "", "", generate_leaderboard(), None


def generate_leaderboard():
    """Read the CSV file and generate a leaderboard."""
    try:
        # Read the CSV file
        df = pd.read_csv(results_file, encoding="latin-1", on_bad_lines="skip")
        
        # Ensure the required columns exist
        required_columns = {"Name", "Date", "Score"}
        if not required_columns.issubset(df.columns):
            missing_cols = required_columns - set(df.columns)
            return html.Div(f"Missing columns in CSV: {', '.join(missing_cols)}", style={"textAlign": "center", "color": "red"})
        
        # Fill missing values in 'Score' and 'Date' columns
        df["Score"] = pd.to_numeric(df["Score"], errors="coerce").fillna(0).astype(int)
        df["Date"] = df["Date"].fillna("Unknown")
        
        # Group by name, sort by highest score, and pick the latest date for tie-breaking
        leaderboard_df = (
            df.groupby("Name", as_index=False)
            .agg({"Score": "max", "Date": "max"})
            .sort_values("Score", ascending=False)
            .reset_index(drop=True)
        )
        
        # Create HTML table for the leaderboard
        leaderboard_html = html.Table([
            html.Thead(html.Tr([html.Th("Rank"), html.Th("Name"), html.Th("Score"), html.Th("Date")])),
            html.Tbody([
                html.Tr([html.Td(rank + 1), html.Td(row["Name"]), html.Td(row["Score"]), html.Td(row["Date"])])
                for rank, row in leaderboard_df.iterrows()
            ])
        ])
        return leaderboard_html
    except pd.errors.EmptyDataError:
        return html.Div("The leaderboard is empty. Play the quiz to add data!", style={"textAlign": "center", "color": "gray"})
    except Exception as e:
        return html.Div(f"Error generating leaderboard: {e}", style={"textAlign": "center", "color": "red"})


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

