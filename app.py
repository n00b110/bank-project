from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
import dash
from dash import dcc, html
import plotly.graph_objs as go

app = Flask(__name__)
# Secret key for session encryption
app.secret_key = "budgeting101"
# Lifetime of the permenent session
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/', methods=["POST","GET"])
def index():
    # Login
    if request.method == "POST":
        session.permanent = True
        user = request.form["emailName"]
        session["user"] = user
        return redirect(url_for("dashboard"))
    else:
        if "user" in session:
            return redirect(url_for('dashboard'))
        return render_template("index.html")

@app.route('/dashboard/')
def dashboard():
    if "user" in session:
        user = session["user"]
        return render_template("dashboard.html", )
    else:
        return redirect(url_for("index"))

@app.route('/budget/')
def budget():
    if "user" in session:
        user = session["user"]
        return render_template("budget.html")
    else:
        return redirect(url_for("index"))

@app.route('/goals/')
def goals():
    if "user" in session:
        user = session["user"]
        return render_template('goals.html')
    else:
        return redirect(url_for("index"))

@app.route('/settings/')
def settings():
    if "user" in session:
        user = session["user"]
        return render_template('settings.html')
    else:
        return redirect(url_for("index"))

# @app.route('/test/')
# def test():
#     if "user" in session:
#         user = session["user"]
#         return f"<h1>{user}</h1>"
#     else:
#         return redirect(url_for("index"))
    
@app.route("/forgotpassword/")
def fPassword():
    return render_template('fPassword.html')

@app.route("/login/")
def login():
    if "user" in session:
        user = session["user"]
        return render_template('login.html')
    else:
        return redirect("index")

@app.route("/logout/")
def logout():
    if "user" in session:
        user = session["user"]
    session.pop("user", None)
    return redirect(url_for("index"))

recent_month_pie_chart = dash.Dash(__name__, server=app, url_base_pathname='/rmpc/')

rmpc_labels = ['Needs', 'Wants', 'Savings']
rmpc_values = [50, 30, 20]

formatted_rmpc_values = ['${:,.2f}'.format(value) for value in rmpc_values]

recent_month_pie_chart.layout = html.Div(children=[
    dcc.Graph(
        id='pie-chart',
        figure={
            'data': [go.Pie(
                labels=rmpc_labels,
                values=rmpc_values,
                textinfo='label+percent',
                hoverinfo='label+text',
                text=formatted_rmpc_values
                )],
            'layout': go.Layout(
                title='Your Most Recent Month',
                paper_bgcolor='rgb(174, 203, 157)')
        },
        config={'displaylogo': False}
    )
])

last_quarter_pie_chart = dash.Dash(__name__, server=app, url_base_pathname='/lqpc/')

lqpc_labels = ['Needs', 'Wants', 'Savings']
lqpc_values = [80, 10, 10]

formatted_lqpc_values = ['${:,.2f}'.format(value) for value in lqpc_values]

last_quarter_pie_chart.layout = html.Div(children=[
    dcc.Graph(
        id='pie-chart',
        figure={
            'data': [go.Pie(
                labels=lqpc_labels,
                values=lqpc_values,
                textinfo='label+percent',
                hoverinfo='label+text',
                text=formatted_lqpc_values
                )],
            'layout': go.Layout(
                title='Your Last Quarter',
                paper_bgcolor='rgb(174, 203, 157)')
        },
        config={'displaylogo': False}
    )
])

last_year_pie_chart = dash.Dash(__name__, server=app, url_base_pathname='/lypc/')

lypc_labels = ['Needs', 'Wants', 'Savings']
lypc_values = [80, 10, 10]

formatted_lypc_values = ['${:,.2f}'.format(value) for value in lypc_values]

last_year_pie_chart.layout = html.Div(children=[
    dcc.Graph(
        id='pie-chart',
        figure={
            'data': [go.Pie(
                labels=lypc_labels,
                values=lypc_values,
                textinfo='label+percent',
                hoverinfo='label+text',
                text=formatted_lypc_values
                )],
            'layout': go.Layout(
                title='Your Last Year',
                paper_bgcolor='rgb(174, 203, 157)')
        },
        config={'displaylogo': False}
    )
])

life_time_pie_chart = dash.Dash(__name__, server=app, url_base_pathname='/ltpc/')

ltpc_labels = ['Needs', 'Wants', 'Savings']
ltpc_values = [80, 10, 10]

formatted_ltpc_values = ['${:,.2f}'.format(value) for value in ltpc_values]

life_time_pie_chart.layout = html.Div(children=[
    dcc.Graph(
        id='pie-chart',
        figure={
            'data': [go.Pie(
                labels=ltpc_labels,
                values=ltpc_values,
                textinfo='label+percent',
                hoverinfo='label+text',
                text=formatted_ltpc_values
                )],
            'layout': go.Layout(
                title='Your Lifetime Budgeting',
                paper_bgcolor='rgb(174, 203, 157)')
        },
        config={'displaylogo': False}
    )
])

# Create a Dash app
goals_line_graph = dash.Dash(__name__, server=app, url_base_pathname='/line_graph/')

# Sample data for the line graph
x_data = ["January", "February", "March", "April", "May"]
needs_baseline = [50, 50, 50, 50, 50]
wants_baseline = [30, 30, 30, 30, 30]
savings_baseline = [20, 20, 20, 20, 20]
needs_actual = [60, 55, 65, 50, 55]
wants_actual = [30, 45, 20, 45, 25]
savings_actual = [10, 0, 15, 5, 20]

formatted_needs_baseline_values = ['${:,.2f}'.format(value) for value in needs_baseline]
formatted_wants_baseline_values = ['${:,.2f}'.format(value) for value in wants_baseline]
formatted_savings_baseline_values = ['${:,.2f}'.format(value) for value in savings_baseline]
formatted_needs_actual_values = ['${:,.2f}'.format(value) for value in needs_actual]
formatted_wants_actual_values = ['${:,.2f}'.format(value) for value in wants_actual]
formatted_savings_actual_values = ['${:,.2f}'.format(value) for value in savings_actual]

# Define layout of the app
goals_line_graph.layout = html.Div(children=[
    dcc.Graph(
        id='line-graph',
        figure={
            'data': [
                go.Scatter(
                    x=x_data,
                    y=needs_baseline,
                    mode='lines+markers',
                    marker=dict(color='#ADD8E6'),
                    name='Needs Goal',
                    hoverinfo= 'x+text',
                    text= formatted_needs_baseline_values
                ),
                go.Scatter(
                    x=x_data,
                    y=wants_baseline,
                    mode='lines+markers',
                    marker=dict(color='#FFDAB9'),
                    name='Wants Goal',
                    hoverinfo= 'x+text',
                    text= formatted_wants_baseline_values
                ),
                go.Scatter(
                    x=x_data,
                    y=savings_baseline,
                    mode='lines+markers',
                    marker=dict(color='#C1FFC1'),
                    name='Savings Goal',
                    hoverinfo= 'x+text',
                    text= formatted_savings_baseline_values
                ),
                go.Scatter(
                    x=x_data,
                    y=needs_actual,
                    mode='lines+markers',
                    marker=dict(color='blue'),
                    name='Actual Needs Spending',
                    hoverinfo= 'x+text',
                    text= formatted_needs_actual_values
                ),
                go.Scatter(
                    x=x_data,
                    y=wants_actual,
                    mode='lines+markers',
                    marker=dict(color='orange'),
                    name='Actual Wants Spending',
                    hoverinfo= 'x+text',
                    text= formatted_wants_actual_values
                ),
                go.Scatter(
                    x=x_data,
                    y=savings_actual,
                    mode='lines+markers',
                    marker=dict(color='#00DF00'),
                    name='Actual Savings',
                    hoverinfo= 'x+text',
                    text= formatted_savings_actual_values
                )
            ],
            'layout': go.Layout(
                title='Another Look at the Data',
                xaxis=dict(title='Months'),
                yaxis=dict(title='Percent of Spending', range=[0, 100])
            )
        },
        config={
            'displaylogo': False}
    )
])

if __name__ == "__main__": # If this app is not being called as part of a module, then:
    app.run(debug=True)
