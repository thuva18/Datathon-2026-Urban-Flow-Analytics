"""
chatbot/parameter_resolver.py
Resolves parameters like dates, times, and taxi zones from natural language.
"""
import re
import datetime
from difflib import get_close_matches
import pandas as pd

from chatbot.config import ZONES_FILE, DATASET_START, DATASET_END

# System date (as requested by user constraints for resolving "tomorrow", etc.)
SYSTEM_DATE = datetime.date(2026, 9, 12)

_zone_names_cache = []

def _get_zone_names():
    global _zone_names_cache
    if not _zone_names_cache:
        try:
            df = pd.read_csv(ZONES_FILE)
            _zone_names_cache = df['zone_name'].dropna().unique().tolist()
        except:
            _zone_names_cache = []
    return _zone_names_cache

def resolve_zone(zone_str: str) -> str | None:
    """Fuzzy match a zone name against the dataset's known zones."""
    if not zone_str:
        return None
    
    zone_str = zone_str.strip()
    zones = _get_zone_names()
    
    # Exact match (case insensitive)
    for z in zones:
        if z.lower() == zone_str.lower():
            return z
            
    # Fuzzy match
    matches = get_close_matches(zone_str, zones, n=1, cutoff=0.6)
    if matches:
        return matches[0]
        
    # Heuristics: JFK Airport
    if "jfk" in zone_str.lower():
        return "JFK Airport"
    # LaGuardia
    if "laguardia" in zone_str.lower() or "lga" in zone_str.lower():
        return "LaGuardia Airport"
    # Times Sq
    if "times sq" in zone_str.lower():
        return "Times Sq/Theatre District"
        
    return None

def resolve_date(date_str: str) -> str | None:
    """
    Resolve relative dates ("tomorrow", "today", "yesterday") to YYYY-MM-DD.
    If already YYYY-MM-DD, validate and return.
    """
    if not date_str:
        return None
        
    d = date_str.lower().strip()
    
    if d == "today":
        return SYSTEM_DATE.strftime("%Y-%m-%d")
    if d == "tomorrow":
        return (SYSTEM_DATE + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if d == "yesterday":
        return (SYSTEM_DATE - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
    # Check if format is YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', d):
        return d
        
    return None

def resolve_hour(time_str: str) -> int | None:
    """Resolve '8 AM', '18:00', 'evening rush' to an integer 0-23."""
    if not time_str:
        return None
        
    t = str(time_str).lower().strip()
    
    # "8 AM", "8am"
    m = re.match(r'^(\d{1,2})\s*(am|pm)$', t)
    if m:
        h = int(m.group(1))
        ampm = m.group(2)
        if ampm == "pm" and h < 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
        return h
        
    # "18:00" or just "18"
    m = re.match(r'^(\d{1,2})(:\d{2})?$', t)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return h
            
    # Period mappings
    if "morning rush" in t or "am rush" in t:
        return 8
    if "evening rush" in t or "pm rush" in t:
        return 17
    if "morning" in t:
        return 9
    if "afternoon" in t:
        return 14
    if "evening" in t:
        return 18
    if "night" in t:
        return 22
        
    return None

def get_dow(date_str: str) -> int | None:
    """Return Day of Week (0=Monday, 6=Sunday). Note: app.py uses 0=Mon, 6=Sun"""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.weekday()
    except:
        return None
        
def get_month(date_str: str) -> int | None:
    """Return month number (1-12)"""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.month
    except:
        return None
