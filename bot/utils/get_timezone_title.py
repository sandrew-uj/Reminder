
def plus_or_minus(tz: int):
    return "+" if tz >= 0 else ""


def get_title_by_tz(tz: int):
    city: str = "NONAME"
    if tz == 2:
        city = "KALT (Калининград)"
    elif tz == 3:
        city = "MSK (Москва)"
    elif tz == 4:
        city = "SAMT (Самара)"
    elif tz == 5:
        city = "YEKT (Екатеринбург)"
    elif tz == 6:
        city = "OMST (Омск)"
    elif tz == 7:
        city = "KRAT (Красноярск)"
    elif tz == 8:
        city = "IRKT (Иркутск)"
    elif tz == 9:
        city = "YAKT (Якутск)"
    elif tz == 10:
        city = "VLAT (Владивосток)"
    elif tz == 11:
        city = "MAGT (Магнитогорск)"
    elif tz == 12:
        city = "PETT (Камчатка)"
    return f"MSK{plus_or_minus(tz-3)}{tz-3}(UTC{plus_or_minus(tz)}{tz}) - {city}"