import os
from fractions import Fraction

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from voicing import generateChorale

app = application = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        ts = request.form['ts'] or None
        chorale = request.form['chorale']
        rhythm = list(filter(None, request.form['rhythm'].split()))
        lengths = None
        if rhythm:
            lengths = [Fraction(rhythm[i % len(rhythm)])
                       for i in range(len(chorale))]

        score = generateChorale(chorale, lengths, ts)
        fp = score.write('musicxml')
        with open(fp, 'r') as f:
            mxml = f.read()
            return render_template('index.html', mxml=mxml, ts=ts,
                                   rhythm=' '.join(rhythm), chorale=chorale)
