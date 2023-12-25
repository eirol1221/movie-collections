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

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
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
        movie_url = "https://www.themoviedb.org/"

        form = AddForm()

        if form.validate_on_submit():
            print(form.title.data)



        return render_template("add.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)




    # ---- CREATE NEW DB ---- #
    # db.create_all()





