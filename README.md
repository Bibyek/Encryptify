# 🛡️ Encryptify: End-to-End Encrypted Communication Suite

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?style=for-the-badge&logo=flask)
![Socket.IO](https://img.shields.io/badge/Socket.IO-RealTime-black?style=for-the-badge&logo=socket.io)
![Security](https://img.shields.io/badge/Security-RSA%20%2B%20AES-red?style=for-the-badge&logo=lock)

> **"Privacy is not an option, it's a right."**

**Encryptify** is a BCA 6th Semester project-II that demonstrates a robust, mathematically secure communication system. Unlike standard chat applications, Encryptify implements the **RSA Algorithm from scratch** to ensure true End-to-End Encryption (E2EE), proving that even the database administrator cannot read user messages.

---

## 🚀 Key Features

### 1. 🔐 Secure Real-Time Chat (The Core)
* **Instant Messaging:** Powered by **WebSockets (Socket.IO)** for zero-latency communication.
* **Mathematical Security:** Implements a custom RSA Key Generation engine.
    * Each user gets a unique **Public Key** (visible to others) and **Private Key** (stored secretly).
    * Messages are encrypted *before* they hit the database.

### 2. 🕵️ "Spy View" Evidence System
* A dedicated module proving the system's integrity.
* Displays the **Raw Database View**, showing that all stored messages are purely ciphertext (random numbers) and unreadable to hackers or admins.

### 3. 🛠️ Cryptography Utility Belt
A standalone suite of tools for file and text security:
* **Text Locker:** Encrypt/Decrypt sensitive notes using **AES-128**.
* **File Vault:** Upload images or documents to lock them into `.enc` files using Fernet (Symmetric Encryption).

### 4. 📂 Enterprise Architecture
* **Scalable Backend:** Built on Python Flask with SQLAlchemy ORM.
* **Database Agnostic:** Configured for **PostgreSQL** (Production) but supports SQLite for development.
* **Modern UI:** A clean, glassmorphism-inspired interface using **Bootstrap 5**.

---

## 🧠 The Algorithm (Under the Hood)

Encryptify does not rely solely on libraries for its core logic. The Key Generation is calculated mathematically:

$$n = p \times q$$
$$\phi(n) = (p-1) \times (q-1)$$
$$d \equiv e^{-1} \pmod{\phi(n)}$$

* **p, q:** Large Prime Numbers generated securely.
* **n:** The Modulus (Part of Public Key).
* **e:** Public Exponent.
* **d:** Private Exponent (The Secret Key).

---

## 📸 Screenshots

<img width="1268" height="601" alt="Screenshot 2026-01-27 222951" src="https://github.com/user-attachments/assets/3cd4dc7f-a92e-46a4-aee6-e1f13e186537" />
<img width="1265" height="592" alt="Screenshot 2026-01-27 223027" src="https://github.com/user-attachments/assets/306c9752-c055-43e5-b353-58f5167f4e44" />
<img width="1265" height="596" alt="Screenshot 2026-01-27 223049" src="https://github.com/user-attachments/assets/4a76ecdd-371e-46ee-a009-cb2c4b1dc0ee" />
<img width="1265" height="593" alt="Screenshot 2026-01-27 223108" src="https://github.com/user-attachments/assets/512992f3-90bc-420e-96d7-b38a229ae1f0" />
<img width="1264" height="598" alt="Screenshot 2026-01-27 223128" src="https://github.com/user-attachments/assets/3327b63b-e733-4155-b269-584f55a1966b" />
<img width="1262" height="578" alt="Screenshot 2026-01-27 223228" src="https://github.com/user-attachments/assets/19a147cc-d89e-47f0-ac63-1aa091058872" />
<img width="1268" height="590" alt="Screenshot 2026-01-27 223248" src="https://github.com/user-attachments/assets/fdf699d1-5b19-4dd8-b15c-d6d4b4e69a2d" />


---

## 🛠️ Installation & Setup

Want to run this locally? Follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/encryptify.git](https://github.com/your-username/encryptify.git)
cd encryptify
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Database Setup
Ensure PostgreSQL (or XAMPP MySQL) is running.

Update the SQLALCHEMY_DATABASE_URI in app.py with your credentials.

Run the app to auto-migrate tables:

Bash
python app.py
4. Run the Server
Bash
python app.py
Visit http://127.0.0.1:5000 in your browser.

🔮 Future Roadmap
[ ] Hybrid Encryption: Combining RSA (for key exchange) with AES (for message payload) to increase speed.

[ ] Voice Notes: Encrypted audio blob transmission.

[ ] PWA Support: Making the web app installable on mobile devices.

👨‍💻 Author
BCA 6th Semester TU 
Project II
