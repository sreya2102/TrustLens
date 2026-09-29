import csv
import os
import random

# Set seed for reproducibility
random.seed(42)

# Ensure data directory exists
os.makedirs("ml/data", exist_ok=True)

# Templates for data generation
BENIGN_TEMPLATES = [
    # Tech / Coding blogs
    ("Learn Python Programming: A Step-by-Step Tutorial", 
     "In this tutorial, we will explore the fundamentals of Python programming. Python is a popular, open-source language widely used for data analysis, web development, and artificial intelligence. We will cover variables, loops, control structures, and function definitions. Make sure to download the latest interpreter from the official website and configure your workspace IDE. Practice writing clean code, document your classes and functions, and follow PEP 8 styling conventions to keep your codebase readable and easily maintainable by team members."),
    
    # E-commerce (Safe version)
    ("Wireless Noise Canceling Headphones - Model Pro 5", 
     "Enjoy immersive sound quality with the new Model Pro 5 wireless headphones. Features active noise cancellation, 40-hour battery life, and comfortable over-ear design. Inside the box, you will find a USB-C charging cable, audio cable, and user manual. The headphones come with a standard 1-year manufacturer warranty. Shipping is calculated at checkout. Read customer reviews below to see how other users rate the audio quality, comfort during long usage, and Bluetooth connectivity stability across different devices."),
    
    # Recipe
    ("Classic Chocolate Chip Cookies Recipe", 
     "Preheat your oven to 375 degrees Fahrenheit. In a large bowl, cream together the softened butter, white sugar, and brown sugar until smooth. Add eggs one at a time, then stir in the vanilla extract. Combine flour, baking soda, and salt; gradually blend into the creamed mixture. Fold in the chocolate chips. Drop by rounded spoonfuls onto ungreased cookie sheets. Bake for 9 to 11 minutes or until golden brown. Cool on wire racks. This recipe makes about 24 delicious homemade cookies that the whole family will love."),
    
    # News/Informational
    ("Mars Rover Discovers Ancient Lake Bed Evidence", 
     "Scientists at the space agency have announced that the latest robotic rover has analyzed mineral samples indicating the presence of an ancient lake bed. Using advanced spectrographic instruments, the rover detected clay minerals and sulfate salts that typically form in wet environments. This finding suggests that liquid water may have persisted on the Martian surface for millions of years in the geological past. Researchers are continuing to plan upcoming drilling missions to extract deeper core samples from the crater floor."),
    
    # Corporate
    ("About Us - Innovate Tech Solutions", 
     "At Innovate Tech Solutions, we specialize in delivering enterprise-grade cloud integration, cybersecurity audits, and custom software engineering. Founded in 2018, our team consists of certified architects, engineers, and project managers committed to client success. We value transparency, technical excellence, and sustainable development. Contact us today to schedule a consultation with our experts. Read our case studies to learn how we helped businesses scale their infrastructure and optimize computational workloads."),
    
    # Personal Blog
    ("My Summer Trip to the Swiss Alps", 
     "Last month, I had the incredible opportunity to travel to Switzerland and hike some of the most beautiful trails in the Alps. The mountain air was crisp, and the scenery was absolutely breathtaking. I stayed in a small chalet in Lauterbrunnen and spent my days hiking around Grindelwald and Murren. I captured hundreds of landscape photos and met other hikers from all around the world. It was a truly refreshing vacation away from screens, and I cannot wait to plan my next alpine adventure.")
]

PRIVACY_RISK_TEMPLATES = [
    # Consent walls
    ("Privacy Policy Consent Check", 
     "We use cookies to analyze web traffic. By clicking allow cookies, you consent to our third-party partners and advertising networks tracking your device information and location. This data collection allows us and our marketing partners to build an ad profiling database to show you targeted ads and personalized ads. If you do not agree, we may restrict access to our services. We share your data and share your personal details with external networks to optimize advertising campaigns."),
    
    # Social signups demanding permissions
    ("Connect Your Account - Free Games Portal", 
     "To play free games, please log in with your social account. By connecting, you grant us permission to access contacts, track location, and read device information. We require this consent to personalize gameplay. Our third-party partners and targeted ads networks will collect statistics to serve advertising. We may share with partners your activity data. Ad profiling is enabled by default to improve relevance."),
    
    # Newsletter with small print
    ("Join Our VIP Newsletter - Daily Deals", 
     "Sign up for our newsletter to get daily discounts. By entering your email, you agree that we share your data with marketing partners and third party partners. We track location and gather device information to customize promotional materials. We participate in advertising networks that serve personalized ads. Consent required for data collection is covered under our terms of service. You may receive promotional materials from our marketing affiliates."),
    
    # App download page privacy disclosure
    ("Download PDF Reader Pro - Terms of Use", 
     "Before installing PDF Reader Pro, note that the application will share your personal details with third-party advertising partners. The application is configured to track location, access contacts, and upload device information to our servers. This data collection is necessary for personalized ads profiling and targeted ads delivery. Advertising networks collect this data automatically. If you do not consent, please uninstall the product immediately.")
]

DARK_PATTERN_TEMPLATES = [
    # Countdown timer / Flash sale
    ("Huge E-Commerce Flash Sale - 70% Off", 
     "Act now! Our massive flash sale ends soon. Hurry, offer ends soon and you will miss out. We have only few left in stock, so do not miss out on this deal. Tick-tock, only today, this is your last chance to buy at this price. Running out of stock rapidly! Sale ends in final hours. Hurry up and place your order before the seconds left countdown reaches zero. Only limited time only, buy now!"),
    
    # Scarcity on products
    ("Vintage Leather Boots - Dark Brown", 
     "Only 1 left! High demand for this item, and we have only 2 left in our warehouse. Almost sold out! Selling fast due to low stock. Few remaining, almost gone, so grab these last items before we are completely out of stock. Demand is high, and this item is while supplies last only. Avoid backorder soon. Act now or miss out on these limited quantity designer boots."),
    
    # Flight seat scarcity
    ("Flight from New York to London - Seat Selection", 
     "Hurry! Only 3 left at this low price. Last items available. Flash sale ends, last chance to lock in this economy rate! Only 4 left, almost sold out. Demand is high, 25 people are viewing this flight right now. Don't miss out on this trip. Act now, offer ends soon! Limited time only. Tickets are selling fast!"),
    
    # Ticket vendor
    ("Live Concert Tickets - Front Row Section", 
     "Hurry up! Tick-tock, ticket sales are closing fast. Only 5 left for front row. Last-minute tickets available for final hours. Only few left, running out of seats! Don't miss out. Last chance, sale ends soon! Almost gone. Limited quantity remaining. While supplies last.")
]

SUBSCRIPTION_TRAP_TEMPLATES = [
    # Software subscription
    ("Cloud Storage Service - Signup Page", 
     "Start your 14-day free trial. An auto-renewal applies, and your credit card will be charged a recurring billing fee after the trial. Continuous service means we renew automatically every month. Billed monthly membership fee applies unless you cancel anytime. Recurring billing ensures uninterrupted access. Cancel any time in your profile settings. Billed annually renewal applies at the end of the trial period."),
    
    # Streaming service subscription
    ("StreamCinema Premium Account", 
     "Register for StreamCinema. Try it with a free trial. The subscription will auto-renew automatically. Continuous billing and recurring service charges are billed weekly. The trial period ends in 7 days, after the trial, continuous service billing is activated. We renew automatically and charge a membership fee. Cancel anytime to stop billing."),
    
    # Fitness club membership
    ("GetFit Gym Membership Online Portal", 
     "Join our fitness community! Free trial for the first week, followed by auto-renewal. Continuous billing applies with recurring billing charges. You will be billed monthly for membership fee. Continuous service allows you to visit all gyms. Subscription renews automatically unless canceled. Cancel any time. After the trial period, your auto-renew membership starts.")
]

FINANCIAL_MANIPULATION_TEMPLATES = [
    # Payday loans
    ("Fast Cash Loans - Instant Approval", 
     "Need money? Get instant approval for a guaranteed loan with no risk! Win cash today, claim reward, and double your income. No obligation, get financial freedom. Risk-free cash prize! Make money fast and enjoy easy money. Claim now, guaranteed returns, no risk, free gift. Get rich and make money fast with our quick cash programs."),
    
    # Sweepstakes scams
    ("Congratulations! You Have Won!", 
     "Congratulations! You are our lucky visitor. Claim reward now to win cash. This is a risk-free jackpot! Receive a free gift and claim now to get rich. Easy money and double your income today. No risk, no obligation, guaranteed returns. Make money fast and claim your cash prize immediately. Instant approval for your rewards!"),
    
    # High-yield investment scam
    ("Crypto Profit Multiplier - Double Your Assets", 
     "Welcome to the future of financial freedom! Double your income with our automated crypto trading algorithm. Guaranteed returns with no risk. Make money fast and get rich in days. Risk-free, guaranteed loan options available for premium members. Congratulations on finding this easy money secret. Claim reward, win cash, no obligation. Claim now to start earning.")
]


# We will generate a list of 550 records by mixing and matching templates and keywords
records = []
current_id = 1

# Helper to add a page
def add_record(url, title, text, label, safe, privacy_risky, dark_pattern, subscription_trap, financial_manipulation):
    global current_id
    records.append({
        "id": current_id,
        "url": url,
        "page_title": title,
        "page_text": text,
        "label": label,
        "safe": safe,
        "privacy_risky": privacy_risky,
        "dark_pattern": dark_pattern,
        "subscription_trap": subscription_trap,
        "financial_manipulation": financial_manipulation
    })
    current_id += 1

# Generate Benign (Safe) Pages: Target ~120
safe_urls = [
    "https://techblog.example.com/python-intro",
    "https://cookingcorner.example.net/cookies-recipe",
    "https://spaceinfo.example.org/mars-rover-clay",
    "https://innovatesolutions.example.com/about-us",
    "https://traveldiaries.example.com/swiss-hiking",
    "https://wikipedia.example.org/wiki/Photosynthesis",
    "https://devdocs.example.io/javascript-reference",
    "https://localnews.example.com/community-center-opening",
    "https://fitlife.example.com/healthy-eating-habits",
    "https://gardeningtips.example.net/spring-planting-guide"
]
for i in range(120):
    url = random.choice(safe_urls) + f"?page={i}"
    title_base, text_base = random.choice(BENIGN_TEMPLATES)
    noise = f" Reference ID: {random.randint(1000, 9999)}. This article is for informational purposes only. Published on Section {random.choice(['A', 'B', 'C'])}."
    text = text_base + noise
    title = f"{title_base} | Part {i+1}"
    add_record(url, title, text, "Safe", 1, 0, 0, 0, 0)

# Generate Privacy Risky Pages: Target ~110
privacy_urls = [
    "https://cookies.adsportal.example.com/accept",
    "https://freegames.example.net/connect",
    "https://newsletters.vipdeals.example.com/subscribe",
    "https://pdfreader.softwaredownload.example.org/terms",
    "https://weatherwidgets.example.com/install",
    "https://coupontracker.example.net/signup"
]
for i in range(110):
    url = random.choice(privacy_urls) + f"?session={i}"
    title_base, text_base = random.choice(PRIVACY_RISK_TEMPLATES)
    noise = f" Privacy Version {random.randint(1, 5)}. IP Address logging may apply. User agent string: {random.choice(['Chrome', 'Firefox', 'Safari'])}."
    text = text_base + noise
    title = f"{title_base} - Update {i+1}"
    add_record(url, title, text, "Caution", 0, 1, 0, 0, 0)

# Generate Dark Pattern Pages (Urgency / Scarcity): Target ~110
dark_urls = [
    "https://flashsale.shop.example.com/discounts",
    "https://bootsstore.example.net/item404",
    "https://traveltickets.example.com/checkout",
    "https://liveconcert.example.org/tickets",
    "https://hotelbooking.example.com/reserve",
    "https://gadgetshop.example.net/deal"
]
for i in range(110):
    url = random.choice(dark_urls) + f"?ref={i}"
    title_base, text_base = random.choice(DARK_PATTERN_TEMPLATES)
    noise = f" Order ID: {random.randint(100000, 999999)}. Total item count remaining: {random.randint(1, 5)}."
    text = text_base + noise
    title = f"{title_base} - {i+1}"
    add_record(url, title, text, "Caution", 0, 0, 1, 0, 0)

# Generate Subscription Trap Pages: Target ~110
sub_urls = [
    "https://cloudstorage.example.com/signup",
    "https://streamcinema.example.net/register",
    "https://getfitgym.example.com/join",
    "https://vpnservice.example.org/freetrial",
    "https://productivityapp.example.net/billing"
]
for i in range(110):
    url = random.choice(sub_urls) + f"?trial_id={i}"
    title_base, text_base = random.choice(SUBSCRIPTION_TRAP_TEMPLATES)
    noise = f" Subscription contract code: {random.randint(1000, 9999)}. Secure card payment processed via standard portals."
    text = text_base + noise
    title = f"{title_base} - Trial {i+1}"
    add_record(url, title, text, "Risky", 0, 0, 0, 1, 0)

# Generate Financial Manipulation Pages: Target ~110
fin_urls = [
    "https://fastcash.example.com/loans",
    "https://congratulations.winprize.example.net/claim",
    "https://cryptomultiplier.example.com/double",
    "https://paydayloans.example.org/quickcash",
    "https://luckydraw.example.net/jackpot"
]
for i in range(110):
    url = random.choice(fin_urls) + f"?win_id={i}"
    title_base, text_base = random.choice(FINANCIAL_MANIPULATION_TEMPLATES)
    noise = f" Transaction reference code: {random.randint(10000, 99999)}. Security code verification completed."
    text = text_base + noise
    title = f"{title_base} - Claim {i+1}"
    add_record(url, title, text, "Risky", 0, 0, 0, 0, 1)

# Write to CSV
csv_path = "ml/data/dataset.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "id", "url", "page_title", "page_text", "label",
        "safe", "privacy_risky", "dark_pattern", "subscription_trap", "financial_manipulation"
    ])
    writer.writeheader()
    for rec in records:
        writer.writerow(rec)

print(f"Dataset generated successfully at {csv_path}. Generated {len(records)} records.")
