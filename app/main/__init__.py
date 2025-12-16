from flask import Blueprint
main = Blueprint('main', __name__)

from . import views  # We don’t have custom error pages here.

