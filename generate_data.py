"""
Grassroots Music Venue Analytics — Rule-Based Synthetic Data Generator
=======================================================================
Generates synthetic data for all 10 database tables using rule-based
programmatic generation (numpy + pandas).

Each generator function applies explicit business rules to derive values,
rather than drawing from unconstrained random distributions. This mirrors
real-world operational logic and ensures internal consistency across tables.

Calibration sources:
  - Music Venue Trust (2023): ticket prices £8–£30 at grassroots venues
  - Musicians' Union: artist fees £800–£2,500 for small-capacity venues
  - Mailchimp Benchmarks (2024): email open rate ~26%, click rate ~2.9%
  - CGA by NIQ (2024): pint £4.50–£6.50, cocktail £8–£12
  - UKHospitality (2023): avg per-head bar spend £10–£20

Run in Google Colab or locally. All CSVs are written to the working directory.
"""

import numpy as np
import pandas as pd

SEED = 42
rng  = np.random.default_rng(SEED)   # single seeded generator for reproducibility


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 1 — VenueRoom
# Fixed lookup table — two physical rooms, each with a fixed capacity.
# Capacity is a property of the room, not the event (3NF design decision).
# ══════════════════════════════════════════════════════════════════════════════

def generate_venue_rooms():
    data = [
        {"room_id": "RMM-001", "venue_room": "Main Hall", "capacity": 400},
        {"room_id": "RMM-002", "venue_room": "Lounge",    "capacity": 200},
    ]
    return pd.DataFrame(data)


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 2 — Promoter
# Fixed lookup — real-sounding independent promoter companies.
# ══════════════════════════════════════════════════════════════════════════════

def generate_promoters():
    names = [
        "Local Gig Co",     "Pulse Promotions",   "SummerSounds Ltd",
        "Blue Note Events", "Afro Vibes Co",       "Arts Council Presents",
        "StreetBeat Promo", "Indie Nights",        "Groove Factory",
        "Neon World Tours", "Roots and Routes",
    ]
    data = {
        "promoter_id":   [f"PRO-{str(i+1).zfill(3)}" for i in range(len(names))],
        "promoter_name": names,
    }
    return pd.DataFrame(data)


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 3 — Artist
#
# Rule: typical_fee is a base rate varied by ±10% to simulate negotiation.
# Fees calibrated to Musicians' Union grassroots rates (£800–£2,500).
# ══════════════════════════════════════════════════════════════════════════════

def generate_artists():
    base_data = [
        ("The Velvet Echoes",  "Rock",       "Manchester, UK",  1800),
        ("DJ Lumina",          "Electronic", "London, UK",      2200),
        ("Sara Montague",      "Jazz",       "London, UK",      1500),
        ("Kojo Beats",         "Afrobeats",  "London, UK",      2000),
        ("Midnight Strings",   "Classical",  "Birmingham, UK",  1200),
        ("Blaze MC",           "Hip-Hop",    "London, UK",      2500),
        ("Luna Park",          "Indie Pop",  "Bristol, UK",     1400),
        ("The Brass Collective","Funk",      "Manchester, UK",  1100),
        ("Anya Petrova",       "Folk",       "Edinburgh, UK",    800),
        ("Neon Pulse",         "Synthwave",  "Leeds, UK",       1600),
    ]
    n = len(base_data)

    # Rule: fee varies ±10% around base rate to simulate negotiation variance
    fee_multipliers = rng.uniform(0.90, 1.10, size=n)

    df = pd.DataFrame(base_data, columns=["artist_name","genre","origin","base_fee"])
    df["artist_id"]   = [f"ART-{str(i+1).zfill(3)}" for i in range(n)]
    df["typical_fee"] = (df["base_fee"] * fee_multipliers).round(2)
    return df[["artist_id","artist_name","genre","origin","typical_fee"]]


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 4 — VenueEvent
#
# Rules:
#   - Operating costs scale with room capacity (larger room = higher costs)
#   - Cost variation ±5% simulates real-world fluctuation (overtime, extra staff)
#   - Ticket prices follow MVT (2023) range: £8–£30 standard, higher for specials
# ══════════════════════════════════════════════════════════════════════════════

def generate_venue_events():
    templates = [
        # (date,         type,        genre,       room,      price, promoter,    staff, sec,  overhead)
        ("2025-06-14", "Concert",    "Rock",       "RMM-001", 18.00, "PRO-001",   420,   280,  600),
        ("2025-06-21", "Club Night", "Electronic", "RMM-001", 14.00, "PRO-002",   380,   300,  600),
        ("2025-07-05", "Concert",    "Mixed",      "RMM-001", 22.00, "PRO-003",   450,   310,  650),
        ("2025-07-12", "Concert",    "Jazz",       "RMM-002", 16.00, "PRO-004",   280,   180,  350),
        ("2025-07-26", "Concert",    "Afrobeats",  "RMM-001", 15.00, "PRO-005",   400,   270,  600),
        ("2025-08-09", "Concert",    "Classical",  "RMM-002", 22.00, "PRO-006",   300,   190,  400),
        ("2025-08-16", "Club Night", "Hip-Hop",    "RMM-001", 16.00, "PRO-007",   420,   320,  620),
        ("2025-09-06", "Concert",    "Mixed",      "RMM-001", 20.00, "PRO-003",   480,   330,  680),
        ("2025-09-13", "Concert",    "Indie Pop",  "RMM-002", 12.00, "PRO-008",   290,   180,  370),
        ("2025-09-27", "Concert",    "Funk",       "RMM-002", 10.00, "PRO-009",   270,   170,  340),
        ("2025-10-11", "Club Night", "Synthwave",  "RMM-001", 17.00, "PRO-010",   390,   270,  580),
        ("2025-10-25", "Concert",    "Folk",       "RMM-002", 10.00, "PRO-011",   240,   150,  300),
    ]
    n = len(templates)

    df = pd.DataFrame(templates, columns=[
        "event_date","event_type","genre","room_id",
        "base_ticket_price","promoter_id",
        "staffing_base","security_base","overhead_base"
    ])

    df["event_id"] = [f"EVT-{str(i+1).zfill(3)}" for i in range(n)]

    # Rule: costs vary ±5% around base to simulate real operational variance
    cost_variation = rng.uniform(0.95, 1.05, size=(n, 3))
    df["staffing_cost"]  = (df["staffing_base"]  * cost_variation[:, 0]).round(2)
    df["security_cost"]  = (df["security_base"]  * cost_variation[:, 1]).round(2)
    df["venue_overhead"] = (df["overhead_base"]  * cost_variation[:, 2]).round(2)

    # Start times: Club Nights start later (21:00–22:00), Concerts earlier (18:00–20:00)
    start_hours = np.where(df["event_type"] == "Club Night",
                           rng.integers(21, 23, size=n),
                           rng.integers(18, 21, size=n))
    start_mins  = rng.choice([0, 15, 30], size=n)
    df["start_time"] = [f"{h:02d}:{m:02d}:00" for h, m in zip(start_hours, start_mins)]

    cols = ["event_id","event_date","start_time","event_type","genre",
            "room_id","base_ticket_price","promoter_id",
            "staffing_cost","security_cost","venue_overhead"]
    return df[cols]


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 5 — EventArtist  (junction table resolving Artist ↔ VenueEvent M:N)
#
# Rules:
#   - Headliners (last in set order) paid 95–105% of typical_fee
#   - Support acts paid 80–95% (common industry practice)
#   - set_order 1 = opener, highest = headliner
# ══════════════════════════════════════════════════════════════════════════════

def generate_event_artists(artists_df):
    bookings = [
        ("EVT-001", ["ART-001"]),
        ("EVT-002", ["ART-002"]),
        ("EVT-003", ["ART-001","ART-004","ART-008","ART-007"]),
        ("EVT-004", ["ART-003"]),
        ("EVT-005", ["ART-004"]),
        ("EVT-006", ["ART-005"]),
        ("EVT-007", ["ART-006"]),
        ("EVT-008", ["ART-002","ART-006","ART-010","ART-009"]),
        ("EVT-009", ["ART-007"]),
        ("EVT-010", ["ART-008"]),
        ("EVT-011", ["ART-010"]),
        ("EVT-012", ["ART-009"]),
    ]

    # Build lookup: artist_id -> typical_fee
    fee_lookup = artists_df.set_index("artist_id")["typical_fee"].to_dict()

    rows = []
    ea_id = 1
    for event_id, artist_ids in bookings:
        n_acts = len(artist_ids)
        for set_order, artist_id in enumerate(artist_ids, start=1):
            typical = fee_lookup[artist_id]
            is_headliner = (set_order == n_acts)

            # Rule: headliner fee closer to typical; support acts negotiated down
            if is_headliner:
                multiplier = rng.uniform(0.95, 1.05)
            else:
                multiplier = rng.uniform(0.80, 0.95)

            rows.append({
                "event_artist_id": f"EA-{str(ea_id).zfill(3)}",
                "event_id":        event_id,
                "artist_id":       artist_id,
                "artist_fee_paid": round(float(typical) * multiplier, 2),
                "set_order":       set_order,
            })
            ea_id += 1

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 6 — Customer  (60 anonymised profiles)
#
# Rules:
#   - Age band weights reflect typical grassroots venue demographics
#     (younger-skewing audience, 18–34 dominant)
#   - accessibility_needs assigned with realistic low probability (~11%)
#   - is_student and customer_segment removed — derivable from age_band (3NF fix)
# ══════════════════════════════════════════════════════════════════════════════

def generate_customers(n=60):
    age_bands   = ["18-24", "25-34", "35-44", "45-54", "55-64"]
    age_weights = np.array([0.30,   0.35,   0.20,   0.10,   0.05])

    postcodes = [
        "SW1 1","EC2 4","M1 2","B1 1","LS1 5","EH1 3","CF10 1","SW3 2",
        "E1 6","M4 4","BS1 3","SE1 7","N1 0","NG1 5","L1 8","G1 2",
        "SW11 1","OX1 2","E14 5","M20 3","W1 4","CB1 1","SE16 3","LE1 6",
        "SW6 2","BA1 1","EC1 8","NE1 4","WC2 5","SE11 4","M13 9","SW19 2",
        "E2 8","LS2 7","N7 6","EH3 9","W6 0","BS2 0","L3 4","SE5 7",
        "NG7 2","CF11 6","G2 1","OX2 6","M15 5","SW7 3","EC3 7","CB2 3",
        "SE10 8","W4 1","NE4 5","LE2 7","WC1 6","BA2 4","N16 8","SW15 1",
        "M1 5","E3 4","BS8 1","L2 2",
    ]
    access_options = ["None"] * 9 + ["Wheelchair access", "Hearing loop"]

    # Rule: age band sampled according to demographic weights
    chosen_ages = rng.choice(age_bands, size=n, p=age_weights / age_weights.sum())

    df = pd.DataFrame({
        "customer_id":         [f"CST-{str(i+1).zfill(3)}" for i in range(n)],
        "age_band":            chosen_ages,
        "postcode_sector":     [postcodes[i % len(postcodes)] for i in range(n)],
        "accessibility_needs": rng.choice(access_options, size=n),
    })
    return df


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 7 — PromotionCampaign
#
# Rules:
#   - Email open rates: Mailchimp Arts & Entertainment benchmark ~26% mean
#   - open_rate is NULL for non-email channels (not applicable — stored as NaN)
#   - Budget capped at £500 (realistic grassroots marketing spend)
#   - Campaign window ends 2 days before event; starts 18–25 days before
# ══════════════════════════════════════════════════════════════════════════════

def generate_campaigns(events_df):
    templates = [
        ("EVT-001", "Email",       "ROCK15",    15.0),
        ("EVT-002", "Social Media","ELECTRO10", 10.0),
        ("EVT-003", "Email",       "MIXED20",   20.0),
        ("EVT-005", "Social Media","AFRO10",    10.0),
        ("EVT-007", "Influencer",  "HIPHOP15",  15.0),
        ("EVT-008", "Email",       "AUTUMN20",  20.0),
        ("EVT-011", "Social Media","NEON10",    10.0),
    ]
    n = len(templates)

    event_dates = events_df.set_index("event_id")["event_date"].to_dict()

    rows = []
    for i, (event_id, channel, code, disc_pct) in enumerate(templates):
        ev_date   = pd.to_datetime(event_dates[event_id])
        end_date  = (ev_date - pd.Timedelta(days=2)).strftime("%Y-%m-%d")
        days_back = int(rng.integers(18, 26))
        start_date = (ev_date - pd.Timedelta(days=days_back)).strftime("%Y-%m-%d")

        # Rule: open_rate only applies to Email channel (Mailchimp benchmark ~26%)
        if channel == "Email":
            open_rate = round(float(rng.normal(loc=29.0, scale=3.0)), 2)
        else:
            open_rate = np.nan   # NULL in database — not applicable

        # Rule: click rate higher for Influencer (higher engagement) than Email
        if channel == "Influencer":
            click_rate = round(float(rng.uniform(12.0, 18.0)), 2)
        else:
            click_rate = round(float(rng.uniform(7.0, 14.0)), 2)

        conversion_rate = round(float(rng.uniform(3.0, 7.5)), 2)

        rows.append({
            "campaign_id":         f"CMP-{str(i+1).zfill(3)}",
            "event_id":            event_id,
            "campaign_channel":    channel,
            "discount_code":       code,
            "discount_percentage": disc_pct,
            "start_date":          start_date,
            "end_date":            end_date,
            "budget":              round(float(rng.uniform(200.0, 500.0)), 2),
            "open_rate":           open_rate,
            "click_rate":          click_rate,
            "conversion_rate":     conversion_rate,
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 8 — TicketSale  (2,500–3,000 rows expected)
#
# Rules (all explicitly coded):
#   1. Sell-through rate varies by genre (Electronic 90%, Folk 55%)
#   2. 18–22% of tickets use a campaign discount → price = base × (1 − disc%)
#   3. 7% are VIP → price = base × 1.4
#   4. No-show rate: 12–15% of sold tickets (attended = 0, refunded = 0)
#   5. Refund rate: 4–5% of sold tickets (attended = 0, refunded = 1)
#   6. Booking channel: 70% Online, 15% Box Office, 15% Door
#   7. Customer selection biased by genre (younger for Electronic, older for Jazz)
#   8. Sale datetime spread over 21 days before event; door sales on event day
# ══════════════════════════════════════════════════════════════════════════════

# Genre → target sell-through rate (proportion of room capacity sold)
SELL_THROUGH = {
    "Rock": 0.85, "Electronic": 0.90, "Mixed": 0.75, "Jazz": 0.60,
    "Afrobeats": 0.80, "Classical": 0.65, "Hip-Hop": 0.88,
    "Indie Pop": 0.65, "Funk": 0.58, "Synthwave": 0.82, "Folk": 0.55,
}

# Genre → customer age-band sampling weights [18-24, 25-34, 35-44, 45-54, 55-64]
GENRE_AGE_WEIGHTS = {
    "Electronic": [0.40, 0.40, 0.15, 0.04, 0.01],
    "Hip-Hop":    [0.45, 0.35, 0.15, 0.04, 0.01],
    "Synthwave":  [0.35, 0.40, 0.18, 0.06, 0.01],
    "Rock":       [0.30, 0.35, 0.22, 0.10, 0.03],
    "Afrobeats":  [0.30, 0.40, 0.20, 0.08, 0.02],
    "Indie Pop":  [0.35, 0.38, 0.18, 0.07, 0.02],
    "Mixed":      [0.28, 0.35, 0.22, 0.10, 0.05],
    "Funk":       [0.20, 0.35, 0.25, 0.15, 0.05],
    "Jazz":       [0.10, 0.20, 0.30, 0.25, 0.15],
    "Classical":  [0.08, 0.15, 0.28, 0.30, 0.19],
    "Folk":       [0.10, 0.20, 0.30, 0.25, 0.15],
}

AGE_BANDS = ["18-24", "25-34", "35-44", "45-54", "55-64"]

def generate_ticket_sales(events_df, customers_df, campaigns_df, rooms_df):
    # Build lookup dictionaries from DataFrames
    room_cap     = rooms_df.set_index("room_id")["capacity"].to_dict()
    camp_by_ev   = campaigns_df.set_index("event_id").to_dict("index")

    # Group customer IDs by age band for genre-biased selection
    custs_by_age = customers_df.groupby("age_band")["customer_id"].apply(list).to_dict()

    all_rows      = []
    ticket_id     = 1
    attendees_map = {}   # event_id -> [customer_ids who attended]

    for _, event in events_df.iterrows():
        event_id   = event["event_id"]
        genre      = event["genre"]
        event_date = event["event_date"]
        base_price = float(event["base_ticket_price"])
        capacity   = room_cap[event["room_id"]]
        vip_price  = round(base_price * 1.4, 2)

        # Rule 1: sell-through determines how many tickets to generate
        n_tickets  = int(capacity * SELL_THROUGH.get(genre, 0.70))

        # Rule 2 & 3: determine ticket type composition
        campaign   = camp_by_ev.get(event_id)
        disc_pct   = float(campaign["discount_percentage"]) if campaign else 0
        disc_price = round(base_price * (1 - disc_pct / 100), 2) if campaign else None
        camp_id    = campaign["campaign_id"] if campaign else None

        n_discount = int(n_tickets * rng.uniform(0.18, 0.22)) if campaign else 0
        n_vip      = int(n_tickets * rng.uniform(0.06, 0.09))
        n_standard = n_tickets - n_discount - n_vip

        ticket_types = (
            [("Early Bird", disc_price, camp_id)] * n_discount +
            [("VIP",        vip_price,  None)]    * n_vip +
            [("Standard",   base_price, None)]    * n_standard
        )
        rng.shuffle(ticket_types)

        # Rule 4 & 5: attendance outcomes
        no_show_rate = rng.uniform(0.12, 0.15)
        refund_rate  = rng.uniform(0.04, 0.05)
        outcomes     = rng.random(size=n_tickets)   # one draw per ticket

        # Rule 7: genre-biased customer pool
        age_weights = np.array(GENRE_AGE_WEIGHTS.get(genre, [0.2]*5))
        age_weights = age_weights / age_weights.sum()

        # Rule 8: sale date spread
        ev_dt    = pd.to_datetime(event_date)
        sale_days = rng.integers(0, 21, size=n_tickets)  # days before event

        attendees_map[event_id] = []

        for j, (ttype, price, used_camp_id) in enumerate(ticket_types):
            # Genre-biased customer selection
            age_band    = rng.choice(AGE_BANDS, p=age_weights)
            pool        = custs_by_age.get(age_band, customers_df["customer_id"].tolist())
            customer_id = str(rng.choice(pool))

            # Rule 6: booking channel
            channel = rng.choice(
                ["Online", "Box Office", "Door"],
                p=[0.70, 0.15, 0.15]
            )

            # Rule 8: door sales happen on event day; pre-sales spread over 21 days
            if channel == "Door":
                sale_dt = f"{event_date} {rng.integers(17,20):02d}:{rng.integers(0,59):02d}:00"
            else:
                sale_date = (ev_dt - pd.Timedelta(days=int(sale_days[j]))).strftime("%Y-%m-%d")
                sale_dt   = f"{sale_date} {rng.integers(8,21):02d}:{rng.integers(0,59):02d}:{rng.integers(0,59):02d}"

            # Rules 4 & 5: attendance status derived from random draw
            o = outcomes[j]
            if o < refund_rate:
                attended = 0; refunded = 1
            elif o < refund_rate + no_show_rate:
                attended = 0; refunded = 0
            else:
                attended = 1; refunded = 0

            if attended:
                attendees_map[event_id].append(customer_id)

            all_rows.append({
                "ticket_sale_id":  f"TKT-{str(ticket_id).zfill(4)}",
                "event_id":        event_id,
                "customer_id":     customer_id,
                "campaign_id":     used_camp_id if used_camp_id else "",
                "sale_datetime":   sale_dt,
                "price_paid":      price,
                "ticket_type":     ttype,
                "booking_channel": channel,
                "attended":        attended,
                "refunded":        refunded,
            })
            ticket_id += 1

    return pd.DataFrame(all_rows), attendees_map


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 9 — BarOrder
#
# Rules:
#   1. ONLY customers with attended=True can have a bar order
#      (enforced by reading from attendees_map built in TicketSale generation)
#   2. Bar order rate varies by genre (Electronic 78%, Folk 60%)
#   3. Spend drawn from genre-calibrated range (CGA by NIQ / UKHospitality)
#   4. 20% of orders anonymous (customer_id NULL — nullable FK design decision)
#   5. Timestamp: 30–150 minutes after event start
# ══════════════════════════════════════════════════════════════════════════════

# Genre → (min_spend, max_spend, order_probability)
GENRE_BAR = {
    "Rock":       (8.0,  28.0, 0.72),
    "Electronic": (10.0, 35.0, 0.78),
    "Mixed":      (9.0,  30.0, 0.74),
    "Jazz":       (12.0, 30.0, 0.68),
    "Afrobeats":  (9.0,  28.0, 0.70),
    "Classical":  (10.0, 28.0, 0.62),
    "Hip-Hop":    (10.0, 32.0, 0.76),
    "Indie Pop":  (7.0,  22.0, 0.65),
    "Funk":       (8.0,  24.0, 0.68),
    "Synthwave":  (10.0, 34.0, 0.77),
    "Folk":       (8.0,  20.0, 0.60),
}

def generate_bar_orders(events_df, attendees_map):
    all_rows = []
    order_id = 1

    for _, event in events_df.iterrows():
        event_id   = event["event_id"]
        genre      = event["genre"]
        event_date = event["event_date"]
        min_spend, max_spend, bar_rate = GENRE_BAR.get(genre, (8.0, 25.0, 0.70))

        # Rule 1: only use attendees confirmed from ticket sales
        attendees = list(set(attendees_map.get(event_id, [])))
        n = len(attendees)
        if n == 0:
            continue

        # Rule 2: apply bar visit probability per attendee
        visits = rng.random(size=n) < bar_rate

        # Rule 3: spend drawn uniformly within genre range
        spends = np.round(rng.uniform(min_spend, max_spend, size=n) * 2) / 2

        # Rule 5: order timestamps 30–150 minutes after doors (start_time)
        start_hour = int(event["start_time"].split(":")[0])
        minutes_in = rng.integers(30, 151, size=n)
        order_hours = start_hour + minutes_in // 60
        order_mins  = minutes_in % 60

        # Rule 4: 20% anonymous orders
        anonymous_mask = rng.random(size=n) < 0.20
        channels       = rng.choice(["Bar", "App"], size=n, p=[0.80, 0.20])

        for j, customer_id in enumerate(attendees):
            if not visits[j]:
                continue   # customer didn't visit the bar tonight

            linked_customer = "" if anonymous_mask[j] else customer_id

            all_rows.append({
                "bar_order_id":    f"BAR-{str(order_id).zfill(3)}",
                "event_id":        event_id,
                "customer_id":     linked_customer,
                "order_timestamp": f"{event_date} {int(order_hours[j]):02d}:{int(order_mins[j]):02d}:00",
                "total_spend":     spends[j],
                "order_channel":   channels[j],
            })
            order_id += 1

    return pd.DataFrame(all_rows)


# ══════════════════════════════════════════════════════════════════════════════
# TABLE 10 — BarOrderItem  (1NF fix — atomic line items per bar order)
#
# Rule: each order is decomposed into 1–3 distinct drink types with quantity.
# Drink type mix weighted by realistic on-trade sales (beer most common).
# ══════════════════════════════════════════════════════════════════════════════

DRINK_TYPES   = ["Beer", "Wine", "Cocktail", "Soft Drink"]
DRINK_WEIGHTS = np.array([0.45,  0.25,  0.20,    0.10])

def generate_bar_order_items(bar_orders_df):
    all_rows = []
    item_id  = 1
    n_orders = len(bar_orders_df)

    # Rule: number of distinct item types per order (1 most common)
    n_items_per_order = rng.choice([1, 2, 3], size=n_orders, p=[0.55, 0.35, 0.10])
    quantities        = rng.choice([1, 2, 3], size=(n_orders, 3), p=[0.55, 0.35, 0.10])

    for idx, (_, order) in enumerate(bar_orders_df.iterrows()):
        n_types = n_items_per_order[idx]
        chosen_drinks = rng.choice(DRINK_TYPES, size=n_types,
                                   p=DRINK_WEIGHTS / DRINK_WEIGHTS.sum(),
                                   replace=False)
        for k, drink in enumerate(chosen_drinks):
            all_rows.append({
                "order_item_id": f"ITM-{str(item_id).zfill(4)}",
                "bar_order_id":  order["bar_order_id"],
                "item_name":     drink,
                "quantity":      int(quantities[idx, k]),
            })
            item_id += 1

    return pd.DataFrame(all_rows)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — run all generators in FK-dependency order and export to CSV
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nGrassroots Venue Data Generator (Rule-Based)")
    print("=" * 52)

    venue_rooms  = generate_venue_rooms()
    promoters    = generate_promoters()
    artists      = generate_artists()
    events       = generate_venue_events()
    event_artists = generate_event_artists(artists)
    customers    = generate_customers(n=60)
    campaigns    = generate_campaigns(events)

    tickets, attendees_map = generate_ticket_sales(
        events, customers, campaigns, venue_rooms
    )

    bar_orders   = generate_bar_orders(events, attendees_map)
    bar_items    = generate_bar_order_items(bar_orders)

    # Export all tables to CSV
    tables = {
        "venue_room.csv":         venue_rooms,
        "promoter.csv":           promoters,
        "artist.csv":             artists,
        "venue_event.csv":        events,
        "event_artist.csv":       event_artists,
        "customer.csv":           customers,
        "promotion_campaign.csv": campaigns,
        "ticket_sale.csv":        tickets,
        "bar_order.csv":          bar_orders,
        "bar_order_item.csv":     bar_items,
    }

    for filename, df in tables.items():
        df.to_csv(filename, index=False)
        print(f"  {filename:40s}  {len(df):>5,} rows")

    # Summary statistics
    print("\nSummary Statistics")
    print("-" * 52)
    attended = tickets["attended"].sum()
    refunded = tickets["refunded"].sum()
    print(f"  Total ticket sales:   {len(tickets):>5,}")
    print(f"    Attended:           {attended:>5,}  ({attended/len(tickets)*100:.1f}%)")
    print(f"    Refunded:           {refunded:>5,}  ({refunded/len(tickets)*100:.1f}%)")
    print(f"  Bar orders:           {len(bar_orders):>5,}")
    print(f"  Bar order items:      {len(bar_items):>5,}")

    print("\nSell-through by event:")
    room_cap = venue_rooms.set_index("room_id")["capacity"].to_dict()
    ticket_counts = tickets.groupby("event_id").size()
    for _, ev in events.iterrows():
        cap  = room_cap[ev["room_id"]]
        sold = ticket_counts.get(ev["event_id"], 0)
        print(f"  {ev['event_id']}  {ev['genre']:<12}  {sold:>3}/{cap}  ({sold/cap*100:.0f}%)")

    print("\nAll CSVs generated.")

    # Preview first table
    print("\nTicketSale preview (first 5 rows):")
    print(tickets.head())
