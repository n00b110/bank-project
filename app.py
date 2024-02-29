from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/test/')
def about():
    return render_template('test.html')

@app.route("/admin/")
def admin():
    return redirect(url_for("index"))


if __name__ == "__main__": # If this app is not being called as part of a module, then:
    app.run(debug=True)
