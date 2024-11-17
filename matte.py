
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
try:
    with open(results_file, "x") as f:
        f.write("Name,Date,Time,Session Status,Score,Total Questions\n")
except FileExistsError:
    pass

# Set the total time in seconds (5 minutes = 300 seconds)
total_time = 300

# Server-side variables
questions = []
current_answer = 0
correct_count = 0
total_count = 0
time_left = total_time
timeout_occurred = False

# App layout
app.layout = html.Div(style={
    "maxWidth": "800px",
    "margin": "auto",
    "padding": "20px",
    "fontFamily": "Arial, sans-serif",
    "border": "1px solid #ddd",
    "borderRadius": "10px",
    "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)",
    "backgroundColor": "#f9f9f9",
}, children=[
    html.H1("Math Training Program", style={
        "textAlign": "center",
        "fontSize": "2.5rem",
        "color": "#333",
        "marginBottom": "20px",
    }),

    # Name input section
    html.Div(id="name-section", children=[
        html.Label("Enter your name:", style={"fontSize": "1.2rem"}),
        dcc.Input(id="name-input", type="text", placeholder="Your name", style={
            "width": "100%",
            "padding": "10px",
            "marginBottom": "10px",
            "borderRadius": "5px",
            "border": "1px solid #ccc",
        }),
        html.Button("Start", id="start-btn", n_clicks=0, style={
            "padding": "10px 20px",
            "backgroundColor": "#007bff",
            "color": "white",
            "border": "none",
            "borderRadius": "5px",
            "cursor": "pointer",
        }),
        html.Div(id="name-feedback", style={"color": "red", "marginTop": "10px"})
    ], style={"marginBottom": "20px"}),

    # Timer section
    html.Div(id="timer-section", style={
        "textAlign": "center",
        "marginBottom": "20px",
        "fontSize": "1.5rem",
        "color": "#ff5722",
        "fontWeight": "bold",
    }),

    # Training section
    html.Div(id="training-section", style={"display": "none"}, children=[
        html.H3(id="question", style={"textAlign": "center", "fontSize": "1.8rem", "marginBottom": "20px"}),
        html.Div([
            dcc.Input(id="answer-input", type="number", placeholder="Your answer", style={
                "width": "calc(70% - 20px)",
                "padding": "10px",
                "borderRadius": "5px",
                "border": "1px solid #ccc",
                "marginRight": "10px",
            }),
            html.Button("Submit", id="submit-btn", n_clicks=0, style={
                "padding": "10px 20px",
                "backgroundColor": "#007bff",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "cursor": "pointer",
            })
        ], style={"textAlign": "center", "marginBottom": "20px"}),
        html.Div(id="feedback", style={"textAlign": "center", "marginTop": "20px", "fontSize": "1.2rem", "color": "#333"}),
        html.Div(id="score", style={"textAlign": "center", "marginTop": "20px", "fontSize": "1.2rem", "color": "#555"}),
    ]),

    # Leaderboard section
    html.Div(id="leaderboard-section", children=[
        html.H2("Leaderboard", style={
            "textAlign": "center",
            "fontSize": "2rem",
            "color": "#333",
            "marginBottom": "20px",
        }),
        html.Div(id="leaderboard", style={"margin": "auto", "width": "100%"})
    ]),

    # "Start New Session" button
    html.Div(id="new-session-section", children=[
        html.Button("Start New Session", id="new-session-btn", n_clicks=0, style={
            "display": "none",
            "padding": "10px 20px",
            "backgroundColor": "#007bff",
            "color": "white",
            "border": "none",
            "borderRadius": "5px",
            "cursor": "pointer",
        })
    ], style={"textAlign": "center", "marginTop": "20px"}),

    # Timer interval
    dcc.Interval(id="timer-interval", interval=1000, n_intervals=0, disabled=True)
])


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
     Output("answer-input", "value")],
    [Input("start-btn", "n_clicks"),
     Input("submit-btn", "n_clicks"),
     Input("answer-input", "n_submit"),
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
        if not name or name.strip() == "":
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
        return {"display": "block"}, {"display": "none"}, "", f"Time Left: {time_left // 60}:{time_left % 60:02d}", False, f"{question[0]} × {question[1]} =", "", "", generate_leaderboard(), False, {"display": "none"}, None

    # Handle timer updates
    if triggered_id == "timer-interval":
        if time_left > 0:
            time_left -= 1
            return dash.no_update, dash.no_update, dash.no_update, f"Time Left: {time_left // 60}:{time_left % 60:02d}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            timeout_occurred = True
            return (
                {"display": "none"}, {"display": "block"}, "Time is up!", "Time is up!", True,
                dash.no_update, "Time is up! Session over.", f"Final Score: {correct_count}/{total_count}",
                generate_leaderboard(), True, {"display": "block"}, None
            )

    # Handle question submission
    if (triggered_id == "submit-btn" or triggered_id == "answer-input") and not timeout_occurred:
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
                    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"{question[0]} × {question[1]} =", feedback, f"Score: {correct_count}/{total_count}", generate_leaderboard(), dash.no_update, {"display": "none"}, None
            else:
                # End of session
                now = datetime.now()
                try:
                    with open(results_file, "a") as f:
                        f.write(f"{name},{now.date()},{now.time().strftime('%H:%M:%S')},Session Completed,{correct_count},{total_count}\n")
                except Exception as e:
                    print(f"Error saving session data: {e}")

                # Ensure all 12 outputs are returned
                return (
                    {"display": "none"},  # Hide training-section
                    {"display": "block"},  # Show name-section
                    "Session Completed! 🎉",  # name-feedback
                    f"Time Left: {time_left // 60}:{time_left % 60:02d}",  # timer-section
                    True,  # Disable timer
                    "No more questions. Quiz over!",  # question
                    f"Final Score: {correct_count}/{total_count}",  # feedback
                    f"Final Score: {correct_count}/{total_count}",  # score
                    generate_leaderboard(),  # leaderboard
                    True,  # Disable submit button
                    {"display": "block"},  # Show new-session-btn
                    None  # Clear answer-input
                )

    # Default return for no-update cases
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


def generate_leaderboard():
    """Generate a styled leaderboard."""
    try:
        df = pd.read_csv(results_file, encoding="latin-1", on_bad_lines="skip")
        df["Name"] = df["Name"].str.strip()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        leaderboard_df = df[df["Session Status"] == "Session Completed"]
        leaderboard_df = leaderboard_df.sort_values(by=["Score", "Date"], ascending=[False, True]).reset_index(drop=True).head(10)
        return html.Table(
            children=[
                html.Thead(html.Tr([
                    html.Th("Rank", style={"padding": "10px", "backgroundColor": "#007bff", "color": "white", "textAlign": "center"}),
                    html.Th("Name", style={"padding": "10px", "backgroundColor": "#007bff", "color": "white", "textAlign": "center"}),
                    html.Th("Score", style={"padding": "10px", "backgroundColor": "#007bff", "color": "white", "textAlign": "center"}),
                    html.Th("Total Questions", style={"padding": "10px", "backgroundColor": "#007bff", "color": "white", "textAlign": "center"}),
                    html.Th("Date", style={"padding": "10px", "backgroundColor": "#007bff", "color": "white", "textAlign": "center"})
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(rank + 1, style={"padding": "10px", "textAlign": "center"}),
                        html.Td(row["Name"], style={"padding": "10px", "textAlign": "center"}),
                        html.Td(row["Score"], style={"padding": "10px", "textAlign": "center"}),
                        html.Td(row["Total Questions"], style={"padding": "10px", "textAlign": "center"}),
                        html.Td(row["Date"].strftime('%Y-%m-%d') if not pd.isnull(row["Date"]) else "N/A", style={"padding": "10px", "textAlign": "center"})
                    ]) for rank, row in leaderboard_df.iterrows()
                ])
            ],
            style={
                "width": "100%",
                "border": "1px solid #ddd",
                "borderCollapse": "collapse",
                "textAlign": "center",
                "marginTop": "20px",
                "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)"
            }
        )
    except pd.errors.EmptyDataError:
        return html.Div(
            "The leaderboard is empty. Play the quiz to add data!",
            style={"textAlign": "center", "color": "gray", "fontSize": "1.2rem", "marginTop": "20px"}
        )
    except Exception as e:
        return html.Div(
            f"Error generating leaderboard: {e}",
            style={"textAlign": "center", "color": "red", "fontSize": "1.2rem", "marginTop": "20px"}
        )


if __name__ == "__main__":
    app.run_server(debug=True)

