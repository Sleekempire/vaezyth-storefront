import random
import re
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# Improved Regex for emails - more restrictive on domain parts
EMAIL_REGEX = r'[a-zA-Z0-9.\-_]{2,}@[a-zA-Z0-9.\-_]{2,}\.[a-zA-Z]{2,6}'
IGNORE_EMAILS = {
    'noreply', 'no-reply', 'support', 'sales', 'admin', 'postmaster', 'hostmaster', 'webmaster', 
    'help', 'billing', 'office', 'hello', 'hi', 
    'pals', 'complaints', 'foi', 'sar', 'finance', 'legal', 'accounts', 'events', 
    'press', 'media', 'communications', 'reception', 'booking', 
    'clinical', 'ward', 'nursing', 'doctor', 'surgery', 'medicine', 'patient',
    'feedback', 'alert', 'notification', 'donotreply', 'spam', 'test',
    'appointment', 'referral', 'bookingenquiries', 'colposcopy', 'paeds', 'diab', 
    'epu', 'rfs', 'oncology', 'cardiology', 'theatre', 'radiology', 'pharm', 'imaging',
    'u00', 'x20', 'x3c', 'x3e', 'hours', 'job.', 'recruit.', 'dataprotection',
    'employers', 'jobseekers', 'enquries', 'firstname.lastname', 'yourname',
    'email'
}
JUNK_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.pdf', '.css', '.js', '.webp', '.ico', '.woff', '.2x', '.zip', '.exe', '.aspx'}
EXCLUDE_DOMAINS = {
    'example.com', 'test.com', 'placeholder.com', 'dummy.com', 'wixpress.com', 'squarespace.com', 
    'wordpress.org', 'domain.com', 'email.com', 'searx.be', 'searx.work', 'searx.info', 
    'searxng.org', 'imirhil.fr', 'gnous.eu', 'mdelnet.xyz', 'nixnet.services', 'ononoki.org', 
    'tiekoetter.com', 'prvcy.eu', 'bus-hit.me', 'rasp.fr', 'fmac.xyz', 'disroot.org', 
    'sethforprivacy.com', 'suneret.net', 'github.com', 'bsky.app', 'archive.org', 'mozilla.org',
    'w3.org', 'cryptcheck.fr'
}

# Strong Recruiter/Academic Keywords
POSITIVE_KEYWORDS = {
    'recruitment', 'career', 'jobs', 'hr', 'human.resources', 'human-resources', 'talent', 'hiring', 'people', 'staffing', 'work@', 'join@', 'resourcing',
    'professor', 'admission', 'doctoral', 'phd', 'research', 'lab', 'supervisor', 'studentship', 'academic', 'faculty', 'scholarship'
}

def is_valid_recruiter_email(email):
    email_lower = email.lower()
    
    # 1. Basics
    if '@' not in email_lower or '.' not in email_lower: return False
    if len(email_lower) < 7 or len(email_lower) > 90: return False
    
    # 2. Block lists
    try:
        prefix, domain = email_lower.split('@')
        for ignore in IGNORE_EMAILS:
            # Check if ignore keyword is in the prefix (local-part)
            if ignore in prefix: 
                # OVERRIDE: If it contains a positive keyword, we allow it (e.g. recruitment.admin@)
                if any(good in prefix for good in POSITIVE_KEYWORDS):
                    continue
                return False
            # Check if it's the start of the domain (e.g. info@...)
            if domain.startswith(ignore): return False
    except:
        return False
        
    for domain_exc in EXCLUDE_DOMAINS:
        if domain_exc in domain: return False
        
    if any(ext in email_lower for ext in JUNK_EXTENSIONS): return False
    
    # 3. Structural checks
    try:
        prefix, domain = email_lower.split('@')
        # Filter out emails with excessive numbers or repeating symbols (common scraper noise)
        if len(re.findall(r'\d', prefix)) > 4: return False
        if re.search(r'[-.]{3,}', prefix): return False # Catch things like ---@ or ....@
        if 'firstname' in prefix or 'lastname' in prefix: return False
        if 'x22' in prefix: return False # Catch hex encoded scraped quotes
        
        # Catch bot-obfuscated emails replacing vowels with x (e.g., xdxtor@cxsxxno.com)
        # Wave 1 patterns
        if prefix.count('x') > 4 or domain.count('x') > 4: return False
        if re.search(r'x[a-z]{0,1}x[a-z]{0,1}x', email_lower): return False
        
        # Wave 2 patterns - Specific obfuscated tokens
        scramble_tokens = [
            'nxws', 'xdxtor', 'stxr', 'lxnk', 'journxl', 'mxtro', 'cxllxr', 
            'postx', 'thx', 'bxz', 'bxr', 'clxnk', 'mxrk', 'wstx', 'jxnnxfxr', 
            'gxzx', 'progrxmm', 'dxxly', 'prxss', 'rxcord'
        ]
        if any(token in email_lower for token in scramble_tokens):
            return False

        # Additional broad pattern for scrambled sequences (e.g. x.x.x, x-x-x)
        if re.search(r'x[\._\-]x[\._\-]x', prefix): return False
        
        # High density of X with low vowel count (Suspicious)
        if 'x' in prefix:
            vowels = len(re.findall(r'[aeiou]', prefix))
            if vowels == 0 and len(prefix) > 3: return False
            if prefix.count('x') / len(prefix) > 0.35 if len(prefix) > 5 else False: return False
        
        # Filter out clinical/departmental noise if it doesn't have a positive keyword
        if any(bad in prefix for bad in ['ward', 'surgery', 'pharm', 'imaging', 'clin', 'lab']):
            if not any(good in email_lower for good in POSITIVE_KEYWORDS):
                return False
                
        # Avoid non-standard TLDs if not .uk or .com (mostly for cold reach UK)
        tld = domain.split('.')[-1]
        if tld not in ['uk', 'com', 'org', 'net', 'be']:
            if not any(good in email_lower for good in POSITIVE_KEYWORDS):
                return False
                
        # Must have a legitimate looking domain (at least one dot, TLD length 2-6)
        if '.' not in domain or len(tld) < 2: return False
        
        # Avoid generic prefixes if they aren't explicit recruiter names or keywords
        # Short prefixes like "a@b.com" are often false positives
        if len(prefix) < 3 and not any(k in prefix for k in ['hr', 'cv']):
            return False
            
    except:
        return False

    # 4. Character sanity
    if any(char in email_lower for char in ['/', '\\', '*', '?', '"', '<', '>', '|', '(', ')', '[', ']', '{', '}', ',', ';']):
        return False
        
    # Pattern check: No triple dots or dots at the start/end of prefix
    if '..' in email_lower or email_lower.startswith('.') or '@.' in email_lower:
        return False
        
    return True

def extract_emails_from_text(text):
    emails = re.findall(EMAIL_REGEX, text)
    valid_emails = []
    for email in emails:
        if is_valid_recruiter_email(email):
            valid_emails.append(email)
        else:
            pass # Verbose debugging can go here
    return list(set(valid_emails))

def scrape_url_for_emails(url):
    """
    Fetches a URL and extracts all valid emails.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()
            emails = extract_emails_from_text(text_content)
            
            for a in soup.find_all('a', href=True):
                if a['href'].startswith('mailto:'):
                    email = a['href'].replace('mailto:', '').split('?')[0].strip()
                    if is_valid_recruiter_email(email):
                        emails.append(email)
            return list(set(emails))
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
    return []

def search_engine_aggregator(query, num_results):
    """
    Attempts to gather as many unique discovery URLs as possible from multiple search engines.
    """
    discovery_urls = set()
    def get_random_ua():
        return random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 OPR/103.0.0.0'
        ])

    searx_instances = [
        "https://searx.be", "https://searx.work", "https://searx.gnous.eu",
        "https://searx.info", "https://searxng.org", "https://baresearch.org",
        "https://search.mdelnet.xyz", "https://searx.nixnet.services",
        "https://search.ononoki.org", "https://searx.tiekoetter.com",
        "https://searx.prvcy.eu", "https://search.bus-hit.me",
        "https://searx.rasp.fr", "https://searx.fmac.xyz", "https://search.disroot.org",
        "https://searx.sethforprivacy.com", "https://searx.suneret.net"
    ]
    
    def fetch_searx(instance):
        try:
            # Try JSON first
            url = f"{instance}/search?q={urllib.parse.quote(query)}&format=json"
            resp = requests.get(url, headers={'User-Agent': get_random_ua()}, timeout=15)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    return [res['url'] for res in data.get('results', [])]
                except: pass
            
            # Fallback to HTML
            url_html = f"{instance}/search?q={urllib.parse.quote(query)}"
            resp = requests.get(url_html, headers={'User-Agent': get_random_ua()}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                urls = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http') and instance not in href:
                        urls.append(href)
                return urls
        except: pass
        return []

    # Block list for job aggregators and SEO spam
    BLOCK_SITES = {
        'jobted', 'adzuna', 'indeed', 'linkedin.com/jobs', 'glassdoor', 'totaljobs', 'jobsite',
        'monster', 'ziprecruiter', 'themuse', 'simplyhired', 'jooble', 'careerbuilder', 'facebook.com',
        'youtube.com', 'twitter.com', 'instagram.com', 'pinterest.com', 'wikipedia.org',
        'otta.com', 'workabroad', 'brighthorizons', 'care.com', 'gumtree', 'jobsearch', 'myjobmag',
        'charityjob', 'reed.co.uk/jobs', 'jobs.theguardian', 'cwjobs', 'technojobs', 'jobserve'
    }

    def fetch_mojeek(q):
        try:
            url = f"https://www.mojeek.com/search?q={urllib.parse.quote(q)}"
            resp = requests.get(url, headers={'User-Agent': get_random_ua()}, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                return [a['href'] for a in soup.find_all('a', class_='ob', href=True)]
        except: pass
        return []

    def fetch_ddg_lite(q):
        try:
            url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(q)}"
            resp = requests.get(url, headers={'User-Agent': get_random_ua()}, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                return [a['href'] for a in soup.find_all('a', class_='result__url', href=True)]
        except: pass
        return []

    def fetch_bing(q):
        try:
            url = f"https://www.bing.com/search?q={urllib.parse.quote(q)}&count=50"
            resp = requests.get(url, headers={'User-Agent': get_random_ua()}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                urls = []
                for li in soup.find_all('li', class_='b_algo'):
                    a = li.find('a', href=True)
                    if a and a['href'].startswith('http') and not any(x in a['href'] for x in ['bing.com', 'microsoft.com', 'msn.com']):
                        urls.append(a['href'])
                return list(set(urls))
        except: pass
        return []

    def fetch_google_lite(q):
        try:
            # Use the mobile/low-JS search endpoint
            url = f"https://www.google.com/search?q={urllib.parse.quote(q)}&gbv=1&hl=en"
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'}, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                urls = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if "/url?q=" in href:
                        clean_url = href.split("/url?q=")[1].split("&")[0]
                        if clean_url.startswith("http"): urls.append(clean_url)
                return urls
        except: pass
        return []

    with ThreadPoolExecutor(max_workers=14) as executor:
        # Searx (Larger sample for faster discovery)
        searx_results = list(executor.map(fetch_searx, random.sample(searx_instances, min(14, len(searx_instances)))))
        for batch in searx_results:
            discovery_urls.update(batch)
        
        future_mojeek = executor.submit(fetch_mojeek, query)
        future_ddg = executor.submit(fetch_ddg_lite, query)
        future_bing = executor.submit(fetch_bing, query)
        future_google = executor.submit(fetch_google_lite, query)
        
        discovery_urls.update(future_mojeek.result() or [])
        discovery_urls.update(future_ddg.result() or [])
        discovery_urls.update(future_bing.result() or [])
        discovery_urls.update(future_google.result() or [])

    # AGENCY DIRECTORY SEEDFALLBACK: When results are low, add major recruitment agency base sites
    if len(discovery_urls) < 10:
        seed_agencies = [
            'https://www.hays.co.uk', 'https://www.michaelpage.co.uk', 'https://www.robertwalters.com',
            'https://www.adecco.co.uk', 'https://www.randstad.co.uk', 'https://www.morganmckinley.com',
            'https://www.roberthalf.co.uk', 'https://www.reed.co.uk', 'https://www.monroeconsulting.com',
            'https://www.betterplaced.com', 'https://www.bpesearch.com', 'https://www.harveynash.com',
            'https://www.venquis.com', 'https://www.handle.co.uk', 'https://www.thinkpublishing.co.uk'
        ]
        discovery_urls.update(seed_agencies)

    # Filter out job aggregators to prioritize direct company sites
    discovery_urls = {u for u in discovery_urls if not any(site in u.lower() for site in BLOCK_SITES)}

    # Yahoo (Broad selection)
    try:
        headers = {'User-Agent': get_random_ua()}
        url = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}&n=50"
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "RU=" in href:
                    try:
                        clean_url = urllib.parse.unquote(href.split("RU=")[1].split("/RK=")[0])
                        if clean_url.startswith("http"): discovery_urls.add(clean_url)
                    except: pass
                elif "http" in href and not any(x in href for x in ["yahoo.com", "bing.com", "google.com"]):
                    discovery_urls.add(href)
    except: pass

    discovery_urls = {u for u in discovery_urls if not any(d in u.lower() for d in ["google.com", "microsoft.com", "apple.com", "yahoo.com"])}
    
    # TURBO: If we have very few URLs, try a broader Bing search
    if len(discovery_urls) < 10:
        discovery_urls.update(fetch_bing(query + " recruiter"))
        
    return list(discovery_urls)[:num_results * 10] # Return more candidates for deep crawl

def recursive_email_discovery(url):
    if any(d in url.lower() for d in EXCLUDE_DOMAINS):
        return []

    discovery_set = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        time.sleep(random.uniform(0.1, 0.5))
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            discovery_set.update(extract_emails_from_text(resp.text))
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            sub_pages = []
            for a in soup.find_all('a', href=True):
                text = a.get_text().lower()
                href = a['href']
                if any(ext in href.lower() for ext in [".png", ".jpg", ".jpeg", ".pdf"]): continue
                if any(k in text or k in href.lower() for k in ["contact", "about", "team", "career", "people", "staff", "join", "meet", "personnel", "recruit"]):
                    if href.startswith("/"): href = urllib.parse.urljoin(url, href)
                    if href.startswith("http") and href not in sub_pages:
                        sub_pages.append(href)
            
            # Reorder: prioritize 'Meet the Team' / 'People' over 'Contact' for individual leads
            sub_pages.sort(key=lambda x: 0 if any(k in x.lower() for k in ["meet", "team", "people", "our-people"]) else 1)
            
            for a in soup.find_all('a', href=True):
                if a['href'].lower().startswith('mailto:'):
                    email = a['href'][7:].split('?')[0].strip()
                    if is_valid_recruiter_email(email):
                        discovery_set.add(email)

            # Deep crawl: up to 6 sub-pages
            for sub in sub_pages[:6]:
                try:
                    time.sleep(random.uniform(0.1, 0.2))
                    s_resp = requests.get(sub, headers=headers, timeout=10)
                    if s_resp.status_code == 200:
                        discovery_set.update(extract_emails_from_text(s_resp.text))
                        # Even find mailtos on subpages
                        s_soup = BeautifulSoup(s_resp.text, 'html.parser')
                        for sa in s_soup.find_all('a', href=True):
                            if sa['href'].lower().startswith('mailto:'):
                                se = sa['href'][7:].split('?')[0].strip()
                                if is_valid_recruiter_email(se): discovery_set.add(se)
                except: pass
    except: pass
    
    return list(discovery_set)

def autonomous_scrape_query(query, num_results=100):
    print(f"Starting LIVE web scrape for: {query}", flush=True)
    
    # Relax restrictive quoting, keep it natural
    if "@" not in query and "email" not in query.lower():
        # Keep it broad: Keyword Location recruiter email
        query = f"{query} recruiter email"
    else:
        # If user already provided email/keywords, don't force extra "contact email"
        pass
    
    discovery_urls = search_engine_aggregator(query, num_results)
    print(f"Aggregated {len(discovery_urls)} discovery URLs. Starting parallel deep crawl...", flush=True)
    
    # 1. Deduplicate early
    discovery_urls = list(set(discovery_urls))[:num_results] 
    
    results = []
    
    # Extract cleaner role
    ignore_list = ['hiring', 'contact', 'email', 'recruitment', 'UK', 'United Kingdom', 'GB', 'specialized', 'agency', 'niche', 'recruiter', 'partners', 'manager', 'talent', 'acquisition', 'specialist', 'technical', 'in', 'at']
    clean_role = query
    for word in ignore_list:
        clean_role = re.sub(rf'(?i)\b{word}\b', ' ', clean_role)
    clean_role = re.sub(rf'(?i)\b(cv|apply|your|to)\b', ' ', clean_role.replace('"', '').replace("'", ""))
    clean_role = re.sub(rf'\s+', ' ', clean_role).strip().title()
    if not clean_role or len(clean_role) < 3: clean_role = "Analytical Problem Solver"

    def process_url(url):
        try:
            emails = recursive_email_discovery(url)
            found_leads = []
            for email in emails:
                domain = email.split('@')[1]
                company = domain.split('.')[0].capitalize()
                prefix = email.split('@')[0]
                
                if len(prefix) < 2: continue
                
                clean_name = prefix.replace('.', ' ').replace('-', ' ').replace('_', ' ')
                if any(x in clean_name.lower() for x in ['info', 'admin', 'office', 'career', 'job', 'hello', 'contact', 'support', 'investor']):
                    clean_name = "Hiring Manager"
                elif len(clean_name) > 20: 
                    clean_name = "Hiring Manager"
                else:
                    clean_name = clean_name.title()
                
                domain_lower = domain.lower()
                industry = "Professional Services"
                
                if any(x in domain_lower for x in [".edu", ".ac.uk", ".edu.", "university", "college", "institute", "research", "lab"]):
                    industry = "Academic/Research"
                elif any(x in domain_lower for x in ["gmail", "outlook", "hotmail", "yandex", "icloud"]): 
                    industry = "Direct Lead"
                elif any(x in company.lower() or x in domain_lower for x in ["tech", "soft", "data", "cloud", "compute", "digital", "ai", "consult", "analyst", "intelligence", "analytics", "business", "fin", "market", "operation", "strategy"]): 
                    industry = "Technology/Consulting"
                elif any(x in company.lower() or x in domain_lower for x in ["bank", "fin", "invest", "capital", "wealth", "insur", "trading", "equity"]): 
                    industry = "Finance"
                
                found_leads.append({
                    'company_name': company,
                    'recruiter_name': clean_name,
                    'email': email,
                    'industry': industry,
                    'target_role': clean_role,
                    'source_url': url
                })
            return found_leads
        except:
            return []

    with ThreadPoolExecutor(max_workers=10) as executor:
        batch_results = list(executor.map(process_url, discovery_urls))
        for batch in batch_results:
            results.extend(batch)
    # Re-filter results to avoid excessive 'info@' if better ones are found for the same company
    company_leads = {}
    for res in results:
        comp = res['company_name']
        prefix = res['email'].split('@')[0].lower()
        if comp not in company_leads:
            company_leads[comp] = []
        company_leads[comp].append(res)
    
    unique_final = []
    for comp, leads in company_leads.items():
        # Prefer individual names (dots or length) over generic ones
        leads.sort(key=lambda x: 0 if ('.' in x['email'].split('@')[0] or len(x['email'].split('@')[0]) > 4) else 1)
        unique_final.append(leads[0]) # Take top 1 per company

    final = unique_final[:num_results]
    print(f"Manual scrape complete. Identified {len(final)} unique leads.", flush=True)
    return final

def scrape_amazon_deals(query: str, associate_id: str):
    import urllib.parse
    import json
    
    url = f"https://www.amazon.com/s?k={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }
    
    # Try up to 5 times with random User Agents to prevent blocks
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    for attempt in range(5):
        headers["User-Agent"] = random.choice(user_agents)
        try:
            print(f"[{attempt+1}/5] Scraping Amazon for '{query}'...", flush=True)
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"Non-200 status code: {resp.status_code}", flush=True)
                continue
                
            if "captcha" in resp.text.lower():
                print("CAPTCHA blocked.", flush=True)
                continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            products = soup.find_all('div', {'data-component-type': 's-search-result'})
            if not products:
                print("No product divs found on page.", flush=True)
                continue
                
            parsed_results = []
            for p in products:
                asin = p.get('data-asin', '')
                if not asin:
                    continue
                    
                # Title
                title_node = p.find('h2')
                title = title_node.text.strip() if title_node else "N/A"
                
                # Price
                price_node = p.find('span', {'class': 'a-price'})
                price = "N/A"
                if price_node:
                    offscreen = price_node.find('span', {'class': 'a-offscreen'})
                    if offscreen:
                        price = offscreen.text.strip()
                
                # Original Price
                orig_price_node = p.find('span', {'class': 'a-price a-text-price'})
                orig_price = None
                if orig_price_node:
                    offscreen = orig_price_node.find('span', {'class': 'a-offscreen'})
                    if offscreen:
                        orig_price = offscreen.text.strip()
                
                # Rating
                rating = "N/A"
                rating_node = p.find('i', class_=lambda x: x and 'a-icon-star' in x)
                if rating_node:
                    rating_span = rating_node.find('span', class_='a-icon-alt')
                    if rating_span:
                        rating = rating_span.text.strip().split(' ')[0]
                else:
                    alt_rating = p.find('span', class_='a-icon-alt')
                    if alt_rating:
                        rating = alt_rating.text.strip().split(' ')[0]
                        
                # Image URL
                img_node = p.find('img', class_='s-image')
                img_url = img_node.get('src', '') if img_node else ''
                
                # Standard affiliate link format
                affiliate_link = f"https://www.amazon.com/dp/{asin}/?tag={associate_id}"
                
                parsed_results.append({
                    'asin': asin,
                    'title': title,
                    'price': price,
                    'original_price': orig_price,
                    'rating': rating,
                    'image_url': img_url,
                    'affiliate_link': affiliate_link
                })
                
            print(f"Scrape successful! Found {len(parsed_results)} products.", flush=True)
            return parsed_results
        except Exception as e:
            print(f"Scraper error: {e}", flush=True)
            
    print("All attempts failed. Returning empty list.", flush=True)
    return []


