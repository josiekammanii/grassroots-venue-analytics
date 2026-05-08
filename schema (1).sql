-- ============================================================
-- Grassroots Music Venue Analytics Database
-- Schema Definition (3NF Normalised)
-- ============================================================


-- 1. VenueRoom
--    Stores the physical rooms in the venue.
--    Extracted from VenueEvent to remove the transitive dependency
--    venue_room → capacity (3NF fix).
-- ------------------------------------------------------------
CREATE TABLE VenueRoom (
    room_id       VARCHAR(10)  PRIMARY KEY,
    venue_room    VARCHAR(50)  NOT NULL,
    capacity      INT          NOT NULL
);


-- 2. Promoter
--    Stores promoter details as a separate entity.
--    Extracted from VenueEvent to remove the transitive dependency
--    promoter_name → (any future promoter attributes) (3NF fix).
-- ------------------------------------------------------------
CREATE TABLE Promoter (
    promoter_id   VARCHAR(10)  PRIMARY KEY,
    promoter_name VARCHAR(100) NOT NULL
);


-- 3. Artist
--    Stores artist profile information.
--    typical_fee is the artist's standard asking price,
--    separate from what was actually paid per event (held in EventArtist).
-- ------------------------------------------------------------
CREATE TABLE Artist (
    artist_id    VARCHAR(10)  PRIMARY KEY,
    artist_name  VARCHAR(100) NOT NULL,
    genre        VARCHAR(50),
    origin       VARCHAR(100),
    typical_fee  DECIMAL(8,2)
);


-- 4. VenueEvent
--    Stores each individual event.
--    room_id and promoter_id are foreign keys replacing the
--    raw text columns that caused 3NF violations.
--    capacity is no longer stored here — it belongs to VenueRoom.
-- ------------------------------------------------------------
CREATE TABLE VenueEvent (
    event_id          VARCHAR(10)  PRIMARY KEY,
    event_date        DATE         NOT NULL,
    start_time        TIME,
    event_type        VARCHAR(50),
    genre             VARCHAR(50),
    room_id           VARCHAR(10)  NOT NULL,
    base_ticket_price DECIMAL(6,2),
    promoter_id       VARCHAR(10)  NOT NULL,
    staffing_cost     DECIMAL(8,2),
    security_cost     DECIMAL(8,2),
    venue_overhead    DECIMAL(8,2),
    FOREIGN KEY (room_id)     REFERENCES VenueRoom(room_id),
    FOREIGN KEY (promoter_id) REFERENCES Promoter(promoter_id)
);


-- 5. EventArtist
--    Junction table linking artists to events (many-to-many).
--    artist_fee_paid records what was actually paid on the night,
--    which may differ from the artist's typical_fee.
--    set_order records the running order of acts (1 = opener, highest = headliner).
-- ------------------------------------------------------------
CREATE TABLE EventArtist (
    event_artist_id VARCHAR(10)  PRIMARY KEY,
    event_id        VARCHAR(10)  NOT NULL,
    artist_id       VARCHAR(10)  NOT NULL,
    artist_fee_paid DECIMAL(8,2),
    set_order       INT,
    FOREIGN KEY (event_id)  REFERENCES VenueEvent(event_id),
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)
);


-- 6. Customer
--    Stores anonymised customer profile data.
--    is_student and customer_segment have been removed as both
--    were entirely derivable from age_band — storing them would
--    create redundancy and risk contradictory data (2NF/3NF fix).
-- ------------------------------------------------------------
CREATE TABLE Customer (
    customer_id        VARCHAR(10)  PRIMARY KEY,
    age_band           VARCHAR(20),
    postcode_sector    VARCHAR(10),
    accessibility_needs VARCHAR(100)
);


-- 7. PromotionCampaign
--    Stores marketing campaigns linked to specific events.
--    open_rate is NULL for non-email channels (Social Media,
--    Influencer) as that metric does not apply.
-- ------------------------------------------------------------
CREATE TABLE PromotionCampaign (
    campaign_id         VARCHAR(10)  PRIMARY KEY,
    event_id            VARCHAR(10)  NOT NULL,
    campaign_channel    VARCHAR(50),
    discount_code       VARCHAR(30),
    discount_percentage DECIMAL(4,2),
    start_date          DATE,
    end_date            DATE,
    budget              DECIMAL(8,2),
    open_rate           DECIMAL(5,2),
    click_rate          DECIMAL(5,2),
    conversion_rate     DECIMAL(5,2),
    FOREIGN KEY (event_id) REFERENCES VenueEvent(event_id)
);


-- 8. TicketSale
--    Records every individual ticket purchase.
--    campaign_id is nullable — most tickets are sold without a promotion.
--    attended and refunded default to FALSE.
-- ------------------------------------------------------------
CREATE TABLE TicketSale (
    ticket_sale_id  VARCHAR(10)  PRIMARY KEY,
    event_id        VARCHAR(10)  NOT NULL,
    customer_id     VARCHAR(10)  NOT NULL,
    campaign_id     VARCHAR(10),
    sale_datetime   DATETIME     NOT NULL,
    price_paid      DECIMAL(6,2) NOT NULL,
    ticket_type     VARCHAR(30),
    booking_channel VARCHAR(30),
    attended        BOOLEAN      DEFAULT FALSE,
    refunded        BOOLEAN      DEFAULT FALSE,
    FOREIGN KEY (event_id)    REFERENCES VenueEvent(event_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (campaign_id) REFERENCES PromotionCampaign(campaign_id)
);


-- 9. BarOrder
--    Records each bar transaction during an event.
--    customer_id is nullable to allow anonymous walk-up purchases.
--    The items column has been removed — individual items are now
--    stored atomically in BarOrderItem (1NF fix).
-- ------------------------------------------------------------
CREATE TABLE BarOrder (
    bar_order_id    VARCHAR(10)  PRIMARY KEY,
    event_id        VARCHAR(10)  NOT NULL,
    customer_id     VARCHAR(10),
    order_timestamp DATETIME     NOT NULL,
    total_spend     DECIMAL(6,2) NOT NULL,
    order_channel   VARCHAR(30),
    FOREIGN KEY (event_id)    REFERENCES VenueEvent(event_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);


-- 10. BarOrderItem
--     Stores individual drink items per bar order atomically.
--     Extracted from BarOrder to resolve the 1NF violation where
--     multiple items were stored as a single text string (e.g. "2x Beer 1x Wine").
--     Each row now represents exactly one item type and quantity.
-- ------------------------------------------------------------
CREATE TABLE BarOrderItem (
    order_item_id VARCHAR(10)  PRIMARY KEY,
    bar_order_id  VARCHAR(10)  NOT NULL,
    item_name     VARCHAR(50)  NOT NULL,
    quantity      INT          NOT NULL,
    FOREIGN KEY (bar_order_id) REFERENCES BarOrder(bar_order_id)
);
