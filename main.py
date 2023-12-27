from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, FLOAT
import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from datetime import datetime

TMDB_KEY = os.environ['TMDB_KEY']

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collections.db'
db.init_app(app)
Bootstrap5(app)


class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    desc: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(FLOAT, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)


class EditForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

with app.app_context():
    # ---- CREATE NEW DB ---- #
    # db.create_all()

    # ---- ADD FIRST RECORD ---- #
    # db.session.add(Movie(
    #     title="Phone Booth",
    #     year=2002,
    #     desc="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # ))
    # db.session.commit()

    # ---- ADD SECOND RECORD ---- #
    # db.session.add(Movie(
    #     title="Avatar The Way of Water",
    #     year=2022,
    #     desc="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
    #     rating=7.3,
    #     ranking=9,
    #     review="I liked the water.",
    #     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
    # ))
    # db.session.commit()

    def search_movie(title):
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key=<YOUR API KEY>={title}"

        response = requests.get(search_url)
        # id = result['id']
        # desc = result['overview']
        # year = result['release_date'].split('-')[0]
        # img_url = f"http://image.tmdb.org/t/p/original/{result['poster_path']}"
        return response.json()['results']

    def get_review(id):
        review_url = f"https://api.themoviedb.org/3/movie/{id}/reviews?language=en-US&page=1&accept=application/json&api_key=<YOUR API KEY>"
        response = requests.get(review_url)
        result = response.json()['results']
        review = result['content']
        rating = result['author_details']['rating']
        return (review, rating)


    @app.route("/")
    def home():
        movies = db.session.execute(sa.select(Movie).order_by(Movie.ranking.desc())).scalars()
        return render_template("index.html", movies=movies)


    @app.route("/<int:rank>")
    def delete_movie(rank):
        movie_to_delete = db.session.execute(sa.select(Movie).where(Movie.ranking == rank)).scalar()
        db.session.delete(movie_to_delete)
        db.session.commit()
        return redirect("/")


    @app.route("/edit/<int:rank>", methods=['GET', 'POST'])
    def edit(rank):
        form = EditForm()
        movie = db.session.execute(sa.select(Movie).where(Movie.ranking == rank)).scalar()

        if form.validate_on_submit():
            movie.rating = form.rating.data
            movie.review = form.review.data
            db.session.commit()

            return redirect('/')

        return render_template("edit.html", title=movie.title, form=form)


    @app.route("/add", methods=['GET', 'POST'])
    def add_movie():
        form = AddForm()

        if form.validate_on_submit():
            movies = search_movie(form.title.data)

            return render_template('select.html', movies=movies)

        return render_template("add.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)





