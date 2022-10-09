# Harmony

Generate four-part harmony following idiomatic voice-leading procedures with DP!

```python
>>> voiceProgression('B-', 'I I6 IV V43/ii ii V V7 I')
```

![Four-part harmony](https://i.imgur.com/9bl7V5t.png)

See the web interface at [autoharmony.herokuapp.com](https://autoharmony.herokuapp.com/). This was built with [Music21](https://github.com/cuthbertLab/music21).

## Usage

First, install and activate dependencies managed by [Pipenv](https://github.com/pypa/pipenv).

```shell
$ pipenv install
$ pipenv shell
```

To generate a chorale:

```shell
$ python voicing.py
```

Then, create a fresh Postgres database. Tables will be created on first application run. To launch the development web server:

```shell
$ FLASK_APP=app.py FLASK_DEBUG=1 DATABASE_URL=<POSTGRES_URL> flask run
```

To launch the production web server:

```shell
$ DATABASE_URL=<POSTGRES_URL> WEB_CONCURRENCY=2 gunicorn app:app
```

## License

Licensed under the [BSD 3-Clause License](LICENSE.txt).
