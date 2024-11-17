import dash
from dash import html, dcc, Input, Output, State
import random
import pandas as pd
from datetime import datetime

# Initialize the app
app = dash.Dash(__name__)
app.title = "Math Training Program"

# External CSS (Bootstrap)
app.css.config.serve_locally = False
app.css.append_css({
    "external_url": "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
})

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

# Custom styles
custom_styles = {
    "container": {
        "maxWidth": "800px",
        "margin": "auto",
        "padding": "20px",
        "border": "1px solid #ddd",
        "borderRadius": "10px",
        "boxShadow": "0px 4px 6px rgba(0,0,0,0.1)",
        "backgroundColor": "#f9f9f9"
    },
    "header": {
        "textAlign": "center",
        "fontSize": "2rem",
        "marginBottom": "20px",
        "fontWeight": "bold",
        "color": "#333"
    },
    "button": {
        "margin": "10px",
        "padding": "10px 20px",
        "borderRadius": "5px",
        "backgroundColor": "#007bff",
        "color": "white",
        "border": "none",
        "cursor": "pointer"
    },
    "timer": {
        "textAlign": "center",
        "fontSize": "1.5rem",
        "marginBottom": "20px",
        "fontWeight": "bold",
        "color": "#ff5722"
    },
    "leaderboard": {
        "margin": "auto",
        "width": "100%",
        "border": "1px solid #ddd",
        "borderCollapse": "collapse",
        "marginTop": "20px"
    },
    "tableHeader": {
        "backgroundColor": "#007bff",
        "color": "white",
        "textAlign": "center",
        "fontWeight": "bold"
    },
    "tableRow": {
        "textAlign": "center"
    }
}

# App layout
app.layout = html.Div([
    html.Div(style=custom_styles["container"], children=[
        html.H1("Math Training Program", style=custom_styles["header"]),

        # Name input section
        html.Div(id="name-section", children=[
            html.Label("Enter your name:"),
            dcc.Input(id="name-input", type="text", placeholder="Your name", className="form-control", style={"width": "50%", "margin": "auto"}),
            html.Button("Start", id="start-btn", n_clicks=0, style=custom_styles["button"]),
            html.Div(id="name-feedback", style={"color": "red", "marginTop": "10px"})
        ], style={"textAlign": "center", "marginBottom": "20px"}),

        # Timer section
        html.Div(id="timer-section", style=custom_styles["timer"]),

        # Training section (hidden initially)
        html.Div(id="training-section", style={"display": "none"}, children=[
            html.H3(id="question", style={"textAlign": "center"}),
            html.Div([
                dcc.Input(id="answer-input", type="number", placeholder="Your answer", className="form-control", style={"marginRight": "10px", "width": "50%", "margin": "auto"}),
                html.Button("Submit", id="submit-btn", n_clicks=0, style=custom_styles["button"])
            ], style={"textAlign": "center", "marginBottom": "20px"}),
            html.Div(id="feedback", style={"textAlign": "center", "marginTop": "20px"}),
            html.Div(id="score", style={"textAlign": "center", "marginTop": "20px"}),
        ]),

        # Leaderboard section
        html.Div(id="leaderboard-section", children=[
            html.H2("Leaderboard", style={"textAlign": "center", "marginTop": "30px"}),
            html.Div(id="leaderboard", style={"textAlign": "center", "marginTop": "20px"})
        ]),

        # "Start New Session" button
        html.Div(id="new-session-section", children=[
            html.Button("Start New Session", id="new-session-btn", n_clicks=0, style=custom_styles["button"])
        ], style={"textAlign": "center", "marginTop": "20px"}),

        # Interval component for the timer
        dcc.Interval(id="timer-interval", interval=1000, n_intervals=0, disabled=True)
    ])
])

# Server-side variables to track state
questions = []
current_answer = 0
correct_count = 0
total_count = 0
time_left = total_time
timeout_occurred = False


def generate_leaderboard():
    """Generate a leaderboard showing the top 10 scores."""
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
                    html.Th("Rank", style=custom_styles["tableHeader"]),
                    html.Th("Name", style=custom_styles["tableHeader"]),
                    html.Th("Score", style=custom_styles["tableHeader"]),
                    html.Th("Date", style=custom_styles["tableHeader"])
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(rank + 1, style=custom_styles["tableRow"]),
                        html.Td(row["Name"], style=custom_styles["tableRow"]),
                        html.Td(row["Score"], style=custom_styles["tableRow"]),
                        html.Td(row["Date"].strftime('%Y-%m-%d') if not pd.isnull(row["Date"]) else "N/A", style=custom_styles["tableRow"])
                    ])
                    for rank, row in leaderboard_df.iterrows()
                ])
            ],
            style=custom_styles["leaderboard"]
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
