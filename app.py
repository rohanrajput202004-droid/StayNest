import os
import sqlite3
import random
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# -----------------------------------------------------------------------------
# StayNest - Flask Application Configuration
# Beginner friendly, standard Python without ORM or complex classes
# -----------------------------------------------------------------------------

# Absolute path to current directory (ensures PythonAnywhere finds database)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'staynest.db')

app = Flask(__name__)
app.secret_key = 'staynest-secret-key-college-portfolio-2026'

# Helper function to connect to SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    # Enable access by column name (e.g., row['name'])
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------------------------------------------------------
# Database Schema and Automatic Seeding
# Creates tables and seeds 20 realistic Indian hotels on first run
# -----------------------------------------------------------------------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users table (Guests and Admins)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Hotels table (20 verified stays across India)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT NOT NULL,
            description TEXT NOT NULL,
            price_per_night INTEGER NOT NULL,
            rating REAL NOT NULL,
            review_count INTEGER DEFAULT 0,
            amenities TEXT NOT NULL,
            image_main TEXT NOT NULL,
            images_extra TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Bookings table (with date overlap prevention)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            hotel_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            guest_email TEXT NOT NULL,
            guest_phone TEXT NOT NULL,
            check_in DATE NOT NULL,
            check_out DATE NOT NULL,
            guests INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT DEFAULT 'Confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (hotel_id) REFERENCES hotels(id)
        )
    ''')

    # 4. Reviews table (realistic guest feedback)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hotel_id) REFERENCES hotels(id)
        )
    ''')

    conn.commit()

    # -------------------------------------------------------------------------
    # Auto-seed Default Users if empty
    # -------------------------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        admin_pass = generate_password_hash("admin123")
        user_pass = generate_password_hash("user123")

        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ("Admin StayNest", "admin@staynest.com", admin_pass, "admin"))

        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ("Rohan Mehta", "rohan@example.com", user_pass, "user"))

        conn.commit()

    # -------------------------------------------------------------------------
    # Auto-seed 20 Hotels if empty
    # -------------------------------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM hotels")
    hotel_count = cursor.fetchone()[0]

    if hotel_count == 0:
        hotels_seed = [
            # Goa
            (
                "Heritage Candolim Bay Resort", "Goa", "Candolim Beach Road, North Goa",
                "Nestled 200 meters from the serene Candolim shoreline, this heritage retreat combines colonial Portuguese architecture with modern tropical luxury. Features manicured palm gardens, a lagoon pool, and an open-air seafood bistro.",
                4800, 4.8, 142,
                "WiFi, Pool, AC, Free Breakfast, Beach Access, Bar",
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Palolem Palms Beach Villa", "Goa", "Palolem Beach Front, South Goa",
                "Wake up to soothing ocean breezes and golden sands right at your doorstep. These eco-luxury wooden cottages provide private sun-decks, beach hammocks, and fresh coastal coconut breakfasts.",
                3200, 4.6, 98,
                "WiFi, AC, Free Breakfast, Beach Access, Parking",
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Fontainhas Latin Heritage Stay", "Goa", "31st January Road, Fontainhas, Panaji",
                "Immerse yourself in Old Goa's vibrant Latin Quarter. Restored 18th-century mansion featuring antique rosewood furniture, tiled verandas, artisanal Goan bakery, and walking access to riverside promenades.",
                3900, 4.7, 115,
                "WiFi, AC, Restaurant, Free Breakfast, Room Service",
                "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80"
            ),
            # Jaipur
            (
                "Rajputana Haveli & Heritage Spa", "Jaipur", "Kanti Nagar, Bani Park, Jaipur",
                "Experience authentic royal Marwari hospitality. Hand-painted frescoes, carved stone jharokhas, traditional puppet evenings, and an ayurvedic rejuvenation spa make your royal city trip memorable.",
                4200, 4.7, 184,
                "WiFi, Pool, Spa, Free Breakfast, Parking, Restaurant",
                "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Amer Valley Royal Palace Hotel", "Jaipur", "Old Delhi Road, Near Amer Fort, Jaipur",
                "Overlooking the rugged Aravalli ridges and Amer fort ramparts. Features palatial courtyard dining, rooftop stargazing cabanas, and regal suites with plush brass-accented interiors.",
                5600, 4.9, 210,
                "WiFi, Pool, Mountain View, Restaurant, Free Breakfast, Bar",
                "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1587985064135-0366536eab42?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Pink City Courtyard Retreat", "Jaipur", "MI Road, Gopalbari, Jaipur",
                "A comfortable, budget-friendly modern boutique stay in central Jaipur. Steps away from bustling Johari Bazaar, offering plush clean beds, high-speed WiFi, and wholesome Rajasthani thali lunches.",
                2750, 4.4, 87,
                "WiFi, AC, Free Breakfast, Room Service, Elevator",
                "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80"
            ),
            # Manali
            (
                "Solang Pinecrest Mountain Resort", "Manali", "Solang Valley Road, Manali",
                "Surrounded by whispering cedar woods and snow-clad Himalayan peaks. Boasts heated wooden chalets, river-facing balconies, evening bonfires, and direct access to Solang adventure trails.",
                4500, 4.8, 160,
                "WiFi, Mountain View, Heater, Free Breakfast, Parking, Restaurant",
                "https://images.unsplash.com/photo-1596436889106-be35e843f974?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1587985064135-0366536eab42?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Old Manali Cedar Wood Lodge", "Manali", "Manu Temple Road, Old Manali",
                "Charming rustic alpine lodge in scenic Old Manali. Unwind with hot apple cider in the glass-house cafe, soak in mountain panoramas, and stroll through nearby apple orchards.",
                2400, 4.5, 92,
                "WiFi, Mountain View, Cafe, Heater, Room Service",
                "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Rohtang Vista Snow Chalet", "Manali", "Naggar Highway, Prini, Manali",
                "Panoramic vistas of the Pir Panjal range. Premium Himalayan stone-and-pine suites equipped with glass fireplaces, heated plush flooring, and mountain valley observation decks.",
                3800, 4.6, 104,
                "WiFi, Mountain View, Fireplace, Free Breakfast, Parking",
                "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"
            ),
            # Mumbai
            (
                "The Marine Bay Grand Suites", "Mumbai", "Marine Drive, Churchgate, Mumbai",
                "Iconic luxury facing the Arabian Sea Queens Necklace. World-class modern suites featuring floor-to-ceiling glass windows, infinity ocean view rooftop pool, and 24-hour executive club lounge.",
                8500, 4.9, 320,
                "WiFi, Sea View, Gym, Pool, Bar, Restaurant, AC",
                "https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Juhu Sands Boutique Hotel", "Mumbai", "Juhu Tara Road, Juhu Beach, Mumbai",
                "Located right across from Juhu Beach. Contemporary breezy interiors, sunset terrace bar, swift airport proximity, and renowned culinary dining curated by celebrated Mumbai chefs.",
                6200, 4.7, 175,
                "WiFi, Beach Access, AC, Free Breakfast, Bar, Parking",
                "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Colaba Heritage Inn", "Mumbai", "Near Gateway of India, Colaba Causeway, Mumbai",
                "Classic colonial-era elegance right in Mumbai's historic cultural hub. Walking distance to Gateway of India, art galleries, and lively cafes. Cozy, air-conditioned designer rooms with warm teak aesthetics.",
                3600, 4.3, 110,
                "WiFi, AC, Room Service, City Center, Elevator",
                "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=800&q=80"
            ),
            # Udaipur
            (
                "Lake Pichola Haveli & Terrace", "Udaipur", "Chandpole Ghat, Old City, Udaipur",
                "Perched right on the waters of Lake Pichola. Breathtaking rooftop dining directly facing the City Palace and Jag Mandir. Traditional jharokha bay seating and royal Rajasthani hospitality.",
                5400, 4.8, 195,
                "WiFi, Lake View, Rooftop Restaurant, Pool, AC, Bar",
                "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1587985064135-0366536eab42?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Fateh Sagar Lakeside Manor", "Udaipur", "Rani Road, Fateh Sagar Lake, Udaipur",
                "Serene boutique manor bordered by tranquil lake waters and the Aravalli hills. Enjoy morning jogs along Rani Road, private lakeside high tea, and tastefully furnished heritage suites.",
                4600, 4.7, 130,
                "WiFi, Lake View, Pool, Free Breakfast, Parking, Garden",
                "https://images.unsplash.com/photo-1568084680786-a84f91d1153c?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Aravalli Sunset Heritage Resort", "Udaipur", "Kodiyat Forest Valley Road, Udaipur",
                "A secluded nature haven on the outskirts of Udaipur. Sprawling green lawns, an azure infinity pool against mountain sunsets, evening folk performances, and holistic spa treatments.",
                6800, 4.9, 155,
                "WiFi, Mountain View, Pool, Spa, Bar, Restaurant, Parking",
                "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80"
            ),
            # Delhi
            (
                "The Lutyens Boutique Suites", "Delhi", "Barakhamba Road, Connaught Place, New Delhi",
                "Sophisticated metropolitan stay located in the heart of central Delhi. Walk to Connaught Place inner circle, upscale cafes, and metro links. Features soundproof executive suites and gym.",
                5800, 4.7, 230,
                "WiFi, AC, Gym, Free Breakfast, Metro Access, Room Service",
                "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Haveli Hauz Khas Village", "Delhi", "Deer Park Road, Hauz Khas Village, New Delhi",
                "Artistic boutique retreat right next to the historic Hauz Khas monument reservoir and Deer Park. Chic bohemian rooms, rooftop sunbeds, and immediate access to trendy indie eateries.",
                3400, 4.5, 140,
                "WiFi, AC, Lake View, Cafe, Terrace, Room Service",
                "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Chanakya Royal Ambassador", "Delhi", "Sujan Singh Park, Near Khan Market, New Delhi",
                "Distinguished British colonial legacy hotel near India Gate and Khan Market. Known for sprawling manicured gardens, refined high tea, fine dining Chinese & North Indian cuisine.",
                7200, 4.8, 180,
                "WiFi, AC, Pool, Spa, Fine Dining, Parking, Gym",
                "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80"
            ),
            # Kerala
            (
                "Kumarakom Backwater Lake Resort", "Kerala", "Vembanad Lake Shore, Kumarakom, Kottayam",
                "A paradise set against the peaceful backwaters of Vembanad Lake. Traditional Meenachil architecture villas with private plunge pools, authentic Ayurvedic therapies, and houseboat rides.",
                6500, 4.9, 245,
                "WiFi, Backwaters View, Pool, Ayurvedic Spa, Free Breakfast, Boat Cruise",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1587985064135-0366536eab42?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80"
            ),
            (
                "Munnar Misty Hills Tea Sanctuary", "Kerala", "Tea County Highway, Chithirapuram, Munnar",
                "Perched amidst emerald green tea plantations shrouded in rolling morning mist. Enjoy fresh Nilgiri tea tastings, guided spice plantation walks, and cozy fireplace evenings in the hills.",
                4100, 4.7, 168,
                "WiFi, Mountain View, Tea Garden View, Fireplace, Free Breakfast, Parking",
                "https://images.unsplash.com/photo-1613545325278-f24b0cae1224?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"
            )
        ]

        cursor.executemany('''
            INSERT INTO hotels (name, city, address, description, price_per_night, rating, review_count, amenities, image_main, images_extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', hotels_seed)

        conn.commit()

        # Seed realistic guest reviews
        reviews_seed = [
            (1, "Aarav Sharma", 5, "Amazing experience in North Goa! The beach is just a short 3-minute walk, and the breakfast spread had excellent fresh dosas and tropical fruit."),
            (1, "Priya Patel", 5, "Super clean rooms, very courteous staff. The pool area is peaceful and perfect for evening relaxation."),
            (2, "Rohan Mehta", 4, "Loved the wooden cottages right by Palolem beach. Falling asleep to ocean waves was incredible."),
            (4, "Vikramaditya Rathore", 5, "True Rajasthani royal charm. The evening cultural performance and puppet show in the haveli courtyard was splendid."),
            (5, "Ananya Iyer", 5, "Spectacular view of Amer hills! The dinner under the stars on the terrace was the highlight of our Jaipur trip."),
            (7, "Siddharth Joshi", 5, "Stayed during winter snow. The heating worked flawlessly and the morning views of Solang peaks are breathtaking."),
            (10, "Neha Kulkarni", 5, "Unbeatable Marine Drive location. Stunning sea view from the room window and top-notch hospitality."),
            (13, "Aditya Nair", 5, "Rooftop dining right over Lake Pichola! Watching the illuminated City Palace at night was magical."),
            (19, "Kavita Menon", 5, "The backwaters cruise organized by the resort was serene. Outstanding traditional Kerala fish curry and warm staff.")
        ]

        cursor.executemany('''
            INSERT INTO reviews (hotel_id, user_name, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', reviews_seed)

        conn.commit()

    conn.close()

# Auto-run database check on startup
init_db()

# -----------------------------------------------------------------------------
# Placeholder Routes (Will be fully built out step-by-step)
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    city_filter = request.args.get('city', '').strip()
    conn = get_db()
    
    # Fetch distinct cities with hotel counts for quick filter pills
    cities = conn.execute('''
        SELECT city, COUNT(*) as count 
        FROM hotels 
        GROUP BY city 
        ORDER BY count DESC, city ASC
    ''').fetchall()

    # Filter hotels by city if selected, otherwise show all hotels sorted by rating
    if city_filter:
        hotels = conn.execute('''
            SELECT * FROM hotels 
            WHERE LOWER(city) = LOWER(?) 
            ORDER BY rating DESC
        ''', (city_filter,)).fetchall()
    else:
        hotels = conn.execute('''
            SELECT * FROM hotels 
            ORDER BY rating DESC
        ''').fetchall()

    conn.close()
    return render_template('index.html', hotels=hotels, cities=cities, selected_city=city_filter)

@app.route('/search')
def search():
    # 1. Retrieve query parameters from URL
    city = request.args.get('city', '').strip()
    check_in = request.args.get('check_in', '').strip()
    check_out = request.args.get('check_out', '').strip()
    guests = request.args.get('guests', '2').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    min_rating = request.args.get('min_rating', '').strip()
    selected_amenities = request.args.getlist('amenity')
    sort = request.args.get('sort', 'recommended').strip()

    conn = get_db()

    # 2. Build dynamic SQL query safely with parameter binding (?)
    query = 'SELECT * FROM hotels WHERE 1=1'
    params = []

    if city:
        query += ' AND LOWER(city) = LOWER(?)'
        params.append(city)

    if min_price and min_price.isdigit():
        query += ' AND price_per_night >= ?'
        params.append(int(min_price))

    if max_price and max_price.isdigit():
        query += ' AND price_per_night <= ?'
        params.append(int(max_price))

    if min_rating:
        try:
            rating_val = float(min_rating)
            query += ' AND rating >= ?'
            params.append(rating_val)
        except ValueError:
            pass

    for am in selected_amenities:
        if am.strip():
            query += ' AND amenities LIKE ?'
            params.append(f'%{am.strip()}%')

    # 3. Apply sorting
    if sort == 'price_low':
        query += ' ORDER BY price_per_night ASC'
    elif sort == 'price_high':
        query += ' ORDER BY price_per_night DESC'
    elif sort == 'rating_high':
        query += ' ORDER BY rating DESC, review_count DESC'
    else:
        # Default 'recommended': sort by best rating and review volume
        query += ' ORDER BY rating DESC, review_count DESC'

    hotels = conn.execute(query, params).fetchall()

    # Get distinct cities for destination dropdown
    cities = conn.execute('SELECT DISTINCT city FROM hotels ORDER BY city ASC').fetchall()

    # Standard list of popular filter amenities
    available_amenities = [
        'WiFi', 'Pool', 'AC', 'Free Breakfast', 
        'Mountain View', 'Lake View', 'Beach Access', 
        'Spa', 'Parking', 'Restaurant', 'Bar'
    ]

    conn.close()

    return render_template(
        'search.html',
        hotels=hotels,
        cities=cities,
        city=city,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        selected_amenities=selected_amenities,
        available_amenities=available_amenities,
        sort=sort
    )

@app.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    conn = get_db()
    
    # Fetch hotel details
    hotel = conn.execute('SELECT * FROM hotels WHERE id = ?', (hotel_id,)).fetchone()
    if not hotel:
        conn.close()
        flash('The requested stay could not be found.', 'danger')
        return redirect(url_for('index'))

    # Fetch reviews for this hotel
    reviews = conn.execute('SELECT * FROM reviews WHERE hotel_id = ? ORDER BY id DESC', (hotel_id,)).fetchall()

    # Fetch related hotels in the same city (excluding current hotel)
    related_hotels = conn.execute('''
        SELECT * FROM hotels 
        WHERE LOWER(city) = LOWER(?) AND id != ? 
        ORDER BY rating DESC LIMIT 3
    ''', (hotel['city'], hotel_id)).fetchall()

    conn.close()

    # Prepare extra gallery images and clean amenities list
    extra_images = [img.strip() for img in hotel['images_extra'].split(',') if img.strip()]
    amenities_list = [am.strip() for am in hotel['amenities'].split(',') if am.strip()]

    # Retrieve dates passed from search or homepage
    check_in = request.args.get('check_in', '').strip()
    check_out = request.args.get('check_out', '').strip()
    guests = request.args.get('guests', '2').strip()

    return render_template(
        'hotel_detail.html',
        hotel=hotel,
        extra_images=extra_images,
        amenities_list=amenities_list,
        reviews=reviews,
        related_hotels=related_hotels,
        check_in=check_in,
        check_out=check_out,
        guests=guests
    )

@app.route('/hotel/<int:hotel_id>/review', methods=['POST'])
def add_review(hotel_id):
    user_name = request.form.get('user_name', '').strip()
    rating = request.form.get('rating', '5').strip()
    comment = request.form.get('comment', '').strip()

    # Form validation
    if not user_name or not comment:
        flash('Please fill in both your name and review comment.', 'warning')
        return redirect(url_for('hotel_detail', hotel_id=hotel_id))

    try:
        rating_val = int(rating)
        if rating_val < 1 or rating_val > 5:
            rating_val = 5
    except ValueError:
        rating_val = 5

    conn = get_db()
    cursor = conn.cursor()

    # Insert new review
    cursor.execute('''
        INSERT INTO reviews (hotel_id, user_name, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (hotel_id, user_name, rating_val, comment))

    # Recalculate average rating and total review count
    cursor.execute('''
        SELECT COUNT(*) as count, AVG(rating) as avg_rating 
        FROM reviews 
        WHERE hotel_id = ?
    ''', (hotel_id,))
    stats = cursor.fetchone()
    
    new_count = stats['count']
    new_avg = round(stats['avg_rating'], 1) if stats['avg_rating'] else 5.0

    cursor.execute('''
        UPDATE hotels 
        SET rating = ?, review_count = ? 
        WHERE id = ?
    ''', (new_avg, new_count, hotel_id))

    conn.commit()
    conn.close()

    flash('Thank you! Your guest review has been recorded successfully.', 'success')
    return redirect(url_for('hotel_detail', hotel_id=hotel_id))

@app.route('/checkout/<int:hotel_id>', methods=['GET', 'POST'])
def checkout(hotel_id):
    # Require login for checkout
    if not session.get('user_id'):
        flash('Please log in or create an account to proceed with your reservation.', 'info')
        return redirect(url_for('login', next=request.url))

    conn = get_db()
    hotel = conn.execute('SELECT * FROM hotels WHERE id = ?', (hotel_id,)).fetchone()
    if not hotel:
        conn.close()
        flash('Hotel could not be found.', 'danger')
        return redirect(url_for('index'))

    # Parse and validate dates
    check_in = request.values.get('check_in', '').strip()
    check_out = request.values.get('check_out', '').strip()
    guests = request.values.get('guests', '2').strip()

    try:
        d1 = datetime.strptime(check_in, '%Y-%m-%d').date()
        d2 = datetime.strptime(check_out, '%Y-%m-%d').date()
        nights = (d2 - d1).days
        if nights <= 0:
            nights = 1
            d2 = d1 + timedelta(days=1)
            check_out = d2.isoformat()
    except Exception:
        d1 = date.today()
        d2 = d1 + timedelta(days=1)
        nights = 1
        check_in = d1.isoformat()
        check_out = d2.isoformat()

    # Price breakdown calculation
    subtotal = nights * hotel['price_per_night']
    tax = int(round(subtotal * 0.12))  # 12% standard GST
    total_price = subtotal + tax

    # ---------------------------------------------------------
    # POST Request: Process and Validate Reservation
    # ---------------------------------------------------------
    if request.method == 'POST':
        guest_name = request.form.get('guest_name', '').strip()
        guest_email = request.form.get('guest_email', '').strip()
        guest_phone = request.form.get('guest_phone', '').strip()
        payment_method = request.form.get('payment_method', 'Pay at Hotel')

        # Form validations
        if not guest_name or not guest_email or not guest_phone:
            flash('Please fill in your name, email, and mobile number.', 'danger')
            return render_template(
                'checkout.html', hotel=hotel, check_in=check_in, check_out=check_out,
                guests=guests, nights=nights, subtotal=subtotal, tax=tax, total_price=total_price,
                guest_name=guest_name, guest_email=guest_email, guest_phone=guest_phone
            )

        cursor = conn.cursor()

        # =========================================================
        # CRITICAL: Overlapping Date Check (Double Booking Protection)
        # An overlap occurs when:
        # new_check_in < existing_check_out AND new_check_out > existing_check_in
        # =========================================================
        cursor.execute('''
            SELECT id, booking_id, check_in, check_out FROM bookings
            WHERE hotel_id = ? 
              AND status = 'Confirmed'
              AND check_in < ? 
              AND check_out > ?
        ''', (hotel_id, check_out, check_in))

        overlap = cursor.fetchone()
        if overlap:
            conn.close()
            flash(
                f"Booking Conflict: {hotel['name']} is already reserved from {overlap['check_in']} to {overlap['check_out']}. Please pick different dates.",
                'danger'
            )
            return render_template(
                'checkout.html', hotel=hotel, check_in=check_in, check_out=check_out,
                guests=guests, nights=nights, subtotal=subtotal, tax=tax, total_price=total_price,
                guest_name=guest_name, guest_email=guest_email, guest_phone=guest_phone
            )

        # Generate unique human-readable booking ID (e.g., SN-48291)
        booking_id = f"SN-{random.randint(10000, 99999)}"

        # Insert confirmed booking into database
        cursor.execute('''
            INSERT INTO bookings (
                booking_id, user_id, hotel_id, guest_name, guest_email, guest_phone,
                check_in, check_out, guests, total_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')
        ''', (
            booking_id, session['user_id'], hotel_id, guest_name, guest_email, guest_phone,
            check_in, check_out, int(guests) if guests.isdigit() else 2, total_price
        ))

        conn.commit()
        conn.close()

        flash('Your reservation has been confirmed successfully!', 'success')
        return redirect(url_for('booking_confirmation', booking_id=booking_id))

    conn.close()

    # Pre-fill guest info if logged in
    return render_template(
        'checkout.html',
        hotel=hotel,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        nights=nights,
        subtotal=subtotal,
        tax=tax,
        total_price=total_price,
        guest_name=session.get('user_name', ''),
        guest_email=session.get('user_email', ''),
        guest_phone=''
    )

@app.route('/booking/confirmation/<booking_id>')
def booking_confirmation(booking_id):
    if not session.get('user_id'):
        flash('Please log in to view your reservation details.', 'info')
        return redirect(url_for('login'))

    conn = get_db()
    booking = conn.execute('''
        SELECT b.*, h.name as hotel_name, h.city, h.address, h.image_main, h.price_per_night
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.booking_id = ?
    ''', (booking_id,)).fetchone()
    conn.close()

    if not booking:
        flash('Booking receipt could not be found.', 'danger')
        return redirect(url_for('index'))

    # Security check: User can only see their own booking (unless admin)
    if booking['user_id'] != session['user_id'] and not session.get('is_admin'):
        flash('You do not have permission to view this reservation.', 'danger')
        return redirect(url_for('index'))

    return render_template('confirmation.html', booking=booking)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # If already logged in, redirect to index
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Beginner-friendly input validations
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('signup.html', name=name, email=email)

        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'danger')
            return render_template('signup.html', name=name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('signup.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter carefully.', 'danger')
            return render_template('signup.html', name=name, email=email)

        conn = get_db()
        cursor = conn.cursor()

        # Check if email is already registered
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Securely hash the password using Werkzeug
        password_hash = generate_password_hash(password)

        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, 'user')
        ''', (name, email, password_hash))
        
        conn.commit()
        new_user_id = cursor.lastrowid
        conn.close()

        # Set session for seamless login after registration
        session['user_id'] = new_user_id
        session['user_name'] = name
        session['user_email'] = email
        session['is_admin'] = False

        flash(f'Welcome to StayNest, {name}! Your account has been created.', 'success')

        next_url = request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to index
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both your email and password.', 'danger')
            return render_template('login.html', email=email)

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        # Verify hashed password with check_password_hash
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['is_admin'] = (user['role'] == 'admin')

            flash(f"Welcome back, {user['name']}!", 'success')

            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            if session['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please verify and try again.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/my-bookings')
def my_bookings():
    # Require login to access personal bookings
    if not session.get('user_id'):
        flash('Please log in to view and manage your reservations.', 'info')
        return redirect(url_for('login', next=request.url))

    conn = get_db()
    # Fetch all reservations made by the logged-in user
    bookings = conn.execute('''
        SELECT b.*, h.name as hotel_name, h.city, h.address, h.image_main, h.price_per_night
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        WHERE b.user_id = ?
        ORDER BY b.id DESC
    ''', (session['user_id'],)).fetchall()

    # Calculate status counts for UI summary pills
    total_count = len(bookings)
    confirmed_count = sum(1 for b in bookings if b['status'] == 'Confirmed')
    cancelled_count = sum(1 for b in bookings if b['status'] == 'Cancelled')

    conn.close()

    return render_template(
        'my_bookings.html',
        bookings=bookings,
        total_count=total_count,
        confirmed_count=confirmed_count,
        cancelled_count=cancelled_count
    )

@app.route('/booking/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    # Require login
    if not session.get('user_id'):
        flash('Please log in to manage your bookings.', 'info')
        return redirect(url_for('login'))

    conn = get_db()
    booking = conn.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()

    if not booking:
        conn.close()
        flash('Reservation could not be found.', 'danger')
        return redirect(url_for('my_bookings'))

    # Security check: User can only cancel their own reservation unless they are an admin
    if booking['user_id'] != session['user_id'] and not session.get('is_admin'):
        conn.close()
        flash('Security Alert: You can only cancel your own reservations.', 'danger')
        return redirect(url_for('my_bookings'))

    # Update reservation status to Cancelled
    conn.execute('''
        UPDATE bookings 
        SET status = 'Cancelled' 
        WHERE id = ?
    ''', (booking_id,))
    conn.commit()
    conn.close()

    flash(f"Reservation #{booking['booking_id']} has been cancelled successfully. Your selected dates have been released.", 'success')
    return redirect(url_for('my_bookings'))

# -----------------------------------------------------------------------------
# Admin Portal & Hotel Management (Step 8)
# Protected by role='admin' check
# -----------------------------------------------------------------------------

@app.route('/admin')
def admin_dashboard():
    # Enforce admin authentication
    if not session.get('is_admin'):
        flash('Access Denied: Administrator credentials required to access this portal.', 'danger')
        return redirect(url_for('login', next=request.url))

    conn = get_db()
    
    # 1. Fetch all hotels
    hotels = conn.execute('SELECT * FROM hotels ORDER BY id DESC').fetchall()
    
    # 2. Fetch all system bookings
    bookings = conn.execute('''
        SELECT b.*, h.name as hotel_name, h.city
        FROM bookings b
        JOIN hotels h ON b.hotel_id = h.id
        ORDER BY b.id DESC
    ''').fetchall()

    # 3. Aggregate KPI metrics
    hotel_count = len(hotels)
    booking_count = len(bookings)
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    rev_row = conn.execute("SELECT SUM(total_price) FROM bookings WHERE status = 'Confirmed'").fetchone()
    total_revenue = rev_row[0] if rev_row and rev_row[0] else 0

    conn.close()

    return render_template(
        'admin_dashboard.html',
        hotels=hotels,
        bookings=bookings,
        hotel_count=hotel_count,
        booking_count=booking_count,
        user_count=user_count,
        total_revenue=total_revenue
    )

@app.route('/admin/hotel/add', methods=['GET', 'POST'])
def admin_add_hotel():
    if not session.get('is_admin'):
        flash('Access Denied: Admin privileges required.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip()
        description = request.form.get('description', '').strip()
        price_str = request.form.get('price_per_night', '').strip()
        amenities = request.form.get('amenities', '').strip()
        image_main = request.form.get('image_main', '').strip()

        # Input validations
        if not name or not city or not address or not description or not price_str or not image_main:
            flash('Please fill in all required hotel fields.', 'danger')
            return render_template('admin_hotel_form.html', mode='add', hotel=request.form)

        try:
            price_per_night = int(price_str)
            if price_per_night <= 0:
                raise ValueError()
        except ValueError:
            flash('Price per night must be a valid positive number.', 'danger')
            return render_template('admin_hotel_form.html', mode='add', hotel=request.form)

        # Default extra images if not supplied
        images_extra = "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80,https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80"

        conn = get_db()
        conn.execute('''
            INSERT INTO hotels (name, city, address, description, price_per_night, rating, review_count, amenities, image_main, images_extra)
            VALUES (?, ?, ?, ?, ?, 4.8, 0, ?, ?, ?)
        ''', (name, city, address, description, price_per_night, amenities, image_main, images_extra))
        conn.commit()
        conn.close()

        flash(f'Hotel "{name}" has been added to StayNest successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_hotel_form.html', mode='add', hotel={})

@app.route('/admin/hotel/edit/<int:hotel_id>', methods=['GET', 'POST'])
def admin_edit_hotel(hotel_id):
    if not session.get('is_admin'):
        flash('Access Denied: Admin privileges required.', 'danger')
        return redirect(url_for('login'))

    conn = get_db()
    hotel = conn.execute('SELECT * FROM hotels WHERE id = ?', (hotel_id,)).fetchone()

    if not hotel:
        conn.close()
        flash('Hotel record not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip()
        description = request.form.get('description', '').strip()
        price_str = request.form.get('price_per_night', '').strip()
        amenities = request.form.get('amenities', '').strip()
        image_main = request.form.get('image_main', '').strip()

        if not name or not city or not address or not description or not price_str or not image_main:
            conn.close()
            flash('Please fill in all required fields.', 'danger')
            return render_template('admin_hotel_form.html', mode='edit', hotel=request.form, hotel_id=hotel_id)

        try:
            price_per_night = int(price_str)
        except ValueError:
            conn.close()
            flash('Price per night must be a valid number.', 'danger')
            return render_template('admin_hotel_form.html', mode='edit', hotel=request.form, hotel_id=hotel_id)

        conn.execute('''
            UPDATE hotels
            SET name = ?, city = ?, address = ?, description = ?, price_per_night = ?, amenities = ?, image_main = ?
            WHERE id = ?
        ''', (name, city, address, description, price_per_night, amenities, image_main, hotel_id))
        conn.commit()
        conn.close()

        flash(f'Hotel "{name}" has been updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    conn.close()
    return render_template('admin_hotel_form.html', mode='edit', hotel=hotel, hotel_id=hotel_id)

@app.route('/admin/hotel/delete/<int:hotel_id>', methods=['POST'])
def admin_delete_hotel(hotel_id):
    if not session.get('is_admin'):
        flash('Access Denied: Admin privileges required.', 'danger')
        return redirect(url_for('login'))

    conn = get_db()
    hotel = conn.execute('SELECT name FROM hotels WHERE id = ?', (hotel_id,)).fetchone()

    if hotel:
        hotel_name = hotel['name']
        # Delete related reviews and the hotel
        conn.execute('DELETE FROM reviews WHERE hotel_id = ?', (hotel_id,))
        conn.execute('DELETE FROM bookings WHERE hotel_id = ?', (hotel_id,))
        conn.execute('DELETE FROM hotels WHERE id = ?', (hotel_id,))
        conn.commit()
        flash(f'Hotel "{hotel_name}" and its associated records have been deleted.', 'info')
    else:
        flash('Hotel record not found.', 'danger')

    conn.close()
    return redirect(url_for('admin_dashboard'))

# -----------------------------------------------------------------------------
# 404 Custom Error Handler
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# -----------------------------------------------------------------------------
# Local Run Server
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Local dev server
    app.run(debug=True, port=5000)
