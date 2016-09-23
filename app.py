from flask import Flask, render_template, request, url_for, jsonify, redirect, json
from flask import flash, session as login_session
from oauth2client import client

from crud import *
import random, string, httplib2

app = Flask(__name__)

CLIENT_SECRETS = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']

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


@app.route('/gconnect', methods=['GET', 'POST'])
def auth():
    flow = client.flow_from_clientsecrets(CLIENT_SECRETS, scope='',
        redirect_uri='postmessage')
    auth_code = request.data
    
    # redirect to the auth_uri
    # you will receive an auth code in response if success

    credentials = flow.step2_exchange(auth_code)
    http_auth = credentials.authorize(httplib2.Http())

     # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
    
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


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
