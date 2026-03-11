from .light import LIGHT_THEME
from .beige import BEIGE_THEME
from .dark import DARK_THEME

THEMES = {
    "Light": LIGHT_THEME,
    "Beige": BEIGE_THEME,
    "Dark":  DARK_THEME,
}

def get_theme_css(name: str) -> str:
    theme = THEMES.get(name, LIGHT_THEME)
    return theme["css"]

def get_theme_config(name: str) -> dict:
    theme = THEMES.get(name, LIGHT_THEME)
    return theme["config"]
