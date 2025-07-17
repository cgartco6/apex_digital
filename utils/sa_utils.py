import requests
import datetime
import json

def get_loadshedding_schedule(area_id, province='gauteng'):
    """Get loadshedding schedule from Eskom API"""
    try:
        response = requests.get(f"https://loadshedding.eskom.co.za/LoadShedding/GetScheduleM/{area_id}/1")
        schedule = response.json()
        return {
            "area": area_id,
            "province": province,
            "schedule": schedule,
            "updated": datetime.datetime.now().isoformat()
        }
    except:
        return {"error": "Schedule unavailable"}

def format_currency(amount):
    """Format amount as South African Rand"""
    return f"R{amount:,.2f}"

def get_sa_public_holidays(year):
    """Get South African public holidays"""
    holidays = [
        "01-01: New Year's Day",
        "03-21: Human Rights Day",
        "04-27: Freedom Day",
        "05-01: Workers' Day",
        "06-16: Youth Day",
        "08-09: National Women's Day",
        "09-24: Heritage Day",
        "12-16: Day of Reconciliation",
        "12-25: Christmas Day",
        "12-26: Day of Goodwill"
    ]
    
    # Calculate moving holidays
    easter = get_easter_date(year)
    holidays.append(f"{(easter - datetime.timedelta(days=2)).strftime('%m-%d')}: Good Friday")
    holidays.append(f"{(easter + datetime.timedelta(days=1)).strftime('%m-%d')}: Family Day")
    
    return sorted(holidays)

def get_easter_date(year):
    """Calculate Easter Sunday date (Gauss algorithm)"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    month = (h + l - 7*m + 114) // 31
    day = ((h + l - 7*m + 114) % 31) + 1
    return datetime.date(year, month, day)

def translate_to_zulu(text):
    """Basic English to isiZulu translation"""
    translations = {
        "hello": "Sawubona",
        "thank you": "Ngiyabonga",
        "app": "Uhlelo",
        "website": "Iwebhusayithi",
        "payment": "Inkokhelo",
        "support": "Ukusekela",
        "digital": "Didijithali"
    }
    for eng, zulu in translations.items():
        text = text.replace(eng, zulu)
    return text
