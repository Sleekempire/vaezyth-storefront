import csv
import re
import sys
import urllib.request
import json
import time

# Define standard mapping lists
product_types = [
    ("cat litter mat", "Cat Litter Mat"),
    ("litter mat", "Cat Litter Mat"),
    ("nail grinder", "Pet Nail Grinder"),
    ("dog leash", "Dog Leash"),
    ("chew toy", "Pet Chew Toy"),
    ("finger cleaner", "Pet Finger Cleaner"),
    ("dog collar", "Dog Collar"),
    ("sofa protector", "Sofa Protector"),
    ("licking feeding mat", "Pet Licking Mat"),
    ("licking mat", "Pet Licking Mat"),
    ("carrier bag", "Pet Carrier Bag"),
    ("cat hammock", "Cat Hammock"),
    ("slow feeder", "Slow Feeder Bowl"),
    ("dog bowl", "Dog Bowl"),
    ("harness and leash", "Dog Harness & Leash"),
    ("water fountain", "Pet Water Fountain"),
]

colors = [
    "Elegant Gray", "Gray", "Light green", "green", "Black", "Pink", "Blue", 
    "Khaki", "Sunlight yellow", "Sunlight Yellow", "Yellow", "Brown", "Grey", 
    "Light Gray", "Coffee", "Red", "USB grey transparent", "White"
]

sizes = [
    r"\b\d+x\d+cm\b",
    r"\b\d+x\d+x\d+cm\b",
    r"\b\d{4}cm\b", # e.g. 3030cm, 3045cm
    r"\b[LSM]\d{4}\b", # e.g. L2045, S1540, M1447
    r"\bSmall\b", r"\bMedium\b", r"\bLarge\b",
    r"\b[SML]\b"
]

def clean_words(text, remove_list):
    """Clean specific category/noise words from text to avoid duplication."""
    for word in remove_list:
        text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)
    # Clean special chars
    text = re.sub(r'^[|/\-,\s\+]+', '', text)
    text = re.sub(r'[|/\-,\s\+]+$', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_row(orig_title):
    title = orig_title
    
    # 1. Extract Color
    matched_color = ""
    parts = [p.strip() for p in title.split("/")]
    if len(parts) > 1:
        last_part = parts[-1]
        for c in colors:
            if c.lower() in last_part.lower():
                matched_color = c
                title = title.replace("/ " + last_part, "").replace("/" + last_part, "").strip()
                break
                
    if not matched_color:
        for c in colors:
            if re.search(r'\b' + re.escape(c) + r'\b', title, re.IGNORECASE):
                matched_color = c
                title = re.sub(r'\b' + re.escape(c) + r'\b', '', title, flags=re.IGNORECASE).strip()
                break
                
    # 2. Extract Size
    matched_size = ""
    for sz_pat in sizes:
        match = re.search(sz_pat, title, re.IGNORECASE)
        if match:
            matched_size = match.group(0)
            title = title.replace(matched_size, "").strip()
            # Standardize 4-digit sizes (e.g. 3030cm -> 30x30cm)
            if re.match(r"^\d{4}cm$", matched_size):
                matched_size = f"{matched_size[:2]}x{matched_size[2:]}"
            break
            
    # 3. Extract Product Type
    matched_type = "Pet Accessory"
    type_removes = []
    for type_key, type_name in product_types:
        if type_key in title.lower():
            matched_type = type_name
            type_removes = type_key.split()
            title = clean_words(title, type_removes)
            break
            
    # 4. Extract Key Feature / Material
    # Remove common category noise words
    noise = ["default", "with", "for", "and", "set", "pet", "toy", "toys", "electric", "reusable", "self", "cleaning", "tool", "effortless", "anti-pull", "anti-splash", "anti-track", "pad"]
    feature = clean_words(title, type_removes + noise)
    
    # Clean up punctuation
    feature = re.sub(r'^[|/\-,\s\+]+', '', feature)
    feature = re.sub(r'[|/\-,\s\+]+$', '', feature)
    feature = re.sub(r'\s+', ' ', feature).strip()
    
    # Capitalize nicely
    feature = " ".join([w.capitalize() for w in feature.split()])
    if not feature:
        feature = "Premium"
        
    return {
        "product_type": matched_type,
        "feature": feature,
        "size": matched_size,
        "color": matched_color
    }

def main():
    print("====================================================")
    print("        Shopify Product Renamer Automator           ")
    print("====================================================")
    
    shop_name = input("Enter your Shopify shop name (e.g. vaezyth-storefront): ").strip()
    access_token = input("Enter your Shopify Admin Access Token (shpat_...): ").strip()
    
    if not shop_name or not access_token:
        print("Error: Shop name and Access Token are required.")
        sys.exit(1)
        
    # Clean shop name if user entered full URL
    if ".myshopify.com" in shop_name:
        shop_name = shop_name.split(".myshopify.com")[0].replace("https://", "").replace("http://", "")
        
    # 1. Parse CSV and group variants by Product ID
    products_map = {}
    try:
        with open("assets/Product_report_clean.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                item_id = row["Item ID"]
                title = row["Title"]
                
                # Parse shopify product id
                match = re.search(r"shopify_zz_(\d+)_(\d+)", item_id)
                if not match:
                    continue
                product_id = match.group(1)
                
                parsed = parse_row(title)
                
                if product_id not in products_map:
                    products_map[product_id] = {
                        "orig_titles": [],
                        "types": set(),
                        "features": set(),
                        "sizes": set(),
                        "colors": set()
                    }
                
                products_map[product_id]["orig_titles"].append(title)
                products_map[product_id]["types"].add(parsed["product_type"])
                products_map[product_id]["features"].add(parsed["feature"])
                if parsed["size"]:
                    products_map[product_id]["sizes"].add(parsed["size"])
                if parsed["color"]:
                    products_map[product_id]["colors"].add(parsed["color"])
    except FileNotFoundError:
        print("Error: assets/Product_report_clean.csv not found. Did you run the conversion first?")
        sys.exit(1)
        
    print(f"\nLoaded {len(products_map)} unique products from CSV file.")
    print("Beginning Shopify sync and renames...\n")
    
    success_count = 0
    fail_count = 0
    
    for product_id, data in products_map.items():
        # Get consensus type and feature
        prod_type = list(data["types"])[0] if data["types"] else "Pet Accessory"
        # Take the shortest/cleanest feature name
        feature = sorted(list(data["features"]), key=len)[0] if data["features"] else "Premium"
        
        # Determine size/color inclusion:
        # If the product only has 1 size and 1 color globally, we append it to the title.
        # If it has multiple variants, we omit size/color from the base product title so variants handle it.
        size_part = list(data["sizes"])[0] if len(data["sizes"]) == 1 else ""
        color_part = list(data["colors"])[0] if len(data["colors"]) == 1 else ""
        
        # Assemble title: ProductType + Feature + Size + Color
        title_parts = [prod_type, feature]
        if size_part:
            title_parts.append(size_part)
        if color_part:
            title_parts.append(color_part)
            
        new_title = " ".join(title_parts)
        new_title = re.sub(r'\s+', ' ', new_title).strip()
        
        orig_display = data["orig_titles"][0][:50] + "..."
        print(f"Product ID: {product_id}")
        print(f"  Old: {orig_display}")
        print(f"  New: {new_title}")
        
        # Make Shopify API request to update title
        url = f"https://{shop_name}.myshopify.com/admin/api/2023-07/products/{product_id}.json"
        payload = {
            "product": {
                "id": int(product_id),
                "title": new_title
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "X-Shopify-Access-Token": access_token,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            method="PUT"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("  Status: ✅ SUCCESS")
                    success_count += 1
                else:
                    print(f"  Status: ❌ FAILED (HTTP {response.status})")
                    fail_count += 1
        except Exception as e:
            print(f"  Status: ❌ FAILED ({str(e)})")
            fail_count += 1
            
        # Shopify rate limit safety delay (max 2 requests per second)
        time.sleep(0.5)
        
    print("\n====================================================")
    print(f"Sync completed! Success: {success_count} | Failed: {fail_count}")
    print("====================================================")

if __name__ == "__main__":
    main()
