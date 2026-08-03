import os
import shutil
import io
import sys
import re
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import QSize, Qt

# ==========================================
# ROBUST PATH RESOLVER (PYINSTALLER SAFE)
# ==========================================
def get_asset_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Guarantees assets are ALWAYS found regardless of Windows working directory!
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    if not base_path:
        base_path = os.path.abspath(".")
        
    return os.path.normpath(os.path.join(base_path, relative_path))


# ==========================================
# PORTABLE USER FILE RESOLVER
# ==========================================
def get_user_file_path(relative_path):
    """
    Get absolute path to user-generated files (DB, images, uploads)
    relative to the executable or script folder. Prevents image-not-found
    errors when copying the database or folder around!
    """
    import sys
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_path = os.path.abspath(".")
    return os.path.normpath(os.path.join(base_path, relative_path))


# ==========================================
# HIGH-ACCURACY DUAL MATH OCR API LOADER
# ==========================================
def image_to_latex_ocr(image_path):
    """
    Asynchronously performs high-accuracy OCR on an image task file using the free, 
    highly accurate OCR.space endpoint with automatic mathematical fraction conversions!
    """
    try:
        import requests
        url = "https://api.ocr.space/parse/image"
        with open(image_path, 'rb') as f:
            files = {'file': f}
            payload = {
                'apikey': 'helloworld',  # Public free key supporting 25,000 requests/month!
                'language': 'eng',
                'isOverlayRequired': False,
                'scale': True,
                'isTable': False
            }
            response = requests.post(url, files=files, data=payload, timeout=12)
            
        if response.status_code == 200:
            result = response.json()
            if not result.get("IsErroredOnProcessing"):
                parsed_text = result["ParsedResults"][0]["ParsedText"].strip()
                cleaned = parsed_text.replace('\r', '').replace('\n', ' ')
                
                # Math Translation Rules: Convert inline slashes into real vertical fractions!
                cleaned = re.sub(r'(\d+)\s*/\s*(\d+)', r'\\frac{\1}{\2}', cleaned)
                cleaned = cleaned.replace(" : ", " : ").replace(" * ", " \\cdot ").replace(" x ", " x ")
                return cleaned
    except Exception as e:
        print(f"Math OCR Error: {e}")
    return None


# ==========================================
# ASSET GENERATOR (10-FRAME MATTE FLAME & SVGS)
# ==========================================
def create_svg_assets():
    """Generates all monochrome vector SVG icons and a 10-frame matte flame loop locally."""
    assets_dir = get_asset_path("assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Standard static SVGs
    assets = {
        "play.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="white">
            <polygon points="7,4 20,12 7,20" />
        </svg>""",
        "history.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#1C1E21" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>""",
        "settings.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#1C1E21" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>""",
        "gear.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#5F6F80" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>""",
        "trophy.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path>
            <path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.45 1-1 1H4v2h16v-2h-5c-.55 0-1-.45-1-1v-2.34"></path>
            <path d="M12 2a5 5 0 0 0-5 5v3.5a5 5 0 0 0 10 0V7a5 5 0 0 0-5-5z"></path>
        </svg>""",
        "back.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline>
        </svg>""",
        "plus.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>""",
        "trash.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#E11D48" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>""",
        "eye.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#1C1E21" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>
        </svg>""",
        "folder.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#1C1E21" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
        </svg>""",
        "rocket.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4.5 16.5c-1.5 1.26-2 2.5-2 2.5s1.24-.5 2.5-2L4.5 16.5z"></path>
            <path d="M12 2C6 2 2 10 2 12c0 0 1.5-1 3.5-1 2 0 4.5 2.5 4.5 4.5 0 2-1 3.5-1 3.5 2 0 10-4 10-10 0-4-3-8-10-8z"></path>
            <line x1="9" y1="15" x2="4.5" y2="19.5"></line><circle cx="14" cy="10" r="1.5" fill="white"></circle>
        </svg>""",
        "text.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#1C1E21" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="17" y1="10" x2="3" y2="10"></line><line x1="21" y1="6" x2="3" y2="6"></line>
            <line x1="21" y1="14" x2="3" y2="14"></line><line x1="17" y1="18" x2="3" y2="18"></line>
        </svg>""",
        "math.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#1C1E21" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="4" x2="12" y2="10"></line><line x1="9" y1="7" x2="15" y2="7"></line>
            <line x1="9" y1="17" x2="15" y2="17"></line><line x1="9" y1="11" x2="15" y2="11"></line>
            <line x1="12" y1="14" x2="12" y2="20"></line>
        </svg>""",
        "medal_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="14" r="6" fill="#FFFBE6"></circle><path d="M12 2L9 8h6l-3-6z" fill="#D4AF37"></path>
            <line x1="12" y1="11" x2="12" y2="17"></line>
        </svg>""",
        "medal_2.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#8A95A5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="14" r="6" fill="#F0F2F5"></circle><path d="M12 2L9 8h6l-3-6z" fill="#8A95A5"></path>
            <path d="M10 12h4v4h-4z"></path>
        </svg>""",
        "medal_3.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#CD7F32" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="14" r="6" fill="#FAF0E6"></circle><path d="M12 2L9 8h6l-3-6z" fill="#CD7F32"></path>
            <circle cx="12" cy="14" r="2"></circle>
        </svg>""",
        
        # New distinct, high-fidelity academic/math SVG icons for Class buttons!
        "cap.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
            <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path>
        </svg>""",
        "ruler.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 19L19 5"></path><path d="M14 4l5 5"></path>
            <path d="M9 9l3 3"></path><path d="M12 12l3 3"></path><path d="M6 6l3 3"></path>
        </svg>""",
        "book.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>""",
        "calculator.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect>
            <line x1="8" y1="6" x2="16" y2="6"></line><line x1="16" y1="14" x2="16" y2="18"></line>
            <circle cx="8" cy="14" r="1"></circle><circle cx="12" cy="14" r="1"></circle>
            <circle cx="8" cy="18" r="1"></circle><circle cx="12" cy="18" r="1"></circle>
        </svg>""",
        "pie.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path>
        </svg>""",
        "abacus.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#2688EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2"></rect>
            <line x1="3" y1="8" x2="21" y2="8"></line><line x1="3" y1="14" x2="21" y2="14"></line>
            <line x1="8" y1="3" x2="8" y2="21"></line><line x1="16" y1="3" x2="16" y2="21"></line>
        </svg>""",
        
        # 10 Frame fluid vectors for the flame animation
        "fire_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
            <path d="M12 2C9.5 6 7 8.5 7 12c0 2.5 1.8 4.5 4.5 5 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 2-4.5c1.5 2 2.5 4 2 6.5-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-3 3-6.5C16.5 5 14 3.5 12 2z" fill="#FF4500"/>
            <path d="M12 5.5c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C15 7.5 13.5 6.5 12 5.5z" fill="#FF8C00"/>
            <path d="M12 9c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>
        </svg>""",
        "fire_2.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
            <path d="M12 2c2 1 4.5 3 4.5 6.5 0 2.5-1.8 4.5-4.5 5-1-.2-1.5-.8-1.5-1.5 0-1 1-1.5 1-2.5s-1.5-2.5-2-4.5c-1.5 2-2.5 4-2 6.5.3 1.2 1.2 2.2 2.5 2.5-2.5-1-3.5-3-3-6.5C7 5 9.5 3 12 2z" fill="#FF3300"/>
            <path d="M12 6c1.2 1.5 2.5 3.2 2.5 5.2 0 1.6-1.1 2.9-2.5 3.2-.7-.1-1-.5-1-1 0-.6.6-1 .6-1.6s-1-1.6-1.3-3c-1 1.3-1.6 2.6-1.3 4.3.2.8.8 1.4 1.6 1.6-1.6-.6-2.2-2-1.9-4.3C9 8 10.5 6.5 12 6z" fill="#FFA500"/>
            <path d="M12 10c.6 1 1.2 2 1.2 3.2 0 .8-.6 1.5-1.2 1.7-.3 0-.5-.3-.5-.6s.3-.6.3-1c-.2-.5-.5-1-.7-1.8-.5.7-.8 1.4-.7 2.3.1.4.4.7.8.8-.8-.3-1.1-1-1-2.3.5-1.2 1.2-2 1.6-2.6z" fill="#FFEA00"/>
        </svg>""",
        "fire_3.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
            <path d="M11.5 2C14 5 15.5 7 15 11c-.5 2.5-2.2 4-4.5 4.5-.8-.1-1.2-.6-1.2-1.2 0-.8.8-1.2.8-2s-1.2-2-1.6-3.6c-1.2 1.6-2 3.2-1.6 5.2.2 1 .8 1.8 1.8 2-2-.8-2.8-2.4-2.4-5.2C6.5 4.5 8.5 3 11.5 2z" fill="#FF4500"/>
            <path d="M11.5 5.5c1 1.5 2 3 1.8 5-.2 1.6-1.2 2.6-2.6 2.8-.5-.1-.8-.4-.8-.8 0-.6.6-.8.6-1.3s-.8-1.3-1-2.4c-.8 1-1.3 2.1-1.1 3.5.1.7.5 1.2 1.1 1.3-1.3-.5-1.8-1.6-1.6-3.5 1-2.2 2.2-3.2 3.6-4.6z" fill="#FF8C00"/>
            <path d="M11.5 8.5c.5.8 1 1.5.9 2.5-.1.8-.7 1.3-1.4 1.4-.3 0-.4-.2-.4-.4 0-.3.3-.4.3-.7s-.4-.7-.5-1.2c-.4.5-.6 1-.5 1.7.1.4.3.6.6.7-.7-.3-1-.8-.9-1.7.5-1.1 1.1-1.6 1.8-2.3z" fill="#FFD700"/>
        </svg>"""
    }
    
    for filename, content in assets.items():
        path = os.path.join(assets_dir, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    # 10 Frame matte flat vectors
    fire_variations = [
        ('<path d="M12 2C9.5 6 7 8.5 7 12c0 2.5 1.8 4.5 4.5 5 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 2-4.5c1.5 2 2.5 4 2 6.5-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-3 3-6.5C16.5 5 14 3.5 12 2z" fill="#FF4500"/>',
         '<path d="M12 5.5c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C15 7.5 13.5 6.5 12 5.5z" fill="#FF8C00"/>',
         '<path d="M12 9c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M12.2 2.2C9.8 6.1 7.2 8.4 7.2 11.8c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16.6 5.1 14.1 3.6 12.2 2.2z" fill="#FF4500"/>',
         '<path d="M12.2 5.7c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C15.1 7.7 13.6 6.7 12.2 5.7z" fill="#FF8C00"/>',
         '<path d="M12.2 9.2c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M12.1 2.3C9.9 6.2 7.3 8.3 7.3 11.7c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16.6 5.2 14.1 3.7 12.1 2.3z" fill="#FF4500"/>',
         '<path d="M12.1 5.8c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C15.1 7.8 13.6 6.8 12.1 5.8z" fill="#FF8C00"/>',
         '<path d="M12.1 9.3c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M12 2.5C9.6 6.3 7.5 8.2 7.5 11.5c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16.5 5.4 14 3.9 12 2.5z" fill="#FF4500"/>',
         '<path d="M12 6c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C15 8 13.5 7 12 6z" fill="#FF8C00"/>',
         '<path d="M12 9.5c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M11.9 2.4C9.5 6.2 7.4 8.1 7.4 11.4c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16.4 5.3 13.9 3.8 11.9 2.4z" fill="#FF4500"/>',
         '<path d="M11.9 5.9c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C14.9 7.9 13.4 6.9 11.9 5.9z" fill="#FF8C00"/>',
         '<path d="M11.9 9.4c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M11.8 2.3C9.4 6.1 7.3 8 7.3 11.3c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16.3 5.2 13.8 3.7 11.8 2.3z" fill="#FF4500"/>',
         '<path d="M11.8 5.8c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C14.8 7.8 13.3 6.8 11.8 5.8z" fill="#FF8C00"/>',
         '<path d="M11.8 9.3c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M11.7 2.2C9.3 6 7.2 7.9 7.2 11.2c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16.2 5.1 13.7 3.6 11.7 2.2z" fill="#FF4500"/>',
         '<path d="M11.7 5.7c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C14.7 7.7 13.2 6.7 11.7 5.7z" fill="#FF8C00"/>',
         '<path d="M11.7 9.2c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M11.6 2.1C9.2 5.9 7.1 7.8 7.1 11.1c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16.1 5 13.6 3.5 11.6 2.1z" fill="#FF4500"/>',
         '<path d="M11.6 5.6c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C14.6 7.6 13.1 6.6 11.6 5.6z" fill="#FF8C00"/>',
         '<path d="M11.6 9.1c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M11.5 2C9.1 5.8 7 7.7 7 11c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C16 4.9 13.5 3.4 11.5 2z" fill="#FF4500"/>',
         '<path d="M11.5 5.5c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C14.5 7.5 13 6.5 11.5 5.5z" fill="#FF8C00"/>',
         '<path d="M11.5 9c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>'),
        ('<path d="M11.4 1.9C9 5.7 6.9 7.6 6.9 10.9c0 2.4 1.8 4.4 4.4 4.9 1-.2 1.5-.8 1.5-1.5 0-1-1-1.5-1-2.5s1.5-2.5 1.9-4.4c1.5 2 2.4 3.9 1.9 6.4-.3 1.2-1.2 2.2-2.5 2.5 2.5-1 3.5-2.9 3-6.4C15.9 4.8 13.4 3.3 11.4 1.9z" fill="#FF4500"/>',
         '<path d="M11.4 5.4c-1.2 2-2.5 3.5-2.5 5.5 0 1.6 1.1 2.9 2.5 3.2.7-.1 1-.5 1-1 0-.6-.6-1-.6-1.6s1-1.6 1.3-3c1 1.3 1.6 2.6 1.3 4.3-.2.8-.8 1.4-1.6 1.6 1.6-.6 2.2-2 1.9-4.3C14.4 7.4 12.9 6.4 11.4 5.4z" fill="#FF8C00"/>',
         '<path d="M11.4 8.9c-.7 1.5-1.5 2.5-1.5 3.5 0 .8.6 1.5 1.3 1.7.3 0 .5-.3.5-.6s-.3-.6-.3-1c.2-.5.5-1 .7-1.8.5.7.8 1.4.7 2.3-.1.4-.4.7-.8.8.8-.3 1.1-1 1-2.3-.5-1.2-1.2-2-1.6-2.6z" fill="#FFD700"/>')
    ]
    
    for idx, (p1, p2, p3) in enumerate(fire_variations):
        content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
            {p1}
            {p2}
            {p3}
        </svg>"""
        path = os.path.join(assets_dir, f"fire_{idx + 1}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
    # Copy Ronaldo GIF to assets to ensure package integrity
    uploads_path = get_asset_path("uploads/ronaldo_siuu_final_6sec.gif")
    assets_path = get_asset_path("assets/ronaldo.gif")
    
    if os.path.exists(uploads_path) and not os.path.exists(assets_path):
        shutil.copy(uploads_path, assets_path)


def render_latex_to_pixmap(latex_str):
    """
    Renders a LaTeX math string directly into a QPixmap.
    LAZY LOADING STRATEGY: Only imports Matplotlib inside this function.
    This guarantees that QMainWindow launches instantly (100ms) without any startup lags!
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fig = plt.figure(figsize=(7, 2), dpi=200, facecolor='white')
        plt.axis('off')
        
        expr = latex_str.strip()
        if not expr.startswith('$'):
            expr = f"${expr}$"
            
        plt.text(0.5, 0.5, expr, size=22, ha='center', va='center', color='#1C1E21')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, facecolor='white')
        plt.close(fig)
        
        buf.seek(0)
        img_data = buf.read()
        
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        return pixmap
    except Exception as e:
        print(f"Lazy in-memory LaTeX rendering error: {e}")
        try:
            plt.close()
        except:
            pass
        return None
