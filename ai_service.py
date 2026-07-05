import google.generativeai as genai
import os
import re

# Configure Gemini AI client
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "your-gemini-key-here"))

def clean_role(role_str):
    if not role_str:
        return "analytical, business, or operational opportunities"
    
    role_lower = role_str.lower()
    
    # If the role is messy, a scrambled location string, or standard generic placeholder
    messy_indicators = [
        'lead dublin', 'discovered lead', 'academic', 'hr', 'team', 'contact', 
        'coordinator', 'staff', 'admin', 'professional staff', 'recruitment',
        'retail', 'education', 'marketing', 'consultant', 'office', 'hello',
        'support', 'info'
    ]
    
    if any(indicator in role_lower for indicator in messy_indicators) or len(role_str) < 3:
        return "analytical, business, or operational opportunities"
        
    if role_lower == 'lead':
        return "analytical, business, or operational opportunities"
        
    return f"{role_str} or analytical opportunities"

def generate_cold_email(profile, recruiter):
    """
    Generates a personalized cold email using AI, or falls back to a template.
    """
    company = recruiter.company_name or 'your team'
    raw_role = recruiter.target_role or 'analytical opportunities'
    role = clean_role(raw_role)
    recipient = recruiter.recruiter_name or 'Hiring Manager'
    
    # Safe name cleansing to prevent weird greetings (like "Dear Candidateprotection,")
    if not recipient or any(token in recipient.lower() for token in ['hiring', 'team', 'recruiter', 'candidate', 'consortium', 'comms', 'editor', 'recruit', 'info', 'admin', 'office', 'hello', 'contact', 'support']):
        recipient = 'Hiring Manager'
    elif ' ' not in recipient and len(recipient) > 10:
        recipient = 'Hiring Manager'
        
    prompt = f"""
    Write a highly professional, versatile, and slightly bulkier (around 100-120 words) cold email from {profile.name} to {recipient} at {company}.
    
    The email must:
    1. Pitch {profile.name} as a highly adaptable, multidisciplinary professional holding dual Master's degrees in Financial Engineering and Data Science.
    2. Be broad and comprehensive enough to apply to various departments (such as operations, business analysis, financial strategy, project management, or general corporate support).
    3. Express a keen interest in exploring potential professional opportunities within {company}'s broader team, rather than a single specific role.
    4. HIGHLIGHTS: Focus on an adaptable skillset combining quantitative modeling, strategic problem-solving, and administrative agility. Emphasize eagerness to contribute to the organization's goals in any capacity where this diverse skillset adds value.
    5. CRITICAL: DO NOT list specific technology software (like SQL, Python, Power BI) to keep the doors wide open. Keep the description general and high-impact.
    6. SUBJECT: Professional Opportunities & Strategic Collaboration - Success Ehiabor.
    7. SALUTATION: Address {recipient} directly (e.g., "Dear {recipient}," or "Dear Hiring Manager,").
    8. Suggest a brief introductory chat and mention the attached CV.
    
    Output ONLY:
    Subject: [Refined Subject Line]
    
    [Email Body]
    """
    
    try:
        print(f"Generating cold email for {recipient} at {company}...", flush=True)
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        
        full_prompt = f"""
        Your tone is confident, professional, and commercially focused.
        Focus on expressing interest in general professional opportunities, operations, business strategy, or analyst roles at {company} in a clean, comprehensive way.
        CRITICAL: DO NOT list specific tech tools like SQL, Power BI, Python, or data modeling. Keep the description general, bulky, and versatile.
        CRITICAL: DO NOT flatter the company, guess their products, or use placeholders. Write the email as a finished, ready-to-send document.
        
        Task: {prompt}
        """
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3)
        )
        content = response.text.strip()
        
        # Parse subject/body
        if "Subject:" in content:
            parts = content.split("\n", 1)
            subject = parts[0].replace("Subject: ", "").strip()
            body = parts[1].strip() if len(parts) > 1 else content
        else:
            subject = f"Professional Opportunities & Strategic Collaboration - {profile.name}"
            body = content
 
        # CLEANSING: Remove any remaining placeholders/parentheses that the AI might have hallucinated
        subject = re.sub(r'[\[\({].*?[\]\)}]', '', subject).strip()
        body = re.sub(r'[\[\({].*?[\]\)}]', '', body).strip()
        body = body.replace('Hiring Manager [Last Name]', 'Hiring Manager')
        body = body.replace('Hiring Manager [Name]', 'Hiring Manager')
 
        # Standardized Signature
        phone = profile.phone or '+44 7349 317709'
        linkedin = profile.linkedin_url or 'https://www.linkedin.com/in/successehiabor'
        signature = f"\n\nBest regards,\n\n{profile.name}\n{phone}\nLinkedIn: {linkedin}"
        
        # Robustly replace any existing sign-off with our standardized one
        sign_off_patterns = [
            r"(?i)(Kind regards|Best regards|Best|Sincerely|Regards|Thanks|Thank you|Yours)(,)?(\s*[\n\r]+\s*)?(" + re.escape(profile.name) + r")?.*$",
            r"(?i)\s*[\n\r]+\s*(" + re.escape(profile.name) + r")\s*$", # Catches just the name on a new line
            r"(?i)(Kind regards|Best regards|Best|Sincerely|Regards|Thanks|Thank you|Yours)(,)?\s*$" # Catches sign-off without name
        ]
        
        cleaned_body = body
        for pattern in sign_off_patterns:
            if re.search(pattern, cleaned_body, re.MULTILINE):
                cleaned_body = re.sub(pattern, "", cleaned_body, flags=re.MULTILINE).strip()
                break # Only need to find one
        
        # Always append our clean signature
        body = cleaned_body + signature
        
        # Final safety: Replace smart quotes to prevent encoding issues
        body = body.replace('—', '-').replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
            
        return subject, body
        
    except Exception as e:
        print(f"AI Generation failed, using versatile analyst template: {e}")
        company = recruiter.company_name or 'your team'
        
        subject = f"Professional Opportunities & Strategic Collaboration - {profile.name}"
        body = f"Dear {recipient},\n\nI am writing to express my strong interest in exploring potential professional opportunities within {company}. As a multidisciplinary professional holding dual Master's degrees in Financial Engineering and Data Science, I offer a unique combination of analytical rigor, quantitative problem-solving, and strategic business acumen.\n\nMy background enables me to quickly adapt to various departmental needs, whether in business analysis, financial modeling, operational support, project coordination, or data-driven strategy. I am highly versatile and eager to contribute to your team's broader objectives in any capacity where my diverse skillset can add immediate value.\n\nI have attached my CV for your review and would welcome the opportunity for a brief introductory call to discuss how my background and adaptable skill set can support your organization's goals.\n\nBest regards,\n\n{profile.name}\n{profile.phone or '+44 7349 317709'}\nLinkedIn: {profile.linkedin_url or 'https://www.linkedin.com/in/successehiabor'}"
 
        body = body.replace('—', '-').replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
        return subject, body

def generate_follow_up(profile, recruiter):
    return f"""Subject: Touching base: {profile.name} x {recruiter.company_name}

Hi {recruiter.recruiter_name},

I'm checking back in to see if you've had a moment to review my profile for the {recruiter.target_role} opening. 

I’m particularly eager to discuss how my work with pricing analytics and retail data could support the current objectives at {recruiter.company_name}. If the timing is better now, I’d love to connect.

Best regards,
{profile.name}"""
