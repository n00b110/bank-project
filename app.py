from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import timedelta
import dash
from dash import dcc, html
import plotly.graph_objs as go
from database import create_new_user, checkLogin, getLastMonth, getLastQuarter, getLastYear, getLifeTime, getRecoveryQuestions, getLineGraphInfo, checkRecoveryAnswers


class Base(DeclarativeBase):
    pass

app = Flask(__name__)
# Secret key for session encryption
app.secret_key = "budgeting101"
# Lifetime of the permenent session
app.permanent_session_lifetime = timedelta(days=5)

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)



# class User(db.Model):
#     __tablename__ = 'users'
#     username = db.Column(db.String(80), primary_key=True, nullable=False)
#     password = db.Column(db.String(80), nullable=False)

#     def __repr__(self):
#         return f"User(username='{self.username}', age={self.age})"

#APP ROUTES

@app.route('/')
def index():
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

@app.route('/budget/', methods=['GET', 'POST'])
def budget():
    if "user" in session:
        user = session["user"]
        if "totals" not in session:
            # Initialize dictionary to store totals
            session["totals"] = {'budget1': 0, 'budget2': 0, 'budget3': 0}
        
        if request.method == 'POST':

            # Reset totals to zero if reset button is clicked
            if 'reset_budget1' in request.form:
                session["totals"]['budget1'] = 0
                return render_template('budget.html', 
                                budget1_total=format(session["totals"]['budget1'], ".2f"),
                               budget2_total=format(session["totals"]['budget2'], ".2f"),
                               budget3_total=format(session["totals"]['budget3'], ".2f"))
            if 'reset_budget2' in request.form:
                session["totals"]['budget2'] = 0
                return render_template('budget.html', 
                                budget1_total=format(session["totals"]['budget1'], ".2f"),
                               budget2_total=format(session["totals"]['budget2'], ".2f"),
                               budget3_total=format(session["totals"]['budget3'], ".2f"))
            if 'reset_budget3' in request.form:
                session["totals"]['budget3'] = 0
                return render_template('budget.html', 
                                budget1_total=format(session["totals"]['budget1'], ".2f"),
                               budget2_total=format(session["totals"]['budget2'], ".2f"),
                               budget3_total=format(session["totals"]['budget3'], ".2f"))
            
            # Update totals with submitted form data
            for key in session["totals"].keys():
                session["totals"][key] += sum(float(value) for value in request.form.getlist(key))

            # For now just printing the data to the console
            print(session["totals"])

        return render_template('budget.html', 
                               budget1_total=format(session["totals"]['budget1'], ".2f"),
                               budget2_total=format(session["totals"]['budget2'], ".2f"),
                               budget3_total=format(session["totals"]['budget3'], ".2f"))
    else:
        return redirect(url_for("index"))

@app.route('/goals/')
def goals():
    if "user" in session:
        user = session["user"]
        update_rmpc_pie_chart(user)
        return render_template('goals.html')
    else:
        return redirect(url_for("index"))

@app.route("/login/", methods=["POST","GET"])
def login():
    if request.method == "POST":
        user = request.form["emailName"]
        password = request.form["pw"]
        if checkLogin(user, password) == True:
            session.permanent = True
            session["user"] = user
            flash("You've been logged in!")
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect Username or Password")
            return render_template('login.html')
    else:
        if "user" in session:
            user = session["user"]
            flash("Looks like you're already logged in!")
            return redirect(request.referrer)    
        return render_template('login.html')

@app.route("/forgotpassword/", methods=["POST","GET"])
def fPassword():
    if request.method == "POST":
        email = request.form.get("email_forgot")
        
        # Use email variable to send out email

        print("Users Email: {}".format(email))

        flash("Password reset email sent")
    return render_template('fPassword.html')

@app.route("/signup/", methods=["POST","GET"])
def signup():
    if request.method == "POST":
        if "user" in session:
            user = session["user"]
            flash("Please log out to sign up with a new account")
            return render_template('signup.html')
        name = request.form.get("real_name")
        email = request.form.get("user_email")
        password = request.form.get("user_password")
        repeat_password = request.form.get("user_password2")
        
        # Check if passwords match
        if password != repeat_password:
            flash("Passwords do not match. Please try again.")
            return render_template('signup.html')
        
        # Proceed with signup if passwords match
        # THIS IS WHERE DATABASE ENTRY WOULD OCCUR

        print("Users Name: {} Users Email: {} Users Password: {}".format(name, email, password))
        
        flash("You have successfully registered!")
        return redirect(url_for('questions', email = email, password = password))
    else:
        return render_template('signup.html')
    
@app.route("/questions/", methods=["POST","GET"])
def questions():
    if request.method == "POST":
        email = request.args.get('email')
        password = request.args.get('password')
        security_question1 = request.form['security_question1']
        security_answer1 = request.form['security_answer1']
        security_question2 = request.form['security_question2']
        security_answer2 = request.form['security_answer2']
    
        if security_question1 == security_question2:
            flash("For enhanced security, please select two distinct security questions.")
            return render_template('questions.html')

        # STORE QUESTIONS AND ANSWERS IN DATABASE
        create_new_user(email, password, security_question1, security_answer1, security_question2, security_answer2)
        print("SQ1: {} ANS1: {}".format(security_question1, security_answer1))
        print("SQ2: {} ANS2: {}".format(security_question2, security_answer2))
        print(email)
        print(password)

        flash("You have successfully registered! Please login to continue.")
        return redirect(url_for('login'))

    else:
        return render_template('questions.html')
    
@app.route("/submit_answers/", methods=['POST'])
def submit_answers():
    security_question1 = request.form['security_question1']
    security_answer1 = request.form['security_answer1']
    security_question2 = request.form['security_question2']
    security_answer2 = request.form['security_answer2']
    
    if security_question1 == security_question2:
        flash("For enhanced security, please select two distinct security questions.")
        return render_template('questions.html')

    # STORE QUESTIONS AND ANSWERS IN DATABASE
    print("SQ1: {} ANS1: {}".format(security_question1, security_answer1))
    print("SQ2: {} ANS2: {}".format(security_question2, security_answer2))

    flash("You have successfully registered! Please login to continue.")
    return redirect(url_for('login'))

@app.route("/logout/")
def logout():
    if "user" in session:
        user = session["user"]
        session.pop("user", None)
        flash("You've been logged out!")
        return redirect(url_for("index"))
    else:
        flash("You are not logged in yet!")
        return redirect(request.referrer)

# Start of Dash code for reports page
# ----------------------------------------------------------------------------------

recent_month_pie_chart = dash.Dash(__name__, server=app, url_base_pathname='/rmpc/')

rmpc_labels = ['Needs', 'Wants', 'Savings']
rmpc_values = [50, 30, 20]

formatted_rmpc_values = ['${:,.2f}'.format(value) for value in rmpc_values]

recent_month_pie_chart.layout = html.Div(children=[
    dcc.Graph(
        id='rmpc-pie-chart',
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
                paper_bgcolor='#f2f2f2')
        },
        config={'displaylogo': False}
    )
])


def update_rmpc_pie_chart(user):
    data = getLastMonth(user)
    rmpc_labels = ['Needs', 'Wants', 'Savings']
    rmpc_values = data

    # Format values for display
    formatted_rmpc_values = ['${:,.2f}'.format(value) for value in rmpc_values]

    # Update the pie chart with new data
    figure = {
        'data': [go.Pie(
            labels=rmpc_labels,
            values=rmpc_values,
            textinfo='label+percent',
            hoverinfo='label+text',
            text=formatted_rmpc_values
        )],
        'layout': go.Layout(
            title='Your Most Recent Month',
            paper_bgcolor='#f2f2f2'
        )
    }

    return figure

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
                paper_bgcolor='#f2f2f2')
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
                paper_bgcolor='#f2f2f2')
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
                paper_bgcolor='#f2f2f2')
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
                yaxis=dict(title='Percent of Spending', range=[0, 100]),
                paper_bgcolor='#f2f2f2'
            )
        },
        config={
            'displaylogo': False}
    )
])

if __name__ == "__main__": # If this app is not being called as part of a module, then:
    app.run(debug=True)
