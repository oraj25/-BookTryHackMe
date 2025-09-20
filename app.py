# app.py
import os
import re
from flask import Flask, render_template, request,url_for
from lxml import etree

app = Flask(__name__, static_folder='static', template_folder='templates')

# Single users dict (consolidated)
users = {
    1: {"name":"John Doe","email":"john@example.com","member_since":"Jan 2025"},
    2: {"name":"Alice Smith","email":"alice@example.com","member_since":"Mar 2024"},
    3: {"name":"Bob Johnson","email":"bob@example.com","member_since":"Jan 2025"},
    99: {"name":"CTF Master","email":"ctf@hidden.com","member_since":"Mar 2024"}  # Hidden profile for CTF
}

# Sample books
books = {
    1: {"title":"To Kill a Mockingbird","author":"Harper Lee","genre":"Classic Literature","desc":"...","img":"book1.jpg"},
    2: {"title":"1984","author":"George Orwell","genre":"Dystopian","desc":"...","img":"book2.jpg"},
    3: {"title":"Pride and Prejudice","author":"Jane Austen","genre":"Classic Romance","desc":"...","img":"book3.jpg"},
    4: {"title":"The Hobbit","author":"J.R.R. Tolkien","genre":"Fantasy","desc":"...","img":"book4.jpg"},
    5: {"title":"The Catcher in the Rye","author":"J.D. Salinger","genre":"Classic","desc":"...","img":"book5.jpg"},
    6: {"title":"Harry Potter and the Philosopher's Stone","author":"J.K. Rowling","genre":"Fantasy","desc":"...","img":"book6.jpg"},
    7: {"title":"The Great Gatsby","author":"F. Scott Fitzgerald","genre":"Classic","desc":"...","img":"book7.jpg"},
    8: {"title":"Moby-Dick","author":"Herman Melville","genre":"Adventure","desc":"...","img":"book8.jpg"},
    99: {"title":"Hidden CTF Book","author":"CTF Master","genre":"Secret","desc":"You found the hidden book!","img":"hidden_book.jpg","ctf": True}
}

@app.route('/')
def index():
    return render_template('index.html', books=books)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    filtered_books = {id: book for id, book in books.items()
                      if query.lower() in book['title'].lower()
                      or query.lower() in book['author'].lower()
                      or query.lower() in book['genre'].lower()}
    special_message = ""
    if re.search(r'<\s*script.*?>', query, re.IGNORECASE):
        special_message = "You've unlocked a hidden book! FLAG: THM{reflected_xss_success}"
    return render_template('search.html', books=filtered_books, query=query, special_message=special_message)

@app.route('/book', methods=['GET'])
def book():
    book_id = request.args.get('id')
    if not book_id or not book_id.isdigit() or int(book_id) not in books:
        return "Book not found!", 404
    selected_book = books[int(book_id)]
    special_flag = ""
    if int(book_id) == 99:
        special_flag = "FLAG: THM{idor_hidden_book}"
    return render_template('book.html', book=selected_book, special_flag=special_flag)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        query = f"SELECT * FROM users WHERE email='{email}' AND password='{password}'"
        print("Simulated SQL query:", query)
        if email == "admin@example.com" and password == "password123":
            return render_template('profile.html', user={'name': 'Admin', 'email': email})
        else:
            if "' OR '1'='1" in email:
                return "CTF FLAG: THM{SQLi_successful}"
            return "Login failed! Try again."
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        
        # Password mismatch check
        if password != confirm:
            return render_template('register.html', error="Passwords do not match.", fullname=fullname, email=email)

        # Detect “SQLi-like” input for CTF
        if re.search(r"('|\"|;|--|\bor\b|\bOR\b|\b1=1\b|union\s+select)", fullname + email, re.IGNORECASE):
            # Create a fake profile based on user input
            fake_user = {
                "name":  "SQLi CTF User",
                "email": email or "SQLiuser@example.com",
                "member_since": "SQLi 2025"  # arbitrary date
            }
            # Set the special CTF flag
            flag_message = "Welcome! Your account is created. Note: CTF FLAG: THM{register_sqli_success}"
            
            # Render profile page with fake user + flag
            return render_template('profile.html', user=fake_user, special_flag=flag_message)

        # Normal registration flow
        new_user = {"name": fullname or "New User", "email": email}
        return render_template('profile.html', user=new_user)

    return render_template('register.html')


@app.route('/profile', methods=['GET'])
def profile():
    user_id = request.args.get('id', '1')
    if not user_id.isdigit() or int(user_id) not in users:
        return "User not found!", 404
    selected_user = users[int(user_id)]
    special_flag = ""
    if int(user_id) == 99:
        special_flag = "FLAG: THM{idor_hidden_user}"
    return render_template('profile.html', user=selected_user, special_flag=special_flag)

# --- UPLOAD_FOLDE ---
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_CTF_FLAG = "THM{file_upload_successful}"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    upload_flag = None

    if file:
        filename = file.filename  # intentionally unsafe for CTF
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # Trigger the flag if any .txt file is uploaded
        if filename.lower().endswith(".txt"):
            upload_flag = UPLOAD_CTF_FLAG

    # Re-render book page with upload flag
    sample_book = books.get(1)
    return render_template('book.html', book=sample_book, upload_flag=upload_flag)


PROFILE_UPLOAD_CTF_FLAG = "THM{profile_upload_successful}"

@app.route('/upload_profile', methods=['POST'])
def upload_profile():
    file = request.files.get('file')
    profile_upload_flag = None
    if file:
        filename = file.filename  # intentionally unsafe for CTF
        save_path = os.path.join('static/uploads', filename)
        os.makedirs('static/uploads', exist_ok=True)
        file.save(save_path)

        # Trigger the flag if the file is any .txt file
        if filename.lower().endswith(".txt"):
            profile_upload_flag = PROFILE_UPLOAD_CTF_FLAG

    # Re-render profile page for user 1 (or adjust ID as needed)
    user = users.get(1)
    return render_template('profile.html', user=user, profile_upload_flag=profile_upload_flag)




# --- XXE route ---

@app.route('/xxe', methods=['GET', 'POST'])
def xxe():
    xxe_flag = None
    if request.method == 'POST':
        xml_data = request.form.get('xml_data', '')
        # Simple CTF trigger for XXE
        if "<!ENTITY xxe" in xml_data or "&xxe;" in xml_data:
            xxe_flag = "THM{Review_xxe_successful}"
        else:
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_data)
                book_elem = root.find('book')
                if book_elem is not None:
                    xxe_flag = f"Parsed content: {book_elem.text}"
                else:
                    xxe_flag = "Parsed XML, no <book> element found."
            except Exception as e:
                xxe_flag = f"Error parsing XML: {str(e)}"

    # Render the book page (book 1 for demo)
    return render_template('book.html', book=books[1], xxe_flag=xxe_flag)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
