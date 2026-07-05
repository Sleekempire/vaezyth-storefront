from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import json
import httpx
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from . import models, schemas, database
from .database import engine, get_db, SessionLocal

app = FastAPI(title="Vaezyth Premium Brand & Sync Engine")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    # Force rebuild database to avoid schema mismatch with new dropshipping fields
    print("Rebuilding Vaezyth Brand database tables...", flush=True)
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Seed brand settings profile
    if not db.query(models.Profile).first():
        brand_profile = models.Profile(
            store_name="Create COMFORT",
            associate_id="",
            bio="Premium Pet Products designed for maximum comfort, utility, and style.",
            email="support@createcomfort.com",
            shopify_shop_name="",
            shopify_access_token=""
        )
        db.add(brand_profile)
    
    # 2. Seed initial Vaezyth Premium Products (using user's actual product images)
    if db.query(models.ProductDeal).count() == 0:
        print("Seeding Vaezyth premium launch products...", flush=True)
        products_data = [
            {
                "title": "Double-Layer Honeycomb Cat Litter Mat",
                "price": "14.99",
                "original_price": "24.99",
                "rating": "4.8",
                "image_url": "/mat_cat_nobg.jpg",
                "image_urls": "/mat_cat_nobg.jpg,/mat_lifestyle_bg.jpg,/mat_pocket_open.jpg,/mat_1.jpg,/mat_2.jpg,/mat_3.jpg,/mat_4.jpg",
                "affiliate_link": "",
                "description": "Stop litter tracking throughout your home with the Vaezyth Double-Layer Honeycomb Litter Mat. The innovative honeycomb-shaped pockets trap loose litter directly from your cat's paws, locking it inside. Featuring a waterproof, slip-resistant base that prevents liquid accidents from seeping through to your floors. Simply open the edge pocket to pour trapped litter back into the box!",
                "features": "Dual-Layer Honeycomb Design: traps up to 95% of loose litter;100% Waterproof Base: prevents urine or water seepage;Soft Comfort Material: gentle on sensitive paws;Easy Clean & Empty: open edge allows quick pouring or rinsing",
                "specifications": json.dumps({
                    "Material": "Eco-Friendly EVA Foam (BPA & Phthalate Free)",
                    "Dimensions": "60cm x 40cm (23.6in x 15.7in)",
                    "Thickness": "1.5cm",
                    "Color": "Slate Black"
                }),
                "how_it_works": "Place directly in front of the exit of your litter box. Stray litter falls into the mesh, locking inside. Pour back into the box by opening the pocket edge.",
                "category": "Cat Litter Mats",
                "seo_title": "Double-Layer Honeycomb Cat Litter Trapping Mat | Vaezyth",
                "seo_description": "Stop tracking litter around your home. Vaezyth's double-layer honeycomb mat traps stray litter from paws. Waterproof, easy-empty, and soft on paws."
            },
            {
                "title": "Premium Retractable Dog Leash",
                "price": "24.99",
                "original_price": "39.99",
                "rating": "4.8",
                "image_url": "/leash_side_view.jpg",
                "image_urls": "/leash_side_view.jpg,/leash_1.jpg,/leash_dimensions.jpg,/poop_bags.jpg,/leash_2.jpg,/leash_3.jpg,/leash_features.jpg",
                "affiliate_link": "",
                "description": "Enjoy stress-free night walks with the ultimate Vaezyth Premium Retractable Dog Leash. Featuring an integrated high-intensity LED flashlight, built-in poop bag dispenser, a 360° tangle-free swivel mechanism, and a secure quick-lock brake button. Crafted with an ergonomic soft-grip handle for maximum comfort during long walks.",
                "features": "Integrated LED Flashlight: illuminates night walks safely;Built-in Poop Bag Dispenser: convenience when you need it;360° Tangle-Free Design: prevents cord entanglement;Comfortable Soft Grip: ergonomic handle reduces wrist fatigue",
                "specifications": json.dumps({
                    "Tape Length": "5.0m (16 feet)",
                    "Max Weight Limit": "50kg (110 lbs)",
                    "Materials": "ABS Case, Nylon Ribbon, Stainless Steel Snap-Hook",
                    "Special Features": "Built-in LED, Integrated Dispenser, 360 Swivel"
                }),
                "how_it_works": "Hold handle. Release brake to let leash feed. Push lock forward to fix length. Push back to unlock.",
                "category": "Dog Leashes",
                "seo_title": "Premium Retractable Dog Leash with Flashlight & Dispenser | Vaezyth",
                "seo_description": "Enjoy stress-free night walks with Vaezyth's heavy-duty retractable leash. Built-in LED flashlight, integrated poop bag dispenser, and 360° tangle-free swivel."
            },
            {
                "title": "2-in-1 Portable Dog Water Bottle & Food Container",
                "price": "21.99",
                "original_price": "34.99",
                "rating": "4.9",
                "image_url": "/bottle_1.jpg",
                "image_urls": "/bottle_1.jpg,/bottle_lifestyle.jpg,/bottle_features.jpg,/bottle_use.jpg",
                "affiliate_link": "",
                "description": "Keep your companion hydrated and fed on hikes, walks, or road trips with the Vaezyth 2-in-1 Portable Dog Water Bottle. Combining a 300ml water cup, a built-in 120g food compartment, and a wide snout Feeder Cup. Features a secure slide lock and one-button flow control to retract unused water and prevent waste.",
                "features": "Dual-Function Hydration & Feeding: holds 300ml water & 120g kibble;One-Button Flow & Lock: effortless single-hand operation;100% Leak-Proof Seal: double lock prevents bag spills;Food-Grade Safe Materials: premium BPA-free construction",
                "specifications": json.dumps({
                    "Capacity": "300ml Water + 120g Food Container",
                    "Material": "Food-Grade Polycarbonate & ABS (BPA Free)",
                    "Dimensions": "26cm x 7.5cm",
                    "Special Features": "One-Button Retraction, Slide Leak Lock, Food Pocket"
                }),
                "how_it_works": "Slide lock key to unlock. Press and hold button to release water into the feeder drawer. Hold button and tilt back to return unused water into bottle.",
                "category": "Dog Travel Essentials",
                "seo_title": "Leak-Proof Portable Dog Water Bottle & Bowl | Vaezyth",
                "seo_description": "Keep your dog hydrated on walks and road trips. Vaezyth's leak-proof pet water bottle features a wide feeder cup and one-button lock. Fast UK shipping."
            }
        ]
        for p in products_data:
            deal = models.ProductDeal(**p)
            db.add(deal)
        db.commit()
    db.close()

# API Endpoints

@app.get("/api/profile", response_model=schemas.Profile)
def get_profile(db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Store profile not found")
    return profile

@app.put("/api/profile", response_model=schemas.Profile)
def update_profile(profile_data: schemas.ProfileCreate, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile:
        profile = models.Profile(**profile_data.dict())
        db.add(profile)
    else:
        for key, value in profile_data.dict().items():
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile

@app.get("/api/deals", response_model=List[schemas.ProductDeal])
def get_deals(db: Session = Depends(get_db)):
    return db.query(models.ProductDeal).filter(models.ProductDeal.is_active == 1).order_by(models.ProductDeal.id.asc()).all()

@app.put("/api/deals/{id}", response_model=schemas.ProductDeal)
def update_deal(id: int, deal_data: schemas.ProductDealBase, db: Session = Depends(get_db)):
    deal = db.query(models.ProductDeal).filter(models.ProductDeal.id == id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in deal_data.dict().items():
        if value is not None:
            setattr(deal, key, value)
    db.commit()
    db.refresh(deal)
    return deal

@app.post("/api/opt-in")
def opt_in(req: schemas.OptInRequest, db: Session = Depends(get_db)):
    existing = db.query(models.Subscriber).filter(models.Subscriber.email == req.email.lower().strip()).first()
    if existing:
        if existing.status == "Unsubscribed":
            existing.status = "Subscribed"
            db.commit()
            return {"status": "success", "message": "Resubscribed successfully!"}
        return {"status": "success", "message": "Already subscribed."}
        
    subscriber = models.Subscriber(
        email=req.email.lower().strip(),
        name=req.name.strip() if req.name else None,
        status="Subscribed",
        opt_in_ip="127.0.0.1"
    )
    db.add(subscriber)
    db.commit()
    return {"status": "success", "message": "Opt-in registered successfully!"}

@app.get("/api/unsubscribe", response_class=HTMLResponse)
def unsubscribe(email: str, db: Session = Depends(get_db)):
    subscriber = db.query(models.Subscriber).filter(models.Subscriber.email == email.lower().strip()).first()
    if subscriber:
        subscriber.status = "Unsubscribed"
        db.commit()
        
    html_content = """
    <html>
        <head>
            <title>Unsubscribed</title>
            <style>
                body { font-family: 'Inter', sans-serif; text-align: center; padding: 50px; background-color: #f8fafc; color: #0f172a; }
                .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(15,23,42,0.05); display: inline-block; }
                h1 { color: #22c55e; margin-bottom: 10px; }
                p { color: #64748b; font-size: 15px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Unsubscribed</h1>
                <p>You have been successfully unsubscribed from Vaezyth's newsletter.</p>
                <p>No further marketing emails will be sent to you.</p>
            </div>
        </body>
    </html>
    """
    return html_content

@app.get("/api/subscribers", response_model=List[schemas.Subscriber])
def list_subscribers(db: Session = Depends(get_db)):
    return db.query(models.Subscriber).order_by(models.Subscriber.id.desc()).all()

@app.post("/api/shopify/sync")
async def sync_to_shopify(req: schemas.ShopifySyncRequest, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile or not profile.shopify_shop_name or not profile.shopify_access_token:
        raise HTTPException(
            status_code=400, 
            detail="Shopify shop name and admin access token must be configured in settings first."
        )
    
    product = db.query(models.ProductDeal).filter(models.ProductDeal.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in database")
        
    # Standardize features format
    features_list = [f.strip() for f in (product.features or "").split(";") if f.strip()]
    features_html = "".join([f"<li>{f}</li>" for f in features_list])
    
    specs_dict = {}
    try:
        if product.specifications:
            specs_dict = json.loads(product.specifications)
    except Exception:
        pass
    
    specs_html = "".join([f"<tr><td style='font-weight:600;padding:4px 8px;border-bottom:1px solid #f1f5f9;'>{k}</td><td style='padding:4px 8px;border-bottom:1px solid #f1f5f9;'>{v}</td></tr>" for k, v in specs_dict.items()])
    
    body_html = f"""
    <p>{product.description}</p>
    <h4>🌟 Key Benefits</h4>
    <ul>{features_html}</ul>
    <h4>⚙️ Specifications</h4>
    <table style='width:100%;border-collapse:collapse;margin-top:10px;'>{specs_html}</table>
    <h4>🚀 How It Works</h4>
    <p>{product.how_it_works}</p>
    """
    
    images_list = [img.strip() for img in (product.image_urls or "").split(",") if img.strip()]
    if not images_list and product.image_url:
        images_list = [product.image_url]
        
    shopify_payload = {
        "product": {
            "title": product.title,
            "body_html": body_html,
            "vendor": profile.store_name,
            "product_type": product.category,
            "status": "active",
            "published_scope": "global",
            "variants": [
                {
                    "price": product.price,
                    "compare_at_price": product.original_price,
                    "requires_shipping": True,
                    "inventory_management": "shopify",
                    "inventory_policy": "continue"
                }
            ],
            "images": [{"src": img} for img in images_list]
        }
    }
    
    headers = {
        "X-Shopify-Access-Token": profile.shopify_access_token,
        "Content-Type": "application/json"
    }
    
    shop_url = f"https://{profile.shopify_shop_name}.myshopify.com/admin/api/2023-07/products.json"
    
    async with httpx.AsyncClient() as client:
        try:
            # If already has a shopify product ID, try to update it instead of creating
            if product.shopify_product_id:
                update_url = f"https://{profile.shopify_shop_name}.myshopify.com/admin/api/2023-07/products/{product.shopify_product_id}.json"
                resp = await client.put(update_url, json=shopify_payload, headers=headers, timeout=25.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return {"status": "success", "message": "Updated product on Shopify!", "shopify_id": product.shopify_product_id}
            
            # Create fresh product
            resp = await client.post(shop_url, json=shopify_payload, headers=headers, timeout=25.0)
            if resp.status_code == 201:
                data = resp.json()
                shopify_id = str(data["product"]["id"])
                product.shopify_product_id = shopify_id
                db.commit()
                return {"status": "success", "message": "Successfully synced to Shopify!", "shopify_id": shopify_id}
            else:
                raise HTTPException(
                    status_code=resp.status_code, 
                    detail=f"Shopify API Error: {resp.text}"
                )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request to Shopify failed: {str(e)}")

@app.get("/api/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_subscribers = db.query(models.Subscriber).filter(models.Subscriber.status == "Subscribed").count()
    total_deals = db.query(models.ProductDeal).filter(models.ProductDeal.is_active == 1).count()
    synced_deals = db.query(models.ProductDeal).filter(models.ProductDeal.shopify_product_id != None).count()
    
    return {
        "totalSubscribers": total_subscribers,
        "totalDeals": total_deals,
        "syncedDeals": synced_deals
    }

# Serve static storefront files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
