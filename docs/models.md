# 3. Configurazione e Database

Una volta impostata graficamente la nostra applicazione, siamo pronti a costruire un database per la gestione di utenti e post del blog. Ma prima di tutto, è importante impostare un file di configurazione per organizzare bene la configurazione della nostra applicazione. 

## File di configurazione

Lo scopo del file di configurazione è duplice:

- inserire in un unico file tutte le variabili di configurazione della nostra applicazione
- permettere di avere differenti set di configurazione in base a dove viene lanciata l'applicazione. Possiamo ad esempio avere un set di configurazione di **sviluppo** e un set di configurazione **produzione**, come faremo in seguto.



Creiamo un file `/config.py` e implementiamo il seguente codice

```python
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'stringa difficile da indovinare'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

Questo sarà lo scheletro della nostra applicazione, in particolare abbiamo un oggetto `Config` da cui faremo derivare i vari set di configurazioni della nostra applicazione. Per ora useremo solo l'oggetto `DevelopmentConfig` in cui inseriremo i set di configurazione per la macchina su cui svilupperemo il blog. In futuro, popoleremo il file anche con altri oggetti (ad esempio per il testing) e popoleremo l'oggetto `ProductionConfig`.

Il dizionario `config`, invece, serve semplicemente ad associare un oggetto di configurazione ad una specifica stringa.

### SECRET_KEY

Per il momento, l'unico parametro di configuraizone utilizzato è `SECRET_KEY`. Questa variabile è importante in quanto è usata da `Flask` e da molte estensioni per criptare dati. Quindi è molto importante che sia sicura e che non venga divulgata. 

```python
SECRET_KEY = os.environ.get('SECRET_KEY') or 'stringa difficile da indovinare'
```

Per ragioni di sicurezza e per evitare di scrivere la chiave direttamente nel file, sfruttiamo le variabili d'ambiente. In questo modo, python controllerà se la variabile d'ambienete `SECRET_KEY` è stata settata ed utilizzerà il suo valore. Se non è stata settata, utilizzerò come default `'stringa difficile da indovinare'`. In fase di sviluppo non è importante settare questa variabile, ma sarà essenziale farlo in fase di produzione.


### Usiamo il file per configurare l'app

Una volta creato il file e gli oggietti di configurazione, dobbiamo usare queste informazioni nella funzione `create_app`. Per farlo, modofichiamo il file `blog/__init__.py` come segue

```python
# ...
from config import config

#...

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
	#...
#...
```

In questo modo, facciamo si che l'applicazione venga configurata in base alle varibabili contenute nell'oggetto di configurazione scelto.
Si noti che passiamo `'deafult'` come valore di default al parametro `config_name`. In quasto modo, se creiamo l'app senza passare esplicitamente il parametro, verrà automaticamente caricato il set di configurazione `DevelopmentConfig`.

## Configurazione del database con Flask-SQLAlchemy

A questo punto siamo pronti a configurare il nostro database. Per gestirlo, utilizzeremo due importantissime estensioni di Flask: 

- **Flask-SQLAlchemy**, molto utile per la gestione del db, in particolare semplifica l'accesso e la creazione di nuove entries del db.
- **Flask-Migrate**, in accoppiata con flask-script, consente di automatizzare l'evoluzione del database stesso.

Inoltre, utilizzeremo fin da subito un'utilissima estensione chiamata **Flask-Security**, che servirà per gestire l'accesso e l'autenticazione agli utenti del blog. Siccome questa estensione è fortemente legata alla struttura del db, la installaremo e utilizzeremo fin da subito.

Per installare questi pacchetti, utilizziamo come al solito il comando

```
(blog)$ pip install flask-sqlalchemy flask-security flask-migrate
```

#### Configurazione di SQLAlchemy

Per prima cosa, dobbiamo inizializzare e configurare flask-sqlalchemy. Per inizializzarlo, modificando il file  `blog/__init__.py` come segue

```python
#...
from flask_sqlalchemy import SQLAlchemy
#...
db = SQLAlchemy()


def create_app(config_name='default'):
	#...
    db.init_app(app)
    #...
#...

```

Inoltre, dobbiamo aggiungere alcune variabili di configurazione nel nostro file `/config.py`.

Modifichiamo l'oggetto `Config` come segue:

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'stringa difficile da indovinare'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass
```

`SQLALCHEMY_COMMIT_ON_TEARDOWN` abilita commit automatici del database ogni volta che gli oggetti vengono creati e modificati senza che questo venga esplicitamente forzato nel codice. Lo inseriamo nell'oggetto `Config` in modo che sia abilitato in ogni altra configurazione che creeremo.


Modifichiamo l'oggetto `Config` come segue:

```python
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
```

In questo modo abilitiamo la creazione del database (sqlite) di development nel file `data-dev.sqlite` all'interno della cartella in cui l'applicazione è lanciata. Sfruttiamo la variabile di ambiente `DEV_DATABASE_URL` per cambiare il percordo del db di development senza modificare il file.

### Creiamo i models del nostro DB

I *models* di un database sono degli oggetti che rappresentano una table all'interno del nostro database, per ora costruiremo i due *models* richiesti da flask-security per funzionare, cioè il model **User** e il model **Role**.

Creiamo un file `blog/models.py` in cui andremo a implementare i vari models come segue

```python
from . import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return "<Role %r>"%self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, required=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(255))
    about = db.Column(db.Text())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "<User %r>"%self.email


```

In questo modo abbiamo creato due models (**User** e **Role**) che sono collegati tra loro da una relazione *Molto a Molti* (`roles_users`).
In altre parole, ogni utente può avere dei ruoli, e viceversa, ogni ruolo può essere associato a più di un utente. Abbiamo inoltre aggiunto le colonne `username` e `about` che non sono richiesti da `flask-security` ma saranno importanti per lo sviluppo del blog. Utilizzando questi due modelli, flask-security permette di gestire gli accessi al sito e anche alle singole pagine del sito stesso. 

### Configuriamo Flask-Security

Una volta creati models essenziali, possiamo inizializzare flask-security in modo da poter gestire in modo semplice l'accesso alla nostra applicazione. Per fare questo, modifichiamo il file `blog/__init__.py` come segue:

```python
#...

from flask_security import Security, SQLAlchemyUserDatastore
#...
security = Security()
#...

def create_app(config_name='default'):
    #...
    from .models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    #...
```

In questo modo, abbiamo informato flask-security di utilizzare i due modelli per gestire la sicurezza del nostro blog.

### Inizializzazione del DB

Per poter utilizzare correttamente il blog con flask-security, è importante che esista almeno un utente attivo nel momento in cui viene lanciata l'applicazione. Per questo motivo, è essenziale automatizzare la nostra applicazione in modo da riempire il DB in fase di configurazione. Per fare questo, creeremo delle funzioni `static` all'interno dei due modelli che permettono di automatizzare il processo di inizializzazione dei ruoli e degli utenti.

In particolare, inizializzeremo il DB con due ruoli, `admin`, `publisher` e `user`. Inoltre, creeremo un utente admin con mail e password salvate dentro due variabili di configurazione `BLOG_ADMIN_MAIL` e `BLOG_ADMIN_PASSWORD`.

Andiamo prima di tutto a settare le due variabili nel file `config.py` ed in particolare nell'oggetto `Config`. Come al solito, utilizzeremo le variabili di ambiente per sovrascrivere queste variabili senza necessariamente riverarle nel file.

```python
class Config:
    #...
    BLOG_ADMIN_MAIL = os.environ.get('BLOG_ADMIN_MAIL') or 'admin@admin.com'
    BLOG_ADMIN_PASSWORD = os.environ.get('BLOG_ADMIN_PASSWORD') or 'admin'
    #...
```

A questo punto, creiamo la funzione per generare i ruoli, inserendola nell'oggetto `Role` del file `blog/models.py`

```python
class Role(db.Model, RoleMixin):
    #...
    @staticmethod
    def insert_roles():
        for role_name in "admin publisher user".split():
            if Role.query.filter_by(name=role_name).first() is None:
                role = Role(name = role_name)
                db.session.add(role)
        db.session.commit()
```

La funzione `insert_roles` controlla che ognuno dei tre ruoli esista nel db utilizzato e nel caso lo inserisce.

Allo stesso modo, creiamo una funzione all'interno dell'oggetto `User` che crea l'utente amministratore.

```python
class User(db.Model, UserMixin):
    #...
    @staticmethod
    def insert_admin():
        from flask import current_app
        if User.query.filter_by(email=current_app.config['BLOG_ADMIN_MAIL']).first() is None:
            user = User(
                email=current_app.config['BLOG_ADMIN_MAIL'],
                password=current_app.config['BLOG_ADMIN_PASSWORD'],
                active=True)
            user.roles.append(Role.query.filter_by(name='admin').first())
            db.session.add(user)
            db.session.commit()
```

Notare che accediamo all'oggetto `current_app` che mette a disposizione flask per indicare l'oggetto applicazione. 

## Gezione del Database con Flask-Migrate e Flask-Script

Abbiamo scritto tutto il necessario per creare ed inizializzare il nostro database. A questo punto non resta altro da fare che creare fisicamente il database ed iniziare ad utilizzarlo.

Per fare questo, dobbiamo utilizzare **flask-migrate** per generare i comandi per la gestione del database. Inoltre, creeremo un nostro comando personalizzato per il deploy nel database di ruoli e amministratore.

### Configurazione e Utilizzo di Flask-Migrate

Per utilizzare Flask-Migrate, accediamo al file `/manage.py` e modifichiamolo come segue

```
#!/usr/bin/env python

from blog import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

#...

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

#...
```

A questo punto, siamo pronti per utilizzare flask-migrate. 
Per prima cosa, dobbiamo inizializzare la cartella di gestione delle migrazioni. Questa cartella conterrà tutti gli scripts generati automaticamente da flask-migrate che tengono traccia dell'evoluzione nel tempo dei *models* del db stesso.

Per farlo, utilizziamo il comando

```
(blog)$ ./manage.py db init
```

che restituirà un output simile al seguente se tutto va bene

```  
  Creating directory /Users/ludus/develop/tutorials/ludoblog/project/migrations ... done
  Creating directory /Users/ludus/develop/tutorials/ludoblog/project/migrations/versions ... done
  Generating /Users/ludus/develop/tutorials/ludoblog/project/migrations/alembic.ini ... done
  Generating /Users/ludus/develop/tutorials/ludoblog/project/migrations/env.py ... done
  Generating /Users/ludus/develop/tutorials/ludoblog/project/migrations/env.pyc ... done
  Generating /Users/ludus/develop/tutorials/ludoblog/project/migrations/README ... done
  Generating /Users/ludus/develop/tutorials/ludoblog/project/migrations/script.py.mako ... done
  Please edit configuration/connection/logging settings in '/Users/ludus/develop/tutorials/ludoblog/project/migrations/alembic.ini' before proceeding.
```

A questo punto, vedrete apparire una nuova cartella chiamata `migrations/` nella cartella principale. Qui verranno contenuti tutti i file di migrazione che generemo. 

Per crare un file di configurazione, utilizziamo il comando

```
(blog)$ ./manage.py db migrate -m "creazione User Role"
```

che genererà un output simile al seguente

```python
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'roles'
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'roles_users'
  Generating /Users/ludus/develop/tutorials/ludoblog/project/migrations/versions/fbdace17c6b3_creazione_user_role.py ... done
```

A questo punto, non ci resta che applicare la migrazione appena generata al database, usando il comando

```
(blog)$ ./manage.py db upgrade
```
Il cui output sarà

```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> fbdace17c6b3, creazione User Role
```

Perfetto, addesso abbiamo creato un database (che al momento sarà vuoto). Se tutto va bene dovrebbe essere apparso un file chiama `data-dev.sqlite` nella cartella principale dell'applicazione.

### Creazione di uno script di Deploy

Prima di procedere, dobbiamo creare uno script che inizializzi il database, in modo da iniziare a popolarlo. Facciamo anche in modo che questo script esegua il comando `upgrade` del database in modo da non doverlo chiamare ogni volta a mano.

Per farlo, modifichiamo nuovamente il file `manage.py` come segue

```python
#...
@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from blog.models import Role, User

    print 'INFO  [deploy command] migrate database to latest revision'
    upgrade()

    print 'INFO  [deploy command] create user roles'
    Role.insert_roles()

    print 'INFO  [deploy command] create admin user'
    User.insert_admin()
#...
```

E potremmo quindi utilizzare il comando appena definito come segue

```
(blog)$ ./manage.py deploy
```

Che rilascerà il seguente output

```
INFO  [deploy command] migrate database to latest revision
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [deploy command] create user roles
INFO  [deploy command] create admin user
```

## Creazione di barre di navigazione dinamiche

A questo punto, il database è pronto ed inizializzato, solo che, al momento, non esistono GUI nella nostra applicazione per gestirlo e visualizzarlo.

La prima cosa (quella più semplice) per verificare se siamo loggati o no è aggiungere un nuovo elemento nella NavBar che appare solo se l'utente ha correttamente eseguito il login nell'applicazione.

Per seguire lo standard di un po' tutti i siti, dobbiamo inserire questo elemento sulla destra della navbar. Purtroppo, flask-nav non gestisce nativamente gli elementi allineati a destra, ed è un po' complicato aggiungerli. Per questo motivo per il momento lasciamo questo elemento allineato sulla dinistra, e scriverò un tutorial per correggere questo problema in seguito.

Andiamo quindi a modificare il file `blog/navbar.py` come segue

```python
from . import nav
from flask_nav.elements import *

from flask_security import current_user

@nav.navigation()
def main_nav():
    navbar = Navbar('Blog')
    navbar.items.append(View('Home', 'main.index'))
    if current_user.is_authenticated:
        usergrp = []
        usergrp.append(current_user.email)
        usergrp.append(View('Logout', 'security.logout'))
        navbar.items.append(Subgroup(*usergrp))
    return navbar
```

A questo punto possiamo testare l'applicazione. Lanciamola e accediamo al solito link `http://127.0.0.1:5000`. Noteremo subito che niente è cambiato dall'ultima volta che abbiamo effettuato l'accesso. Infatti la navbar viene modificato solo se l'utente ha effettuato il login. 

Accediamo quidni all'URL `http://127.0.0.1:5000/login`. Questa è una view generata automaticamente da flask-security che permette di gestire il login. Inseriamo nome utente e password (ricordo che di default abbiamo messo `admin@admin.com` e `admin`)

![Login View](img/login.png)

E potremmo verificare che il login è stato correttamente effettuato

![Index Logged In](img/loggedin.png)

## Flask-SuperAdmin per la gestione del Database

Verificato che il database funziona, vediamo come possiamo utilizzare un'utilissima estensione, chiamata **Flask-SuperAdmin** per la creazione di pannelli di amministrazione. 

Prima di tutto, installiamo l'estensione 

```python
(blog)$ pip install flask-superadmin
```

È importante notare che Flask-SuperAdmin non è nativamente integrato con Flask-Security. Questo vuol dire che normalmente le view generate da questa estensione sono visibili a tutti, cosa che noi vogliamo certamente evitare. 

L'integrazione di Flask-SuperAdmin con Flask-Security da me trovata al momento è un po' macchinosa.

Per prima cosa, è necessario creare un nuovo file, chiamato `blog/adminviews.py` e insere il seguente codice all'interno

```python
from flask_superadmin import AdminIndexView as _AdminIndexView
from flask_superadmin.model import ModelAdmin as _ModelAdmin
from flask_security import current_user
from flask import abort

class ModelAdmin(_ModelAdmin):
    def is_accessible(self):
        return current_user.has_role('admin'):

    def _handle_view(self, name, *args, **kwargs):
        if not self.is_accessible():
            abort(403)


class AdminIndexView(_AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.has_role('admin'):
            abort(403)
        return super(AdminIndexView, self).index()
```

In questo modo estendiamo gli oggetti che gestiscono normalmente le view di Admin e gli diciamo di lasciare passare solo gli utenti che hanno il ruolo di amministratore.

Adesso possiamo configurare il modulo. Apriamo il file `blog/__init__.py` e modifichiamolo come segue

```python
#...
from flask_superadmin import Admin
#...
from .adminviews import ModelAdmin, AdminIndexView
admin=Admin(index_view=AdminIndexView())

def create_app(config_name='default'):
    #...
    admin.init_app(app)
    #...

    from .models import User, Role
    #...
    admin.register(User, admin_class=ModelAdmin, session=db.session)
    admin.register(Role, admin_class=ModelAdmin, session=db.session)
    #...
#...
```

Come ultimo aggiustamente, facciamo in modo che, se l'utente attuale è anche un amministratore, appaia la view admin nella sua navbar, modificando il file `blog/navbar.py` come segue

```python
#...
@nav.navigation()
def main_nav():
    #...
    if current_user.is_authenticated:
        #...
        if current_user.has_role('admin'):
            usergrp.append(View('Admin', 'admin.index'))
        #...
    return navbar
```


A questo punto possiamo testare l'app.
Dopo aver fatto il login, vedremo apparire un nuovo tab nel tab navbar relativa al nostro account

![Admin Tag Navbar](img/adminnav.png)

Che rimanda al link di Amministrazione da cui possiamo modificare aggiungere ed eliminare elementi del database.

![Admin View](img/adminview.png)

Si noti che se proviamo ad accedere al link o sottolink senza aver fatto correttamente il login `http://127.0.0.1:5000/admin` otterremo l'errore di accesso negato.
![Accesso Negato](img/accessonegato.png)

##GitHub parte 3
Trovate la repo aggiornata con tutto il lavoro svolto finora al [link](https://github.com/ludusrusso/ludoblog/tree/p3).

