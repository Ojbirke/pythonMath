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
        f.write("Name,Date,Time,Session Status,Score,Total Questions\n")
except FileExistsError:
    pass

# Set the total time in seconds (5 minutes = 300 seconds)
total_time = 300

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

    # Timer section
    html.Div(id="timer-section", style={"textAlign": "center", "marginBottom": "20px", "fontSize": "20px"}),

    # Training section (hidden initially)
    html.Div(id="training-section", style={"display": "none"}, children=[
        html.H3(id="question", style={"textAlign": "center"}),
        html.Div([
            dcc.Input(id="answer-input", type="number", placeholder="Your answer", style={"marginRight": "10px"}, n_submit=0),
            html.Button("Submit", id="submit-btn", n_clicks=0)
        ], style={"textAlign": "center", "marginBottom": "20px"}),
        html.Div(id="feedback", style={"textAlign": "center", "marginTop": "20px"}),
        html.Div(id="score", style={"textAlign": "center", "marginTop": "20px"}),
    ]),

    # Leaderboard section
    html.Div(id="leaderboard-section", children=[
        html.H2("Leaderboard", style={"textAlign": "center"}),
        html.Div(id="leaderboard", style={"textAlign": "center", "marginTop": "20px"})
    ]),

    # "Start New Session" button
    html.Div(id="new-session-section", children=[
        html.Button("Start New Session", id="new-session-btn", n_clicks=0, style={"display": "none"})
    ], style={"textAlign": "center", "marginTop": "20px"}),

    # Interval component for the timer
    dcc.Interval(id="timer-interval", interval=1000, n_intervals=0, disabled=True)
])

# Server-side variables to track state
questions = []
current_answer = 0
correct_count = 0
total_count = 0
time_left = total_time
timeout_occurred = False


@app.callback(
    [Output("training-section", "style"),
     Output("name-section", "style"),
     Output("name-feedback", "children"),
     Output("timer-section", "children"),
     Output("timer-interval", "disabled"),
     Output("question", "children"),
     Output("feedback", "children"),
     Output("score", "children"),
     Output("leaderboard", "children"),
     Output("submit-btn", "disabled"),
     Output("new-session-btn", "style"),
     Output("answer-input", "value")],  # Clear input field
    [Input("start-btn", "n_clicks"),
     Input("submit-btn", "n_clicks"),
     Input("answer-input", "n_submit"),  # Add n_submit here
     Input("timer-interval", "n_intervals"),
     Input("new-session-btn", "n_clicks")],
    [State("name-input", "value"),
     State("answer-input", "value")]
)
def manage_quiz(start_clicks, submit_clicks, n_submit, n_intervals, new_session_clicks, name, user_answer):
    global questions, current_answer, correct_count, total_count, time_left, timeout_occurred

    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Handle "Start New Session" button click
    if triggered_id == "new-session-btn" and new_session_clicks > 0:
        return {"display": "none"}, {"display": "block"}, "", "", True, "", "", "", generate_leaderboard(), True, {"display": "none"}, None

    # Handle start button click
    if triggered_id == "start-btn" and start_clicks > 0:
        if not name:
            return {"display": "none"}, {"display": "block"}, "Please enter your name to start.", "", True, "", "", "", generate_leaderboard(), True, {"display": "none"}, None

        # Initialize quiz
        questions = [(x, y) for x in [6, 7, 8] for y in range(1, 11)]
        random.shuffle(questions)
        correct_count = 0
        total_count = 0
        time_left = total_time
        timeout_occurred = False
        question = questions.pop()
        current_answer = question[0] * question[1]
        return {"display": "block"}, {"display": "none"}, "", f"Time Left: {time_left // 60}:{time_left % 60:02d}", False, f"{question[0]} × {question[1]} = ?", "", "", generate_leaderboard(), False, {"display": "none"}, None

    # Handle timer updates
    if triggered_id == "timer-interval":
        if time_left > 0:
            time_left -= 1
            return {"display": "block"}, {"display": "none"}, "", f"Time Left: {time_left // 60}:{time_left % 60:02d}", False, dash.no_update, dash.no_update, f"Score: {correct_count}/{total_count}", generate_leaderboard(), False, {"display": "none"}, dash.no_update
        else:
            timeout_occurred = True
            return {"display": "block"}, {"display": "none"}, "", "Time is up! Quiz over!", True, "Time is up! Quiz over!", "You cannot submit answers anymore.", f"Final Score: {correct_count}/{total_count}", generate_leaderboard(), True, {"display": "block"}, dash.no_update

    # Handle question submission via button or Enter key
    if (triggered_id == "submit-btn" or triggered_id == "answer-input") and not timeout_occurred and total_count < 30:
        if user_answer is not None:
            total_count += 1
            if user_answer == current_answer:
                feedback = "Correct! 🎉"
                correct_count += 1
            else:
                feedback = f"Wrong. The correct answer was {current_answer}. 🙁"

            if total_count < 30:
                if questions:
                    question = questions.pop()
                    current_answer = question[0] * question[1]
                    return {"display": "block"}, {"display": "none"}, "", f"Time Left: {time_left // 60}:{time_left % 60:02d}", False, f"{question[0]} × {question[1]} = ?", feedback, f"Score: {correct_count}/{total_count}", generate_leaderboard(), False, {"display": "none"}, None
            else:
                # Log the total score to the CSV file at the end of the session
                now = datetime.now()
                try:
                    with open(results_file, "a") as f:
                        f.write(f"{name},{now.date()},{now.time().strftime('%H:%M:%S')},Session Completed,{correct_count},{total_count}\n")
                    print(f"Session logged for {name}: Score {correct_count}/{total_count}")
                except Exception as e:
                    print(f"Error logging session to CSV: {e}")

                return {"display": "block"}, {"display": "none"}, "", f"Time Left: {time_left // 60}:{time_left % 60:02d}", True, "No more questions. Quiz over!", feedback + " Quiz complete!", f"Final Score: {correct_count}/{total_count}", generate_leaderboard(), True, {"display": "block"}, None

    # Default return for timer updates without affecting input field or question
    return dash.no_update, dash.no_update, dash.no_update, f"Time Left: {time_left // 60}:{time_left % 60:02d}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, {"display": "none"}, dash.no_update

def generate_leaderboard():
    """Read the CSV file and generate a leaderboard."""
    try:
        # Read the results file
        df = pd.read_csv(results_file, encoding="latin-1", on_bad_lines="skip")

        # Clean and process the data
        df["Name"] = df["Name"].str.strip()  # Remove leading/trailing spaces
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # Convert dates to datetime format

        # Filter completed sessions
        leaderboard_df = df[df["Session Status"] == "Session Completed"]

        # Sort by Score (descending) and Date (most recent first)
        leaderboard_df = leaderboard_df.sort_values(
            by=["Score", "Date"], ascending=[False, True]
        ).reset_index(drop=True)

        # Limit to top 10 entries
        leaderboard_df = leaderboard_df.head(10)

        # Generate the table
        return html.Table(
            children=[
                html.Thead(html.Tr([
                    html.Th("Rank"),
                    html.Th("Name"),
                    html.Th("Score"),
                    html.Th("Total Questions"),
                    html.Th("Date")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(rank + 1),
                        html.Td(row["Name"]),
                        html.Td(row["Score"]),
                        html.Td(row["Total Questions"]),
                        html.Td(row["Date"].strftime('%Y-%m-%d') if not pd.isnull(row["Date"]) else "N/A")
                    ])
                    for rank, row in leaderboard_df.iterrows()
                ])
            ],
            style={
                "margin": "auto",
                "border": "1px solid black",
                "borderCollapse": "collapse",
                "width": "80%",
                "textAlign": "center"
            }
        )
    except pd.errors.EmptyDataError:
        return html.Div(
            "The leaderboard is empty. Play the quiz to add data!",
            style={"textAlign": "center", "color": "gray"}
        )
    except Exception as e:
        return html.Div(
            f"Error generating leaderboard: {e}",
            style={"textAlign": "center", "color": "red"}
        )


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)