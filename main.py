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

TMDB_KEY = os.environ['TMDB_KEY']
SECRET_KEY = os.environ['SECRET_KEY']

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collections.db'
db.init_app(app)
Bootstrap5(app)

headers = {
    "accept": "application/json",
}

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    desc: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(FLOAT, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=False)


class EditForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

with app.app_context():
    # ---- TO CREATE NEW DB, UNCOMMENT BELOW LINE ---- #
    # db.create_all()

    # ---- TO ADD FIRST SAMPLE RECORD, UNCOMMENT BELOW LINES ---- #
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

    # ---- TO ADD SECOND SAMPLE RECORD, UNCOMMENT THIS LINE ---- #
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


    # def new_movie(title, year, desc, img_url, rating=0, ranking=0, review="None"):
    #     db.session.add(Movie(
    #         title=title,
    #         year=year,
    #         desc=desc,
    #         rating=rating,
    #         ranking=ranking,
    #         review=review,
    #         img_url=img_url
    #     ))
    #     db.session.commit()


    def search_movie_id(title):
        params = {
            'query': title
        }
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key=<YOUR API KEY>"
        response = requests.get(search_url, headers=headers, params=params)
        return response.json()['results']


    @app.route("/")
    def home():
        movies = db.session.execute(sa.select(Movie).order_by(Movie.rating.desc())).scalars()
        rating_list = [movie.rating for movie in movies]

        for num in range(len(rating_list), 0, -1):
            movie = db.session.execute(sa.select(Movie).where(Movie.rating == rating_list[num-1])).scalar()
            movie.ranking = num
            db.session.commit()

        movies = db.session.execute(sa.select(Movie).order_by(Movie.ranking.desc())).scalars()
        return render_template("index.html", movies=movies)


    @app.route("/<int:id>")
    def delete_movie(id):
        movie_to_delete = db.session.execute(sa.select(Movie).where(Movie.id == id)).scalar()
        db.session.delete(movie_to_delete)
        db.session.commit()
        return redirect("/")


    @app.route("/edit/<int:id>", methods=['GET', 'POST'])
    def edit(id):
        form = EditForm()
        movie = db.session.execute(sa.select(Movie).where(Movie.id == id)).scalar()
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
            movies = search_movie_id(form.title.data)
            return render_template('select.html', movies=movies)
        return render_template("add.html", form=form)


    @app.route("/find")
    def get_movie_details():
        id = request.args.get('id')
        response = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key=<YOUR API KEY>")
        movie_details = response.json()

        new_movie = Movie(
            title=movie_details['title'],
            year=movie_details['release_date'].split('-')[0],
            desc=movie_details['overview'],
            img_url=f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()

        print(new_movie.id)
        return redirect(url_for('edit', id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)





