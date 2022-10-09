import threading
import os
from fractions import Fraction

from flask import Flask, request, render_template, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

from voicing import generateChorale


def create_app(name: str) -> Flask:
    app = Flask(name)
    uri = os.environ["DATABASE_URL"]
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    return app


app = create_app(__name__)
db = SQLAlchemy(app)


class Chorale(db.Model):
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # User-provided input data
    timesig = db.Column(db.Text(), nullable=False)
    rhythm = db.Column(db.Text(), nullable=False)
    chorale = db.Column(db.Text(), nullable=False)

    # Output data or error message
    mxml = db.Column(db.Text())
    error = db.Column(db.Text())

    def __repr__(self):
        return "<Chorale {}>".format(self.id)


with app.app_context():
    db.create_all()


def generate_subprocess(chorale_id):
    with app.app_context():
        obj = Chorale.query.get(chorale_id)
        try:
            rhythm = obj.rhythm.split()
            lengths = [
                Fraction(rhythm[i % len(rhythm)]) for i in range(len(obj.chorale))
            ]
            score = generateChorale(obj.chorale, lengths, obj.timesig)
            fp = score.write("musicxml")
            with open(fp, "r") as f:
                obj.mxml = f.read()
            db.session.commit()
        except Exception as e:
            obj.error = str(e)
            db.session.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    content = request.get_json(silent=True)
    if (
        content is None
        or "ts" not in content
        or "chorale" not in content
        or "rhythm" not in content
    ):
        abort(400)

    ts = content["ts"]
    chorale = content["chorale"]
    rhythm = list(filter(None, content["rhythm"].split()))

    obj = Chorale(timesig=ts, rhythm=" ".join(rhythm), chorale=chorale)
    db.session.add(obj)
    db.session.commit()

    thread = threading.Thread(target=generate_subprocess, args=(obj.id,))
    thread.start()

    return jsonify(id=obj.id)


@app.route("/status/<int:chorale_id>")
def status(chorale_id):
    chorale = Chorale.query.get_or_404(chorale_id)
    if chorale.mxml is not None:
        return jsonify(status="done")
    if chorale.error is not None:
        return jsonify(status="error", message=chorale.error)
    return jsonify(status="working")


@app.route("/view/<int:chorale_id>")
def view(chorale_id):
    chorale = Chorale.query.get_or_404(chorale_id)
    return render_template(
        "index.html",
        mxml=chorale.mxml,
        ts=chorale.timesig,
        rhythm=chorale.rhythm,
        chorale=chorale.chorale,
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
