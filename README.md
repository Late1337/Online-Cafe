# ☕ Online Cafe

An elegant and responsive web application for managing an online cafe — built with Flask, SQLAlchemy, WTForms, and PostgreSQL.

---

Users can:
- Browse the menu
- View dish details
- Add items to a cart
- Place orders
- View their order history
- Register and log in securely

Admins can:
- Add new menu items
- Toggle item availability (active/inactive)
- Manage the menu

---

## 📸 Preview

![Preview Screenshot](static/images/decorative_img.jpg)

---

## 🚀 Features

- 🔐 User registration & login (with CSRF protection)
- 📋 Menu management (admin only)
- 🛒 Shopping cart (per user session)
- ✅ Order creation and history
- 🏪 Location page with store info
- 🎨 Stylish responsive UI (based on Wix template inspiration)

---

## 🧰 Tech Stack

- **Backend**: Flask, SQLAlchemy, WTForms, Flask-Login
- **Frontend**: HTML, CSS, Jinja2 templates
- **Database**: PostgreSQL
- **Authentication**: Flask-Login
- **Session Handling**: Flask session
- **Security**: CSRF protection with Flask-WTF

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/online-cafe.git
cd online-cafe
```

### 2. Set up a virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# OR
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
- Create a database named Online-Coffee-Shop

- Update main.py with your PostgreSQL username and password:
```bash
PGUSER = "your_username"
PGPASSWORD = "your_password"
```
---

## 🛠 Usage
### Run the app:
```bash
python main.py
```

---

## 👤 Admin Access
### To manage the menu and items:

Register a user with nickname: admin

That user will get access to admin-only views (like /add_position and /manage_menu)

---

## 📂 Project Structure
```bash
├── static/
│   └── images/
│       └── menu, background, etc.
├── templates/
│   ├── index.html
│   ├── home.html
│   ├── menu.html
│   └── ...
├── main.py
├── database.py
├── requirements.txt
└── README.md
```

---

## 📄 License
This project is licensed for educational use. Feel free to use, modify, and improve it.

---

## ✨ Author
### Максим — made with love and coffee ☕
