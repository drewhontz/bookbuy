from flask import Flask, render_template, request, url_for, jsonify, redirect
from flask import flash, session as login_session, make_response
from oauth2client import client
from functools import wraps
from crud import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random, string, json, httplib2, requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Buy Application"

# Convenience function for checking if user logged in
def is_logged_in():
    return 'username' in login_session

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return func(*args, **kwargs)
    return decorated_function

@app.route('/')
def catalog():
    latest = show_latest()
    genre = show_genres()
    return render_template('landing.html', latest=latest, genre=genre)


@app.route('/login')
def login():
    # State property used to protect against cross site forgery
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code from ajax response on login.html
    code = request.data

    try:
        # Boilerplate from Google Documentation/Class
        # Upgrade the authorization code into a credentials object by creating
        # Flow object from client_secret json file.
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info, omitted the picture
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
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
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
        h = httplib2.Http()
        # Request to revoke the authorized token from google server
        result = h.request(url, 'GET')[0]
        print 'result is '
        print result

        # If request is successful, remove all info from the session
        if result['status'] == '200':
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            flash("Successfully logged out")
            return redirect('/')
        else:
            response = make_response(
                json.dumps('Failed to revoke token for given user.', 400))
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/JSON')
def JSONcatalog():
    books = show_catalog()
    return jsonify(BookList=[b.serialize for b in books])


@app.route('/<string:genre_id>/<string:book_id>/JSON')
def JSONitem(genre_id, book_id):
    book = get_book_by_id(book_id)
    return jsonify(Book=book.serialize)


@app.route('/new', methods=['GET', 'POST'])
@login_required
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
        if is_logged_in():
            g = get_genre_by_id(genre_id)
            genres = show_genres()
            return render_template('edit_genre.html', ge=g, genres=genres)
        else:
            return redirect('/login')


@app.route('/<string:genre_id>/delete', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    if request.method == 'POST':
        delete_genre(genre_id)
        flash("Genre removed")
        return redirect('/')
    else:
        if is_logged_in():
            g = get_genre_by_id(genre_id)
            return render_template('delete.html', name=g.name, genre=g)
        else:
            return redirect('/login')


@app.route('/genre/<string:genre_id>')
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
        if is_logged_in():
            g = get_genre_by_id(genre_id)
            genre = show_genres()
            return render_template('new_book.html', genre=g, genres=genre)
        else:
            return redirect('/login')


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
        if is_logged_in():
            b = get_book_by_id(book_id)
            genre = get_genre_by_id(b.genre)
            genres = show_genres()
            return render_template('edit_book.html', genre=genre.name, book=b,
                                   genres=genres)
        else:
            return redirect('/login')


@app.route('/<string:genre_id>/<string:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(genre_id, book_id):
    if request.method == 'POST':
        delete_book(book_id)
        flash("Book deleted")
        return redirect(url_for('showGenre', genre_id=genre_id))
    else:
        if is_logged_in():
            b = get_book_by_id(book_id)
            g = get_genre_by_id(genre_id)
            return render_template('delete.html', name=b.title, genre=g)
        else:
            return redirect('/login')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.jinja_env.globals.update(is_logged_in=is_logged_in)
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
