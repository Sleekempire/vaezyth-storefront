from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String, default="Vaezyth")
    associate_id = Column(String, default="")
    bio = Column(Text, default="Premium Pet Products designed for maximum comfort, utility, and style.")
    email = Column(String, default="support@vaezyth.com")
    shopify_shop_name = Column(String, default="")  # e.g., 'vaezyth-store'
    shopify_access_token = Column(String, default="") # Admin API Access Token

class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    status = Column(String, default="Subscribed") # Subscribed, Unsubscribed
    opt_in_ip = Column(String, nullable=True)
    opt_in_at = Column(DateTime(timezone=True), server_default=func.now())

class ProductDeal(Base):
    __tablename__ = "product_deals"
    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String, unique=True, index=True, nullable=True)
    title = Column(String)
    price = Column(String) # Current selling price (e.g. "19.99")
    original_price = Column(String, nullable=True) # Compare at price (e.g. "29.99")
    rating = Column(String, nullable=True, default="4.8")
    image_url = Column(String, nullable=True) # Main image URL
    image_urls = Column(Text, nullable=True) # Comma-separated list of image URLs
    affiliate_link = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    features = Column(Text, nullable=True) # Semicolon-separated benefit bullets
    specifications = Column(Text, nullable=True) # JSON or key-value text
    how_it_works = Column(Text, nullable=True)
    category = Column(String, default="General") # Dogs, Cats, Pet Hair Removal, etc.
    seo_title = Column(String, nullable=True)
    seo_description = Column(Text, nullable=True)
    shopify_product_id = Column(String, nullable=True) # Store returned shopify ID if synced
    is_active = Column(Integer, default=1)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))
    sender_email = Column(String, nullable=True)
    subject = Column(String)
    body = Column(Text)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
