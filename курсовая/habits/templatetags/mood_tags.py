from django import template

register = template.Library()

@register.simple_tag
def mood_emoji_url(mood):
    emoji_map = {
        'ecstatic': 'emoji/ecstatic.svg',
        'happy': 'emoji/happy.svg',
        'neutral': 'emoji/neutral.svg',
        'sad': 'emoji/sad.svg',
        'angry': 'emoji/angry.svg',
    }
    return emoji_map.get(mood, 'emoji/neutral.svg')