from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta


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

@app.route("/logout/")
def logout():
    if "user" in session:
        user = session["user"]
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__": # If this app is not being called as part of a module, then:
    app.run(debug=True)
