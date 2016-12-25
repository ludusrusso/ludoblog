from . import main

@main.route('/')
def index():
    return '<h1>Benvenuti nel mio blog</h1>'
