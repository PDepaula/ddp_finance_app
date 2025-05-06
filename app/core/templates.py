# app/core/templates.py
from fastapi.templating import Jinja2Templates
from app.utils.date_utils import get_current_year
from app.utils.template_utils import add_template_globals
from app.utils.filter_utils import pluralize

# Create a single shared instance of templates
templates = Jinja2Templates(directory="app/templates")

# Add global functions
add_template_globals(templates.env, {
    "current_year": get_current_year
})

# Add custom filters
templates.env.filters["pluralize"] = pluralize