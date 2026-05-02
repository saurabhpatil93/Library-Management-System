from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "library_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- MODELS --------------------

class Member(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))


class Author(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    nationality = db.Column(db.String(100))


class Book(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    genre = db.Column(db.String(100))

    copies = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    author = db.relationship('Author')


class IssueRecord(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    member_name = db.Column(db.String(100))

    book_title = db.Column(db.String(100))

    issue_date = db.Column(db.String(100))

    due_date = db.Column(db.String(100))

    status = db.Column(db.String(100))


class ReturnRecord(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    return_date = db.Column(db.String(100))

    condition = db.Column(db.String(100))

    issue_id = db.Column(db.Integer)


class Fine(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Float)

    paid_status = db.Column(db.Boolean)

    issue_id = db.Column(db.Integer)


class Reservation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    reserve_date = db.Column(db.String(100))

    expiry_date = db.Column(db.String(100))

    status = db.Column(db.String(100))


class Complaint(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    description = db.Column(db.String(300))

    date = db.Column(db.String(100))

    status = db.Column(db.String(100))

# -------------------- REGISTER --------------------

@app.route('/', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']

        email = request.form['email']

        password = request.form['password']

        user = Member(
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)

        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

# -------------------- LOGIN --------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = Member.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session['user'] = user.name

            return redirect('/dashboard')

    return render_template('login.html')

# -------------------- DASHBOARD --------------------
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:

        return redirect('/login')

    books = Book.query.all()

    members = Member.query.all()

    issued_books = IssueRecord.query.all()

    returned_books = ReturnRecord.query.all()

    fines = Fine.query.all()

    return render_template(

        'dashboard.html',

        books=books,

        members=members,

        issued_books=issued_books,

        returned_books=returned_books,

        fines=fines
    )
# -------------------- ADD BOOK --------------------

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():

    if request.method == 'POST':

        title = request.form['title']

        genre = request.form['genre']

        copies = request.form['copies']

        author_name = request.form['author']

        author = Author.query.filter_by(
            name=author_name
        ).first()

        if not author:

            author = Author(
                name=author_name,
                nationality='Unknown'
            )

            db.session.add(author)

            db.session.commit()

        book = Book(
            title=title,
            genre=genre,
            copies=copies,
            author=author
        )

        db.session.add(book)

        db.session.commit()

        return redirect('/dashboard')

    return render_template('add_book.html')

# -------------------- ISSUE BOOK --------------------

@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():

    if request.method == 'POST':

        member_name = request.form['member_name']

        book_title = request.form['book_title']

        issue = IssueRecord(
            member_name=member_name,
            book_title=book_title,
            issue_date='Today',
            due_date='7 Days Later',
            status='Issued'
        )

        db.session.add(issue)

        db.session.commit()

        return redirect('/dashboard')

    return render_template('issue_book.html')

#return book with fine calculation for late returns
@app.route('/return_book', methods=['GET', 'POST'])
def return_book():

    if request.method == 'POST':

        issue_id = request.form['issue_id']

        days_late = int(request.form['days_late'])

        fine_amount = 0

        if days_late > 0:

            fine_amount = days_late * 10

            fine = Fine(
                amount=fine_amount,
                paid_status=False,
                issue_id=issue_id
            )

            db.session.add(fine)

        return_record = ReturnRecord(
            return_date='Today',
            condition='Good',
            issue_id=issue_id
        )

        db.session.add(return_record)

        db.session.commit()

        return redirect('/dashboard')

    return render_template('return_book.html')
# -------------------- DELETE BOOK --------------------

@app.route('/delete/<int:id>')
def delete(id):

    book = Book.query.get(id)

    if book:

        db.session.delete(book)

        db.session.commit()

    return redirect('/dashboard')

# -------------------- LOGOUT --------------------

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

# -------------------- DATABASE --------------------

with app.app_context():

    # Drop old tables to avoid schema conflicts
    db.drop_all()

    # Create fresh tables
    db.create_all()

    # ---------------- SAMPLE AUTHORS ----------------

    author1 = Author(
        name='Guido Rossum',
        nationality='Dutch'
    )

    author2 = Author(
        name='Ian Goodfellow',
        nationality='American'
    )

    author3 = Author(
        name='Andrew Tanenbaum',
        nationality='American'
    )

    db.session.add_all([
        author1,
        author2,
        author3
    ])

    db.session.commit()

    # ---------------- SAMPLE BOOKS ----------------

    books = [

        Book(
            title='Python Programming',
            genre='Programming',
            copies=10,
            author=author1
        ),

        Book(
            title='Deep Learning',
            genre='Artificial Intelligence',
            copies=5,
            author=author2
        ),

        Book(
            title='Computer Networks',
            genre='Networking',
            copies=8,
            author=author3
        ),

        Book(
            title='Machine Learning',
            genre='AI',
            copies=12,
            author=author2
        ),

        Book(
            title='Database Systems',
            genre='DBMS',
            copies=7,
            author=author3
        )
    ]

    db.session.add_all(books)

    db.session.commit()

# -------------------- RUN --------------------

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5200,
        debug=True
    )