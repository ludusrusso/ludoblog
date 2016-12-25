from flask import render_template
from . import main

@main.app_errorhandler(403)
def forbidden(e):
    return 'errore 403 - Accesso Negato', 403

@main.app_errorhandler(404)
def page_not_found(e):
    return 'errore 404 - File non trovato', 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return 'errore 500 - Errore interno al server', 500
