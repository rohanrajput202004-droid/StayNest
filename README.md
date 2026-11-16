# 🏨 StayNest — Hotel Reservation & Discovery System

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rohanrajput202004-droid/StayNest)

> A full-featured, production-ready hotel reservation platform built with **Python Flask**, pure **SQLite (standard library `sqlite3`, zero ORM)**, **Jinja2**, and **Bootstrap 5**. Designed to look and feel like industry leaders (Airbnb / Booking.com / OYO).

---

## 🌟 Key Highlights & Features

- **Realistic Indian Destinations**: Pre-seeded with 20 realistic hotels across **Goa, Jaipur, Manali, Mumbai, Udaipur, Delhi, and Kerala** with authentic pricing (₹2,400 to ₹8,500/night), verified amenities, and natural descriptions (no lorem ipsum).
- **Verified Unsplash Photos with Fallback**: All hotel images are direct high-resolution photos with a built-in custom SVG fallback (`hotel_placeholder.svg`) if network is slow or offline.
- **Hero & Live Search Engine**: Search by Destination, Check-in, Check-out dates, and Guests count.
- **Multi-criteria Filter & Sort**:
  - Filter by budget range (with quick presets like Under ₹3.5k, ₹3.5k–₹6k, ₹6k+).
  - Filter by minimum guest ratings (4.5+ Exceptional, 4.0+ Very Good).
  - Filter by amenities (WiFi, Pool, AC, Breakfast, Mountain/Lake View, Spa, Parking, etc.).
  - Sort by Recommended, Price (Low to High / High to Low), and Guest Rating.
- **Hotel Detail Page**:
  - Airbnb-style photo gallery (large hero photo + stacked room details).
  - Genuine Indian reviewer ratings and interactive review submission.
  - Sticky booking card with **live dynamic price calculation** (Nights count × rate + 12% GST).
- **Double-Booking Protection (Mathematical Interval Overlap)**:
  - Prevents overlapping reservations for the same property using SQLite date comparison:  
    `WHERE check_in < new_check_out AND check_out > new_check_in AND status = 'Confirmed'`
- **Guest Authentication & Sessions**:
  - User signup and login with secure password hashing (`werkzeug.security`).
  - Flash notification messages for actions.
- **My Bookings Dashboard**:
  - View all past and upcoming reservations with printable vouchers.
  - 1-Click Free Cancellation (instantly updates status to `Cancelled` and releases the dates for other travelers).
- **Admin Operations Dashboard**:
  - Protected by admin role check (`admin@staynest.com`).
  - Platform KPIs (Total Properties, Bookings Count, Confirmed Gross Revenue, Registered Users).
  - Full CRUD: Add new hotel with live image preview, Edit existing stays, Delete properties.
  - View all platform bookings table with guest details.
- **Custom 404 Error Page**: Friendly, branded destination recovery page.

---

## 🔑 Pre-Configured Demo Credentials

For quick evaluation and college viva demonstrations:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin@staynest.com` | `admin123` | Full access to Admin Portal, Add/Edit/Delete hotels, All bookings |
| **Guest User** | `rohan@example.com` | `user123` | Book stays, View vouchers, Cancel reservations |

*(On the login screen, convenient 1-click buttons automatically populate these credentials!)*

---

## 🛠️ Technology Stack

- **Backend**: Python 3 (Flask framework)
- **Database**: SQLite 3 (Standard library `sqlite3`, using `conn.row_factory = sqlite3.Row`, zero ORM)
- **Security**: `werkzeug.security` (`generate_password_hash`, `check_password_hash`)
- **Frontend / Templating**: Jinja2 Templates, HTML5, CSS3
- **CSS Framework**: Bootstrap 5.3 (via CDN), Bootstrap Icons 1.11 (via CDN)
- **Typography**: Google Font (*Poppins*)
- **JavaScript**: Vanilla JS only where strictly required (Date limits, live price calculator, 1-click modal triggers)

---

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure Python 3.9+ is installed on your computer:
```bash
python --version
```

### 2. Clone or Navigate to Project Folder
```bash
cd staynest
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Flask App
```bash
python app.py
```

### 5. Open in Your Browser
Visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

> **Note on Database Initialization**: You do **not** need to run any manual database setup command! The first time `app.py` runs, it automatically creates `staynest.db`, generates the schema, and seeds all 20 verified hotels and default demo accounts automatically.

---

## ☁️ Step-by-Step PythonAnywhere Free Hosting Deployment

StayNest is pre-configured specifically for PythonAnywhere free hosting:
- `app.py` is in the root directory.
- Root WSGI application variable `app` is exposed.
- Database path uses `os.path.abspath(os.path.dirname(__file__))`.
- Database auto-initializes upon import.

### Step 1: Create a Free Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com) and register for a free **Beginner** account.
2. Note your username (e.g. `yourusername`).

### Step 2: Open a Bash Console
1. From your PythonAnywhere Dashboard, click **Consoles** > **Bash**.
2. Clone or upload your StayNest files into your home directory:
   ```bash
   git clone https://github.com/your-username/staynest.git
   # OR if uploading zip, unzip it into /home/yourusername/staynest
   ```
3. Ensure the folder is located at: `/home/yourusername/staynest`

### Step 3: Set Up Virtual Environment
Inside the Bash console, run:
```bash
mkvirtualenv --python=python3.10 staynest-venv
pip install -r /home/yourusername/staynest/requirements.txt
```

### Step 4: Configure the Web App
1. Go to the **Web** tab in your PythonAnywhere dashboard.
2. Click **Add a new web app**.
3. Choose **Manual configuration** (do NOT choose the default Flask wizard), and select **Python 3.10**.
4. In the **Virtualenv** section:
   - Enter path: `/home/yourusername/.virtualenvs/staynest-venv`
5. In the **Code** section:
   - **Source code**: `/home/yourusername/staynest`
   - **Working directory**: `/home/yourusername/staynest`

### Step 5: Configure the WSGI Configuration File
1. In the **Code** section of the Web tab, click the link to your **WSGI configuration file** (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`).
2. Delete everything inside it and replace it with:
   ```python
   import sys
   import os

   # Path to your project directory
   project_home = '/home/yourusername/staynest'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   # Import the Flask application
   from app import app as application
   ```
   *(Make sure to replace `yourusername` with your actual PythonAnywhere username!)*
3. Click **Save** in the top right.

### Step 6: Reload and Test!
1. Go back to the **Web** tab and click the big green **Reload yourusername.pythonanywhere.com** button.
2. Open `https://yourusername.pythonanywhere.com` in your browser.
3. Your StayNest hotel reservation website is now live on the internet! 🚀

---

## 🎓 College Viva / Project Presentation Q&A

**Q1: Why did you use pure SQLite (`sqlite3`) instead of SQLAlchemy/ORM?**  
*Answer:* For a beginner-level college portfolio, raw SQL demonstrates a solid understanding of relational database design, query optimization, joins, transactions, and security practices (like parameterized queries to prevent SQL injection). It also keeps the codebase lightweight and dependency-free.

**Q2: How do you prevent double-booking for the same room?**  
*Answer:* We use a mathematical interval overlap check in SQL:
```sql
SELECT id FROM bookings
WHERE hotel_id = ? 
  AND status = 'Confirmed'
  AND check_in < new_check_out 
  AND check_out > new_check_in
```
If this query returns any record, the new reservation is rejected with an alert. If a previous booking is cancelled, its status changes to `'Cancelled'` and the dates are immediately freed.

**Q3: How are passwords stored securely?**  
*Answer:* Passwords are never stored in plain text. We utilize `werkzeug.security.generate_password_hash` which generates a salted cryptographic hash. During login, `check_password_hash` verifies the hash securely.

**Q4: How do you ensure the app doesn't break if an image link fails?**  
*Answer:* Every image tag features an inline fallback handler:  
`onerror="this.onerror=null;this.src='/static/images/hotel_placeholder.svg';"`  
If an Unsplash URL fails or the device is offline, a branded local SVG placeholder displays gracefully.

---

## 📄 License
This project is open-source and free to use for academic, portfolio, and learning purposes.
