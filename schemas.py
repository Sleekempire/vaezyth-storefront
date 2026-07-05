from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProfileBase(BaseModel):
    store_name: str
    associate_id: str
    bio: str
    email: str
    shopify_shop_name: Optional[str] = ""
    shopify_access_token: Optional[str] = ""

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    class Config:
        from_attributes = True

class SubscriberBase(BaseModel):
    email: str
    name: Optional[str] = None
    status: Optional[str] = "Subscribed"

class SubscriberCreate(SubscriberBase):
    opt_in_ip: Optional[str] = None

class Subscriber(SubscriberBase):
    id: int
    opt_in_at: datetime
    class Config:
        from_attributes = True

class ProductDealBase(BaseModel):
    asin: Optional[str] = None
    title: str
    price: str
    original_price: Optional[str] = None
    rating: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[str] = None
    affiliate_link: Optional[str] = None
    description: Optional[str] = None
    features: Optional[str] = None
    specifications: Optional[str] = None
    how_it_works: Optional[str] = None
    category: Optional[str] = "General"
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    shopify_product_id: Optional[str] = None
    is_active: Optional[int] = 1

class ProductDeal(ProductDealBase):
    id: int
    last_updated: datetime
    class Config:
        from_attributes = True

class EmailLogBase(BaseModel):
    subscriber_id: int
    subject: str
    body: str

class EmailLog(EmailLogBase):
    id: int
    sent_at: datetime
    class Config:
        from_attributes = True

class OptInRequest(BaseModel):
    email: str
    name: Optional[str] = None

class ShopifySyncRequest(BaseModel):
    product_id: int

class ShopifySettingsRequest(BaseModel):
    shopify_shop_name: str
    shopify_access_token: str
