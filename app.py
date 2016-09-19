from flask import Flask

app = Flask(__name__)


@app.route('/')
def catalog():
	pass


@app.route('/login', methods=['GET','POST'])
def login():
	pass


@app.route('/JSON')
def JSONcatalog():
	pass


@app.route('/new', methods=['GET','POST'])
def newGenre():
	pass


@app.route('/<string:genre_name>/edit', methods=['GET','POST'])
def editGenre(genre_name):
	pass


@app.route('/<string:genre_name>/delete', methods=['GET','POST'])
def deleteGenre(genre_name):
	pass


@app.route('/<string:genre_name>')
def showGenre(genre_name):
	pass


@app.route('/<string:genre_name>/new', methods=['GET','POST'])
def addBook(genre_name):
	pass


@app.route('/<string:genre_name>/<string:book_title>')
def showBook(genre_name, book_title):
	pass


@app.route('/<string:genre_name>/<string:book_title>/edit', methods=['GET','POST'])
def editBook(genre_name, book_title):
	pass


@app.route('/<string:genre_name>/<string:book_title>/delete', methods=['GET','POST'])
def deleteBook(genre_name, book_title):
	pass


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
