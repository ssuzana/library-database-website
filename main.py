from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#app.app_context().push()
app.config['SECRET_KEY'] = 'yoursecretkey'
Bootstrap(app)
#all_books = []


##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class BookForm(FlaskForm):
    title = StringField('Book Name', validators=[DataRequired()])
    author = StringField('Book Author', validators=[DataRequired()])
    rating = SelectField('Rating', choices=[1,2,3,4,5], validators=[DataRequired()])
    submit = SubmitField('Add Book')

##CREATE TABLE
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    with app.app_context():
        all_books = db.session.execute(db.select(Book)).scalars().all()
    return render_template("index.html", book_list=all_books)

@app.route("/add",  methods=["GET", "POST"])
def add():
    form = BookForm()
    # IF ACCESSED VIA POST THEN THE BOOK HAS BEEN ADDED
    if request.method == "POST":
        new_book = Book(title=request.form["title"],
                        author=request.form["author"],
                        rating=request.form["rating"])
        with app.app_context():
            db.session.add(new_book)
            db.session.commit()
        return redirect(url_for('home'))
    # IF ACCESSED VIA GET THEN THE ADD FORM NEEDS TO BE PRESENTED
    return render_template('add.html', form=form)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    # IF ACCESSED VIA POST THEN THE RATING HAS BEEN EDITED
    if request.method == 'POST':
        book_id = request.form["id"]
        with app.app_context():
            book = db.session.execute(db.select(Book).filter_by(id=book_id)).scalar_one()
            book.rating = request.form["rating"]
            db.session.commit()
            return redirect(url_for('home'))
    # IF ACCESSED VIA GET THEN THE EDIT FORM NEEDS TO BE PRESENTED
    book_id = request.args.get('id')
    with app.app_context():
        book = db.session.execute(db.select(Book).filter_by(id=book_id)).scalar_one()
    return render_template('edit_rating.html', book=book)

@app.route("/delete")
def delete():
    book_id = request.args.get('id')
    with app.app_context():
        # DELETE A RECORD BY ID
        book = db.session.execute(db.select(Book).filter_by(id=book_id)).scalar_one()
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

