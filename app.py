from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)

# --- CONFIGURATION POUR LE DÉPLOIEMENT ---
# On récupère le chemin absolu du dossier où se trouve app.py
basedir = os.path.abspath(os.path.dirname(__file__))

# On définit le chemin de la base de données
# Sur Render, il faut utiliser un chemin absolu pour SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'agri.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODÈLE DE BASE DE DONNÉES ---
class Parcelle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    localisation = db.Column(db.String(100))
    nom_culture = db.Column(db.String(100))
    rendement = db.Column(db.Float)

# Cette partie crée la base de données automatiquement au démarrage si elle n'existe pas
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    parcelles = Parcelle.query.all()
    return render_template('dashboard.html', parcelles=parcelles)

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        loc = request.form.get('localisation')
        cul = request.form.get('nom_culture')
        ren = request.form.get('rendement')
        
        # Conversion sécurisée en float
        try:
            val_rendement = float(ren)
        except (ValueError, TypeError):
            val_rendement = 0.0
            
        new_p = Parcelle(localisation=loc, nom_culture=cul, rendement=val_rendement)
        db.session.add(new_p)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('ajouter_parcelle.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/analyse')
def analyse():
    # On récupère : nom, nombre de parcelles, moyenne de rendement
    stats = db.session.query(
        Parcelle.nom_culture,
        func.count(Parcelle.id).label('nombre'),
        func.avg(Parcelle.rendement).label('moyenne')
    ).group_by(Parcelle.nom_culture).all()

    return render_template('analyse.html', stats=stats)

# NOTE : Le bloc "if __name__ == '__main__':" a été retiré.
# C'est Gunicorn qui gère le lancement sur Render avec la commande : gunicorn app:app
