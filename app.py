from flask import Flask, render_template, request, url_for, jsonify, redirect
from flask import flash, session as login_session
from crud import *
import random, string

app = Flask(__name__)


@app.route('/')
def catalog():
    latest = show_latest()
    genre = show_genres()
    return render_template('landing.html', latest=latest, genre=genre)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/')
    else:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', state=login_session['state'])


@app.route('/JSON')
def JSONcatalog():
    books = show_catalog()
    return jsonify(BookList=[b.serialize for b in books])


@app.route('/new', methods=['GET', 'POST'])
def newGenre():
    if request.method == 'POST':
        name = request.form['name']
        add_genre(name=name)
        flash("New genre added!")
        return redirect('/')
    else:
        g = show_genres()
        return render_template('new_genre.html', genre=g)


@app.route('/<string:genre_id>/edit', methods=['GET', 'POST'])
def editGenre(genre_id):
    if request.method == 'POST':
        edit = request.form['name']
        edit_genre(gid=genre_id, name=edit)
        flash("Genre editted!")
        return redirect(url_for('showGenre', genre_id=genre_id))
    else:
        g = get_genre_by_id(genre_id)
        genres = show_genres()
        return render_template('edit_genre.html', ge=g, genres=genres)


@app.route('/<string:genre_id>/delete', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    if request.method == 'POST':
        delete_genre(genre_id)
        flash("Genre removed")
        return redirect('/')
    else:
        g = get_genre_by_id(genre_id)
        return render_template('delete.html', name=g.name, genre=g)


@app.route('/<string:genre_id>')
def showGenre(genre_id):
    b = show_books(genre_id)
    g = show_genres()
    genre = get_genre_by_id(genre_id)
    return render_template('genre_contents.html', books=b, genre=g,
                           type=genre.name, id=genre.id)


@app.route('/<string:genre_id>/new', methods=['GET', 'POST'])
def newBook(genre_id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        price = request.form['price']
        description = request.form['description']
        picture = request.form['picture']
        add_book(title=title, author=author, publisher=publisher, price=price,
                 description=description, picture=picture, genre_id=genre_id)
        flash("New book added")
        return redirect(url_for('showGenre', genre_id=genre_id))
    else:
        g = get_genre_by_id(genre_id)
        genre = show_genres()
        return render_template('new_book.html', genre=g, genres=genre)


@app.route('/<string:genre_id>/<string:book_id>')
def showBook(genre_id, book_id):
    b = get_book_by_id(book_id)
    g = show_genres()
    genre = get_genre_by_id(genre_id)
    return render_template('item_contents.html', genre=g, book=b, type=genre)


@app.route('/<string:genre_id>/<string:book_id>/edit',
           methods=['GET', 'POST'])
def editBook(genre_id, book_id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        price = request.form['price']
        description = request.form['description']
        picture = request.form['picture']
        edit_book(bid=book_id, title=title, author=author, publisher=publisher,
                  price=price, description=description, picture=picture,
                  genre_id=genre_id)
        flash("Book edits made!")
        return redirect(url_for('showBook', genre_id=genre_id,
                                book_id=book_id))
    else:
        b = get_book_by_id(book_id)
        genre = get_genre_by_id(b.genre)
        genres = show_genres()
        return render_template('edit_book.html', genre=genre.name, book=b,
                               genres=genres)


@app.route('/<string:genre_id>/<string:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(genre_id, book_id):
    if request.method == 'POST':
        delete_book(book_id)
        flash("Book deleted")
        return redirect(url_for('showGenre', genre_id=genre_id))
    else:
        b = get_book_by_id(book_id)
        g = get_genre_by_id(genre_id)
        return render_template('delete.html', name=b.title, genre=g)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
