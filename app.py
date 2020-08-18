import os
from fractions import Fraction

from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy

from voicing import generateChorale

app = application = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Chorale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mxml = db.Column(db.Text(), nullable=False)
    timesig = db.Column(db.Text())
    rhythm = db.Column(db.Text())
    chorale = db.Column(db.Text())

    def __repr__(self):
        return "<Chorale {}>".format(self.id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    ts = request.form["ts"] or None
    chorale = request.form["chorale"]
    rhythm = list(filter(None, request.form["rhythm"].split()))
    lengths = None
    if rhythm:
        lengths = [Fraction(rhythm[i % len(rhythm)]) for i in range(len(chorale))]

    score = generateChorale(chorale, lengths, ts)
    fp = score.write("musicxml")
    with open(fp, "r") as f:
        mxml = f.read()
        obj = Chorale(mxml=mxml, timesig=ts, rhythm=" ".join(rhythm), chorale=chorale)
        db.session.add(obj)
        db.session.commit()
        return redirect(url_for("view", chorale_id=obj.id))


@app.route("/view/<int:chorale_id>")
def view(chorale_id):
    chorale = Chorale.query.get(chorale_id)
    return render_template(
        "index.html",
        mxml=chorale.mxml,
        ts=chorale.timesig,
        rhythm=chorale.rhythm,
        chorale=chorale.chorale,
    )
