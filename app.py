from flask import Flask, render_template, flash, redirect, url_for, request
from flask_mysqldb import MySQL
from wtforms import Form, validators, StringField, FloatField, IntegerField, DateField, SelectField
from datetime import datetime
import MySQLdb
import urllib
import requests

# Create instance of flask app
app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'librarydb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialise MYSQL
mysql = MySQL(app)


# Homepage
@app.route('/')
def index():
    return render_template('home.html')


# Members
@app.route('/members')
def members():
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute("SELECT * FROM members")
    members = cur.fetchall()

    # Render Template
    if result > 0:
        return render_template('members.html', members=members)
    else:
        msg = 'No Members Found'
        return render_template('members.html', warning=msg)

    # Close DB Connection
    cur.close()


# View Details of Member by ID
@app.route('/member/<string:id>')
def viewMember(id):
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute("SELECT * FROM members WHERE id=%s", [id])
    member = cur.fetchone()

    # Render Template
    if result > 0:
        return render_template('view_member_details.html', member=member)
    else:
        msg = 'This Member Does Not Exist'
        return render_template('view_member_details.html', warning=msg)

    # Close DB Connection
    cur.close()


# Define Add-Member-Form
class AddMember(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.length(min=6, max=50)])


# Add Member
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    # Get form data from request
    form = AddMember(request.form)

    # To handle POST request to route
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data

        # Create MySQLCursor
        cur = mysql.connection.cursor()

        # Execute SQL Query
        cur.execute(
            "INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("New Member Added", "success")

        # Redirect to show all members
        return redirect(url_for('members'))

    # To handle GET request to route
    return render_template('add_member.html', form=form)


# Edit Member by ID
@app.route('/edit_member/<string:id>', methods=['GET', 'POST'])
def edit_member(id):
    # Get form data from request
    form = AddMember(request.form)

    # To handle POST request to route
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data

        # Create MySQLCursor
        cur = mysql.connection.cursor()

        # Execute SQL Query
        cur.execute(
            "UPDATE members SET name=%s, email=%s WHERE id=%s", (name, email, id))

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Member Updated", "success")

        # Redirect to show all members
        return redirect(url_for('members'))

    # To handle GET request to route

    # To get existing field values of selected member
    cur2 = mysql.connection.cursor()
    result = cur2.execute("SELECT name,email FROM members WHERE id=%s", [id])
    member = cur2.fetchone()
    # To render edit member form
    return render_template('edit_member.html', form=form, member=member)


# Delete Member by ID
# Using POST instead of DELETE because HTML form can only send GET and POST requests
@app.route('/delete_member/<string:id>', methods=['POST'])
def delete_member(id):

    # Create MySQLCursor
    cur = mysql.connection.cursor()
    # Since deleting parent row can cause a foreign key constraint to fail
    try:
        # Execute SQL Query
        cur.execute("DELETE FROM members WHERE id=%s", [id])

        # Commit to DB
        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        # Flash Failure Message
        flash("Member could not be deleted", "danger")
        flash(str(e), "danger")

        # Redirect to show all members
        return redirect(url_for('members'))
    finally:
        # Close DB Connection
        cur.close()

    # Flash Success Message
    flash("Member Deleted", "success")

    # Redirect to show all members
    return redirect(url_for('members'))


# Books
@app.route('/books')
def books():
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute(
        "SELECT id,title,author,total_quantity,available_quantity,rented_count FROM books")
    books = cur.fetchall()

    # Render Template
    if result > 0:
        return render_template('books.html', books=books)
    else:
        msg = 'No Books Found'
        return render_template('books.html', warning=msg)

    # Close DB Connection
    cur.close()


# View Details of Book by ID
@app.route('/book/<string:id>')
def viewBook(id):
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    # Render Template
    if result > 0:
        return render_template('view_book_details.html', book=book)
    else:
        msg = 'This Book Does Not Exist'
        return render_template('view_book_details.html', warning=msg)

    # Close DB Connection
    cur.close()


# Define Add-Book-Form
class AddBook(Form):
    id = StringField('Book ID', [validators.Length(min=1, max=11)])
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author(s)', [validators.Length(min=2, max=255)])
    average_rating = FloatField(
        'Average Rating', [validators.NumberRange(min=0, max=5)])
    isbn = StringField('ISBN', [validators.Length(min=10, max=10)])
    isbn13 = StringField('ISBN13', [validators.Length(min=13, max=13)])
    language_code = StringField('Language', [validators.Length(min=1, max=3)])
    num_pages = IntegerField('No. of Pages', [validators.NumberRange(min=1)])
    ratings_count = IntegerField(
        'No. of Ratings', [validators.NumberRange(min=0)])
    text_reviews_count = IntegerField(
        'No. of Text Reviews', [validators.NumberRange(min=0)])
    publication_date = DateField(
        'Publication Date', [validators.InputRequired()])
    publisher = StringField('Publisher', [validators.Length(min=2, max=255)])
    total_quantity = IntegerField(
        'Total No. of Books', [validators.NumberRange(min=1)])


# Add Book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    # Get form data from request
    form = AddBook(request.form)

    # To handle POST request to route
    if request.method == 'POST' and form.validate():

        # Create MySQLCursor
        cur = mysql.connection.cursor()

        # Check if book with same ID already exists
        result = cur.execute(
            "SELECT id FROM books WHERE id=%s", [form.id.data])
        book = cur.fetchone()
        if(book):
            error = 'Book with that ID already exists'
            return render_template('add_book.html', form=form, error=error)

        # Execute SQL Query
        cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
            form.id.data,
            form.title.data,
            form.author.data,
            form.average_rating.data,
            form.isbn.data,
            form.isbn13.data,
            form.language_code.data,
            form.num_pages.data,
            form.ratings_count.data,
            form.text_reviews_count.data,
            form.publication_date.data,
            form.publisher.data,
            form.total_quantity.data,
            # When a book is first added, available_quantity = total_quantity
            form.total_quantity.data
        ])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("New Book Added", "success")

        # Redirect to show all books
        return redirect(url_for('books'))

    # To handle GET request to route
    return render_template('add_book.html', form=form)


# Define Import-Books-Form
class ImportBooks(Form):
    no_of_books = IntegerField('No. of Books*', [validators.NumberRange(min=1)])
    quantity_per_book = IntegerField(
        'Quantity Per Book*', [validators.NumberRange(min=1)])
    title = StringField(
        'Title', [validators.Optional(), validators.Length(min=2, max=255)])
    author = StringField(
        'Author(s)', [validators.Optional(), validators.Length(min=2, max=255)])
    isbn = StringField(
        'ISBN', [validators.Optional(), validators.Length(min=10, max=10)])
    publisher = StringField(
        'Publisher', [validators.Optional(), validators.Length(min=2, max=255)])


# Import Books from Frappe API
@app.route('/import_books', methods=['GET', 'POST'])
def import_books():
    # Get form data from request
    form = ImportBooks(request.form)

    # To handle POST request to route
    if request.method == 'POST' and form.validate():
        # Create request structure
        url = 'https://frappe.io/api/method/frappe-library?'
        parameters = {'page': 1}
        if form.title.data:
            parameters['title'] = form.title.data
        if form.author.data:
            parameters['author'] = form.author.data
        if form.isbn.data:
            parameters['isbn'] = form.isbn.data
        if form.publisher.data:
            parameters['publisher'] = form.publisher.data

        # Create MySQLCursor
        cur = mysql.connection.cursor()

        # Loop and make request
        no_of_books_imported = 0
        repeated_book_ids = []
        while(no_of_books_imported != form.no_of_books.data):
            r = requests.get(url + urllib.parse.urlencode(parameters))
            res = r.json()
            # Break if message is empty
            if not res['message']:
                break

            for book in res['message']:
                # Check if book with same ID already exists
                result = cur.execute(
                    "SELECT id FROM books WHERE id=%s", [book['bookID']])
                book_found = cur.fetchone()
                if(not book_found):
                    # Execute SQL Query
                    cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                        book['bookID'],
                        book['title'],
                        book['authors'],
                        book['average_rating'],
                        book['isbn'],
                        book['isbn13'],
                        book['language_code'],
                        book['  num_pages'],
                        book['ratings_count'],
                        book['text_reviews_count'],
                        book['publication_date'],
                        book['publisher'],
                        form.quantity_per_book.data,
                        # When a book is first added, available_quantity = total_quantity
                        form.quantity_per_book.data
                    ])
                    no_of_books_imported += 1
                    if no_of_books_imported == form.no_of_books.data:
                        break
                else:
                    repeated_book_ids.append(book['bookID'])
            parameters['page'] = parameters['page'] + 1

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success/Warning Message
        msg = str(no_of_books_imported) + "/" + \
            str(form.no_of_books.data) + " books have been imported. "
        msgType = 'success'
        if no_of_books_imported != form.no_of_books.data:
            msgType = 'warning'
            if len(repeated_book_ids) > 0:
                msg += str(len(repeated_book_ids)) + \
                    " books were found with already exisiting IDs."
            else:
                msg += str(form.no_of_books.data - no_of_books_imported) + \
                    " matching books were not found."

        flash(msg, msgType)

        # Redirect to show all books
        return redirect(url_for('books'))

    # To handle GET request to route
    return render_template('import_books.html', form=form)


# Edit Book by ID
@app.route('/edit_book/<string:id>', methods=['GET', 'POST'])
def edit_book(id):
    # Get form data from request
    form = AddBook(request.form)

    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # To get existing values of selected book
    result = cur.execute("SELECT * FROM books WHERE id=%s", [id])
    book = cur.fetchone()

    # To handle POST request to route
    if request.method == 'POST' and form.validate():
        # Check if book with same ID already exists (if ID field is being edited)
        if(form.id.data != id):
            result = cur.execute(
                "SELECT id FROM books WHERE id=%s", [form.id.data])
            book = cur.fetchone()
            if(book):
                error = 'Book with that ID already exists'
                return render_template('edit_book.html', form=form, error=error, book=form.data)

        # Calculate new available_quantity (No. of books available to be rented)
        available_quantity = book['available_quantity'] + \
            (form.total_quantity.data - book['total_quantity'])

        # Execute SQL Query
        cur.execute("UPDATE books SET id=%s,title=%s,author=%s,average_rating=%s,isbn=%s,isbn13=%s,language_code=%s,num_pages=%s,ratings_count=%s,text_reviews_count=%s,publication_date=%s,publisher=%s,total_quantity=%s,available_quantity=%s WHERE id=%s", [
            form.id.data,
            form.title.data,
            form.author.data,
            form.average_rating.data,
            form.isbn.data,
            form.isbn13.data,
            form.language_code.data,
            form.num_pages.data,
            form.ratings_count.data,
            form.text_reviews_count.data,
            form.publication_date.data,
            form.publisher.data,
            form.total_quantity.data,
            available_quantity,
            id])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Book Updated", "success")

        # Redirect to show all books
        return redirect(url_for('books'))

    # To handle GET request to route
    # To render edit book form
    return render_template('edit_book.html', form=form, book=book)


# Delete Book by ID
# Using POST instead of DELETE because HTML form can only send GET and POST requests
@app.route('/delete_book/<string:id>', methods=['POST'])
def delete_book(id):
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Since deleting parent row can cause a foreign key constraint to fail
    try:
        # Execute SQL Query
        cur.execute("DELETE FROM books WHERE id=%s", [id])

        # Commit to DB
        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:

        print(e)
        # Flash Failure Message
        flash("Book could not be deleted", "danger")
        flash(str(e), "danger")

        # Redirect to show all members
        return redirect(url_for('books'))
    finally:
        # Close DB Connection
        cur.close()

    # Flash Success Message
    flash("Book Deleted", "success")

    # Redirect to show all books
    return redirect(url_for('books'))


# Transactions
@app.route('/transactions')
def transactions():
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query
    result = cur.execute("SELECT * FROM transactions")
    transactions = cur.fetchall()

    # To handle empty fields
    for transaction in transactions:
        for key, value in transaction.items():
            if value is None:
                transaction[key] = "-"

    # Render Template
    if result > 0:
        return render_template('transactions.html', transactions=transactions)
    else:
        msg = 'No Transactions Found'
        return render_template('transactions.html', warning=msg)

    # Close DB Connection
    cur.close()


# Define Issue-Book-Form
class IssueBook(Form):
    book_id = SelectField('Book ID', choices=[])
    member_id = SelectField('Member ID', choices=[])
    per_day_fee = FloatField('Per Day Renting Fee', [
                             validators.NumberRange(min=1)])


# Issue Book
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    # Get form data from request
    form = IssueBook(request.form)

    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Create choices list for SelectField in form
    # https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SelectField
    cur.execute("SELECT id, title FROM books")
    books = cur.fetchall()
    book_ids_list = []
    for book in books:
        t = (book['id'], book['title'])
        book_ids_list.append(t)

    cur.execute("SELECT id, name FROM members")
    members = cur.fetchall()
    member_ids_list = []
    for member in members:
        t = (member['id'], member['name'])
        member_ids_list.append(t)

    form.book_id.choices = book_ids_list
    form.member_id.choices = member_ids_list

    # To handle POST request to route
    if request.method == 'POST' and form.validate():

        # Get the no of books available to be rented
        cur.execute("SELECT available_quantity FROM books WHERE id=%s", [
                    form.book_id.data])
        result = cur.fetchone()
        available_quantity = result['available_quantity']

        # Check if book is available to be rented/issued
        if(available_quantity < 1):
            error = 'No copies of this book are availabe to be rented'
            return render_template('issue_book.html', form=form, error=error)

        # Execute SQL Query to create transaction
        cur.execute("INSERT INTO transactions (book_id,member_id,per_day_fee) VALUES (%s, %s, %s)", [
            form.book_id.data,
            form.member_id.data,
            form.per_day_fee.data,
        ])

        # Update available quantity, rented count of book
        cur.execute(
            "UPDATE books SET available_quantity=available_quantity-1, rented_count=rented_count+1 WHERE id=%s", [form.book_id.data])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Book Issued", "success")

        # Redirect to show all transactions
        return redirect(url_for('transactions'))

    # To handle GET request to route
    return render_template('issue_book.html', form=form)


# Define Issue-Book-Form
class ReturnBook(Form):
    amount_paid = FloatField('Amount Paid', [validators.NumberRange(min=0)])


# Return Book by Transaction ID
@app.route('/return_book/<string:transaction_id>', methods=['GET', 'POST'])
def return_book(transaction_id):
    # Get form data from request
    form = ReturnBook(request.form)

    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # To get existing values of selected transaction
    cur.execute("SELECT * FROM transactions WHERE id=%s", [transaction_id])
    transaction = cur.fetchone()

    # Calculate Total Charge
    date = datetime.now()
    difference = date - transaction['borrowed_on']
    difference = difference.days
    total_charge = difference * transaction['per_day_fee']

    # To handle POST request to route
    if request.method == 'POST' and form.validate():

        # Calculate debt for this transaction based on amount_paid
        transaction_debt = total_charge - form.amount_paid.data

        # Check if outstanding_debt + transaction_debt exceeds Rs.500
        cur.execute("SELECT outstanding_debt,amount_spent FROM members WHERE id=%s", [
                    transaction['member_id']])
        result = cur.fetchone()
        outstanding_debt = result['outstanding_debt']
        amount_spent = result['amount_spent']
        if(outstanding_debt + transaction_debt > 500):
            error = 'Outstanding Debt Cannot Exceed Rs.500'
            return render_template('return_book.html', form=form, error=error)

        # Update returned_on, total_charge, amount_paid for this transaction
        cur.execute("UPDATE transactions SET returned_on=%s,total_charge=%s,amount_paid=%s WHERE id=%s", [
            date,
            total_charge,
            form.amount_paid.data,
            transaction_id
        ])

        # Update outstanding_debt and amount_spent for this member
        cur.execute("UPDATE members SET outstanding_debt=%s, amount_spent=%s WHERE id=%s", [
            outstanding_debt+transaction_debt,
            amount_spent+form.amount_paid.data,
            transaction['member_id']
        ])

        # Update available_quantity for this book
        cur.execute(
            "UPDATE books SET available_quantity=available_quantity+1 WHERE id=%s", [transaction['book_id']])

        # Commit to DB
        mysql.connection.commit()

        # Close DB Connection
        cur.close()

        # Flash Success Message
        flash("Book Returned", "success")

        # Redirect to show all transactions
        return redirect(url_for('transactions'))

    # To handle GET request to route
    return render_template('return_book.html', form=form, total_charge=total_charge, difference=difference, transaction=transaction)


# Reports
@app.route('/reports')
def reports():
    # Create MySQLCursor
    cur = mysql.connection.cursor()

    # Execute SQL Query to get 5 highest paying customers
    result_members = cur.execute(
        "SELECT id,name,amount_spent FROM members ORDER BY amount_spent DESC LIMIT 5")
    members = cur.fetchall()

    # Execute SQL Query to get 5 most popular books
    result_books = cur.execute(
        "SELECT id,title,author,total_quantity,available_quantity,rented_count FROM books ORDER BY rented_count DESC LIMIT 5")
    books = cur.fetchall()

    # Render Template
    msg = ''
    if result_members <= 0:
        msg = 'No Members Found. '
    if result_books <= 0:
        msg = msg+'No Books Found'
    return render_template('reports.html', members=members, books=books, warning=msg)

    # Close DB Connection
    cur.close()


# Define Search-Form
class SearchBook(Form):
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author(s)', [validators.Length(min=2, max=255)])


# Search
@app.route('/search_book', methods=['GET', 'POST'])
def search_book():
    # Get form data from request
    form = SearchBook(request.form)

    # To handle POST request to route
    if request.method == 'POST' and form.validate():
        # Create MySQLCursor
        cur = mysql.connection.cursor()
        title = '%'+form.title.data+'%'
        author = '%'+form.author.data+'%'
        # Check if book with same ID already exists
        result = cur.execute(
            "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", [title, author])
        books = cur.fetchall()
        # Close DB Connection
        cur.close()

        # Flash Success Message
        if result <= 0:
            msg = 'No Results Found'
            return render_template('search_book.html', form=form, warning=msg)

        flash("Results Found", "success")
        # Render template with search results
        return render_template('search_book.html', form=form, books=books)

    # To handle GET request to route
    return render_template('search_book.html', form=form)


if __name__ == '__main__':
    app.secret_key = "secret"
    app.run(debug=True)
