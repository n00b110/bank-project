from decimal import Decimal
from flask import Flask, redirect, url_for, render_template, request, session, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import timedelta
import dash
from dash import dcc, html
import plotly.graph_objs as go
import plotly.io as pio
from database import create_new_user, checkLogin, getLastMonth, getLastQuarter, getLastYear, getLifeTime, getRecoveryQuestions, getLineGraphInfo, checkRecoveryAnswers, recordNewMonth, checkUserNameInDB, updatePassword


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
            if 'submit_budget' in request.form:
                needs = session["totals"]['budget1']
                wants = session["totals"]['budget2']
                savings = session["totals"]['budget3']
                recordNewMonth(user, needs, wants, savings)
                session["totals"]['budget1'] = 0
                session["totals"]['budget2'] = 0
                session["totals"]['budget3'] = 0
                return redirect(url_for("goals"))
                
            
            # Update totals with submitted form data
            for key in session["totals"].keys():
                session["totals"][key] += sum(float(value) for value in request.form.getlist(key))


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

        #Generate recent month pie chart
        rmpc_labels = ['Needs', 'Wants', 'Savings']
        rmpc_values = getLastMonth(user)
        if rmpc_values == [0.00, 0.00, 0.00]:
            rmpc_values = [100]
            rmpc_labels = ['NO BUDGET DATA ENTERED']
        formatted_rmpc_values = ['${:,.2f}'.format(value) for value in rmpc_values]
        rmpc_fig = go.Figure(data=[go.Pie(
            labels=rmpc_labels,
            values=rmpc_values,
            textinfo='label+percent',
            hoverinfo='label+text',
            text=formatted_rmpc_values
            #colors={'Needs': 'blue', 'Wants': 'green', 'Savings': 'orange'}
        )])

        #Set up colors for the pie charts
        if rmpc_labels[0] != 'NO BUDGET DATA ENTERED':
            colors = {'Needs': '#0b5d1e', 'Wants': '#0b3a5d', 'Savings': '#5d0b19'}
            color_map = [colors[label] for label in rmpc_labels]
            rmpc_fig.data[0].marker.colors = color_map

        rmpc_fig.update_layout(
            title='Your Most Recent Month',
            paper_bgcolor='#f2f2f2'
        )

        #Generate last quarter pie chart
        lqpc_labels = ['Needs', 'Wants', 'Savings']
        lqpc_values = getLastQuarter(user)
        if lqpc_values == [0.00, 0.00, 0.00]:
            lqpc_values = [100]
            lqpc_labels = ['NO BUDGET DATA ENTERED']
        formatted_lqpc_values = ['${:,.2f}'.format(value) for value in lqpc_values]
        lqpc_fig = go.Figure(data=[go.Pie(
            labels=lqpc_labels,
            values=lqpc_values,
            textinfo='label+percent',
            hoverinfo='label+text',
            text=formatted_lqpc_values
        )])
        lqpc_fig.update_layout(
            title='Your Last Quarter',
            paper_bgcolor='#f2f2f2'
        )

        if rmpc_labels[0] != 'NO BUDGET DATA ENTERED':
            color_map = [colors[label] for label in lqpc_labels]
            lqpc_fig.data[0].marker.colors = color_map

        #Generate last year pie chart
        lypc_labels = ['Needs', 'Wants', 'Savings']
        lypc_values = getLastYear(user)
        if lypc_values == [0.00, 0.00, 0.00]:
            lypc_values = [100]
            lypc_labels = ['NO BUDGET DATA ENTERED']
        formatted_lypc_values = ['${:,.2f}'.format(value) for value in lypc_values]
        lypc_fig = go.Figure(data=[go.Pie(
            labels=lypc_labels,
            values=lypc_values,
            textinfo='label+percent',
            hoverinfo='label+text',
            text=formatted_lypc_values
        )])
        lypc_fig.update_layout(
            title='Your Last Year',
            paper_bgcolor='#f2f2f2'
        )

        if rmpc_labels[0] != 'NO BUDGET DATA ENTERED':
            color_map = [colors[label] for label in lypc_labels]
            lypc_fig.data[0].marker.colors = color_map

        #Generate life time pie chart
        ltpc_labels = ['Needs', 'Wants', 'Savings']
        ltpc_values = getLifeTime(user)
        if ltpc_values == [0.00, 0.00, 0.00]:
            ltpc_values = [100]
            ltpc_labels = ['NO BUDGET DATA ENTERED']
        formatted_ltpc_values = ['${:,.2f}'.format(value) for value in ltpc_values]
        ltpc_fig = go.Figure(data=[go.Pie(
            labels=ltpc_labels,
            values=ltpc_values,
            textinfo='label+percent',
            hoverinfo='label+text',
            text=formatted_ltpc_values
        )])
        ltpc_fig.update_layout(
            title='Your Lifetime Budgeting',
            paper_bgcolor='#f2f2f2'
        )

        if rmpc_labels[0] != 'NO BUDGET DATA ENTERED':
            color_map = [colors[label] for label in ltpc_labels]
            ltpc_fig.data[0].marker.colors = color_map

        #Generate the line graph
        x_data = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        needs_baseline = []
        wants_baseline = []
        savings_baseline = []
        needs_actual = []
        wants_actual = []
        savings_actual = []
        budgetInfo = getLineGraphInfo(user)
        for entries in budgetInfo:
            needs_amount = entries[0]
            wants_amount = entries[1]
            savings_amount = entries[2]
            total = needs_amount + wants_amount + savings_amount
            needs_baseline_amount = total / Decimal(2)
            wants_baseline_amount = total * (Decimal(3) / Decimal(10))
            savings_baseline_amount = total * (Decimal(1) / Decimal(5))
            needs_actual.insert(0, needs_amount)
            wants_actual.insert(0, wants_amount)
            savings_actual.insert(0, savings_amount)
            needs_baseline.insert(0, needs_baseline_amount)
            wants_baseline.insert(0, wants_baseline_amount)
            savings_baseline.insert(0, savings_baseline_amount)

        # Define formatted values for display
        formatted_needs_baseline_values = ['${:,.2f}'.format(value) for value in needs_baseline]
        formatted_wants_baseline_values = ['${:,.2f}'.format(value) for value in wants_baseline]
        formatted_savings_baseline_values = ['${:,.2f}'.format(value) for value in savings_baseline]
        formatted_needs_actual_values = ['${:,.2f}'.format(value) for value in needs_actual]
        formatted_wants_actual_values = ['${:,.2f}'.format(value) for value in wants_actual]
        formatted_savings_actual_values = ['${:,.2f}'.format(value) for value in savings_actual]

        # Define the figure for the line graph
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=x_data,
            y=needs_baseline,
            mode='lines+markers',
            marker=dict(color='#ADD8E6'),
            name='Needs Goal',
            hoverinfo='x+text',
            text=formatted_needs_baseline_values
        ))
        # Add other traces similarly for other lines
        line_fig.add_trace(go.Scatter(
            x=x_data,
            y=wants_baseline,
            mode='lines+markers',
            marker=dict(color='#FFDAB9'),
            name='Wants Goal',
            hoverinfo='x+text',
            text=formatted_wants_baseline_values
        ))
        line_fig.add_trace(go.Scatter(
            x=x_data,
            y=savings_baseline,
            mode='lines+markers',
            marker=dict(color='#ABFFAB'),
            name='Savings Goal',
            hoverinfo='x+text',
            text=formatted_savings_baseline_values
        ))
        line_fig.add_trace(go.Scatter(
            x=x_data,
            y=wants_actual,
            mode='lines+markers',
            marker=dict(color='#d62728'),
            name='Wants Actual',
            hoverinfo='x+text',
            text=formatted_wants_actual_values
        ))
        line_fig.add_trace(go.Scatter(
            x=x_data,
            y=needs_actual,
            mode='lines+markers',
            marker=dict(color='#1f77b4'),
            name='Needs Actual',
            hoverinfo='x+text',
            text=formatted_needs_actual_values
        ))
        line_fig.add_trace(go.Scatter(
            x=x_data,
            y=savings_actual,
            mode='lines+markers',
            marker=dict(color='#2ca02c'),
            name='Actual Savings',
            hoverinfo='x+text',
            text=formatted_savings_actual_values
        ))
        # Update the layout of the line graph figure
        line_fig.update_layout(
            title='Another Look at the Data',
            xaxis=dict(title='Months'),
            #yaxis=dict(title='Percent of Spending', range=[0, 100]),
            yaxis=dict(title='Amount Spent'),
            paper_bgcolor='#f2f2f2'
        )


        return render_template("goals.html",
                               rmpc_graph = rmpc_fig.to_html(full_html=False),
                               lqpc_graph = lqpc_fig.to_html(full_html=False),
                               lypc_graph = lypc_fig.to_html(full_html=False),
                               ltpc_graph = ltpc_fig.to_html(full_html=False),
                               linegraph_graph = line_fig.to_html(full_html=False))
    else:
        return redirect(url_for("index"))

@app.route("/login/", methods=["POST","GET"])
def login():
    if request.method == "POST":
        user = request.form["emailName"]
        password = request.form["pw"]
        if checkUserNameInDB(user) == None:
            flash("Incorrect Username or Password")
            return render_template('login.html')
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
        if checkUserNameInDB(email) != None:
            return redirect(url_for('forgotQuestions', email = email))
        else:
            flash("The email provided was not found, please try again")
    return render_template('fPassword.html')

@app.route("/forgotQuestions/", methods=["POST","GET"])
def forgotQuestions():
    email = request.args.get('email')
    recoveryQuestions = getRecoveryQuestions(email)
    if request.method == "POST":
        question1 = request.form.get('question1')
        question2 = request.form.get('question2')
        if checkRecoveryAnswers(email, question1, question2):
            flash("Please choose a new password")
            return redirect(url_for('resetPassword', email = email))
        flash("Answers were not correct. Please try again")
        return render_template('fPasswordQuestions.html', recoveryQuestions = recoveryQuestions)
    return render_template('fPasswordQuestions.html', recoveryQuestions = recoveryQuestions)

@app.route("/resetPassword/", methods=["POST", "GET"])
def resetPassword():
    email = request.args.get('email')
    if request.method == "POST":
        newPassword = request.form.get('newPassword')
        if request.form.get('newPassword') == request.form.get('confirmPassword'):
            updatePassword(email, newPassword)
            flash("Your Password has been Updated!")
            return redirect(url_for('login'))
        else:
            flash("Oops, your passwords did not match!")
    return render_template('resetPassword.html')

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
        
        #check if the username is taken
        if checkUserNameInDB(email) != None:
            flash("Sorry, that email is already taken!")
            return render_template('signup.html')
        
        # Proceed with signup if passwords match
        # THIS IS WHERE DATABASE ENTRY WOULD OCCUR

        print("Users Name: {} Users Email: {} Users Password: {}".format(name, email, password))
        
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

if __name__ == "__main__": # If this app is not being called as part of a module, then:
    app.run(debug=True)
