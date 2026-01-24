from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import json
import rsa_algo  # Make sure rsa_algo.py is in the same folder
# Add these new imports at the very top
import io
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import send_file


app = Flask(__name__)
app.secret_key = "change_this_to_something_secret"

# CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///encryptify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)

# ----------------------------------------
# DATABASE MODELS
# ----------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # Store RSA Keys as JSON strings
    public_key = db.Column(db.String(500), nullable=True) 
    private_key = db.Column(db.String(500), nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # We store the encrypted list as a string like "[123, 456, 789]"
    content = db.Column(db.String(1000), nullable=False) 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%H:%M')
        }

# ----------------------------------------
# ROUTES
# ----------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "User exists!"
        
        # 1. GENERATE RSA KEYS
        pub, priv = rsa_algo.generate_keypair()
        
        # 2. Save them as Strings
        new_user = User(
            username=username, 
            password=password,
            public_key=json.dumps(pub),
            private_key=json.dumps(priv)
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    users = User.query.filter(User.id != current_user_id).all()
    return render_template('dashboard.html', users=users, username=session['username'], user_id=current_user_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------------------------------
# API: FETCH MESSAGES (Decrypts for viewing)
# ----------------------------------------
@app.route('/get_messages/<int:partner_id>')
def get_messages(partner_id):
    if 'user_id' not in session:
        return jsonify([])
    
    my_id = session['user_id']
    me = User.query.get(my_id)
    my_priv_key = json.loads(me.private_key)

    raw_messages = Message.query.filter(
        ((Message.sender_id == my_id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == my_id))
    ).order_by(Message.timestamp.asc()).all()
    
    decrypted_messages = []
    for msg in raw_messages:
        msg_dict = msg.to_dict()
        try:
            # Convert string "[123, 456]" back to list
            encrypted_data = json.loads(msg.content)
            # DECRYPT
            decrypted_text = rsa_algo.decrypt(my_priv_key, encrypted_data)
            msg_dict['content'] = decrypted_text
        except:
            msg_dict['content'] = "[Decryption Error]"
            
        decrypted_messages.append(msg_dict)

    return jsonify(decrypted_messages)

# ----------------------------------------
# SPY VIEW (Evidence Page)
# ----------------------------------------
@app.route('/evidence')
def evidence():
    messages = Message.query.all()
    evidence_data = []
    for msg in messages:
        sender_name = User.query.get(msg.sender_id).username
        receiver_name = User.query.get(msg.receiver_id).username
        evidence_data.append({
            'sender': sender_name,
            'receiver': receiver_name,
            'encrypted_content': msg.content[:50] + "..." 
        })
    return render_template('evidence.html', messages=evidence_data)

# ----------------------------------------
# SOCKET LOGIC (Encrypts before saving)
# ----------------------------------------
@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        join_room(str(session['user_id']))

@socketio.on('private_message')
def handle_private_message(data):
    sender_id = session['user_id']
    receiver_id = data['receiver_id']
    plaintext = data['message']

    print(f"1. Received Plaintext: {plaintext}")

    receiver = User.query.get(receiver_id)
    if not receiver.public_key:
        print("ERROR: Receiver has no Public Key!")
        return

    receiver_pub_key = json.loads(receiver.public_key)

    # ENCRYPT
    encrypted_list = rsa_algo.encrypt(receiver_pub_key, plaintext)
    encrypted_string = json.dumps(encrypted_list) 
    
    print(f"2. Encrypted into: {encrypted_string}")

    # SAVE ENCRYPTED
    new_msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=encrypted_string)
    db.session.add(new_msg)
    db.session.commit()

    # EMIT PLAINTEXT TO UI (For instant feedback)
    emit('new_private_message', {'sender_id': sender_id, 'receiver_id': receiver_id, 'content': plaintext}, room=str(receiver_id))
    emit('new_private_message', {'sender_id': sender_id, 'receiver_id': receiver_id, 'content': plaintext}, room=str(sender_id))


    # ----------------------------------------
# TOOLS SECTION (AES & Utilities)
# ----------------------------------------

# Helper: Generate a valid AES key from a user password
def get_aes_key(password):
    # Turn "secret123" into a valid 32-byte URL-safe base64 key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'salt_static_', # In real apps, salt should be random/stored
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

@app.route('/tools', methods=['GET'])
def tools_page():
    return render_template('tools.html')

@app.route('/tools/text', methods=['POST'])
def tools_text():
    text = request.form['text_input']
    password = request.form['key']
    action = request.form['action']
    
    key = get_aes_key(password)
    f = Fernet(key)
    
    try:
        if action == 'encrypt':
            # Encrypt
            token = f.encrypt(text.encode())
            result = token.decode()
        else:
            # Decrypt
            token = f.decrypt(text.encode())
            result = token.decode()
    except Exception as e:
        result = "Error: Invalid Key or Corrupted Text"

    return render_template('tools.html', text_output=result, text_result=text)

@app.route('/tools/file', methods=['POST'])
def tools_file():
    if 'file' not in request.files:
        return "No file uploaded"
    
    file = request.files['file']
    password = request.form['key']
    action = request.form['action']
    
    if file.filename == '':
        return "No file selected"

    # Read file bytes
    file_data = file.read()
    
    # Get Key
    key = get_aes_key(password)
    f = Fernet(key)
    
    output = io.BytesIO()
    
    try:
        if action == 'encrypt':
            encrypted_data = f.encrypt(file_data)
            output.write(encrypted_data)
            output.seek(0)
            return send_file(output, as_attachment=True, download_name=file.filename + ".enc")
        
        else:
            # Decrypt
            decrypted_data = f.decrypt(file_data)
            output.write(decrypted_data)
            output.seek(0)
            # Remove .enc from filename if present
            original_name = file.filename.replace('.enc', '')
            return send_file(output, as_attachment=True, download_name=original_name)
            
    except Exception as e:
        return f"Error: Failed to process file. Wrong key? {str(e)}"



# ----------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)