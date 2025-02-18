from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def ukrainian_date(value):
    months = {
        1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
        5: "травня", 6: "червня", 7: "липня", 8: "серпня",
        9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
    }
    
    return f"{value.day} {months[value.month]} {value.year} року, {value.hour:02d}:{value.minute:02d}"