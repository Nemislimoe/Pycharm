from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db      = SQLAlchemy(app)
migrate = Migrate(app, db)


# ════════════════════════════════════════════════════════
#  МОДЕЛІ
# ════════════════════════════════════════════════════════

# Many-to-many: Gamer <-> Game  (асоціативна таблиця)
gamer_game = db.Table(
    'gamer_game',
    db.Column('gamer_id', db.Integer, db.ForeignKey('gamer.id'), primary_key=True),
    db.Column('game_id',  db.Integer, db.ForeignKey('game.id'),  primary_key=True),
)


class GameDeveloper(db.Model):
    """Розробник гри."""
    __tablename__ = 'game_developer'

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(120), nullable=False)
    founded = db.Column(db.Integer)
    # ── Міграція 2: додано колонку country ──
    country = db.Column(db.String(80))

    # One-to-many → Game
    games = db.relationship('Game', back_populates='developer', lazy='select')

    def __repr__(self):
        return f'<GameDeveloper {self.name}>'


class Game(db.Model):
    """Гра."""
    __tablename__ = 'game'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    release_year = db.Column(db.Integer)
    # ── Міграція 3: додано колонку genre ──
    genre        = db.Column(db.String(80))

    # ForeignKey для One-to-many
    developer_id = db.Column(db.Integer, db.ForeignKey('game_developer.id'))
    developer    = db.relationship('GameDeveloper', back_populates='games')

    # Many-to-many → Gamer
    gamers = db.relationship('Gamer', secondary=gamer_game, back_populates='games', lazy='select')

    def __repr__(self):
        return f'<Game {self.title}>'


class Gamer(db.Model):
    """Гравець."""
    __tablename__ = 'gamer'

    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email    = db.Column(db.String(120))

    # Many-to-many → Game
    games = db.relationship('Game', secondary=gamer_game, back_populates='gamers', lazy='select')

    # One-to-one → Profile
    profile = db.relationship('Profile', back_populates='gamer', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Gamer {self.username}>'


class Profile(db.Model):
    """Профіль гравця (One-to-one з Gamer)."""
    __tablename__ = 'profile'

    id         = db.Column(db.Integer, primary_key=True)
    level      = db.Column(db.Integer, default=1)
    total_hours= db.Column(db.Integer, default=0)
    bio        = db.Column(db.String(300))

    # One-to-one: унікальний FK
    gamer_id   = db.Column(db.Integer, db.ForeignKey('gamer.id'), unique=True, nullable=False)
    gamer      = db.relationship('Gamer', back_populates='profile')

    def __repr__(self):
        return f'<Profile gamer_id={self.gamer_id} level={self.level}>'


# ════════════════════════════════════════════════════════
#  МАРШРУТ: заповнення тестовими даними  GET /seed
# ════════════════════════════════════════════════════════
@app.route('/seed')
def seed():
    # Очистити перед заповненням
    db.session.execute(gamer_game.delete())
    Profile.query.delete()
    Gamer.query.delete()
    Game.query.delete()
    GameDeveloper.query.delete()
    db.session.commit()

    # ── Розробники ──
    cd_projekt = GameDeveloper(name='CD Projekt Red', founded=1994, country='Poland')
    valve      = GameDeveloper(name='Valve Corporation', founded=1996, country='USA')
    naughty    = GameDeveloper(name='Naughty Dog',      founded=1984, country='USA')

    db.session.add_all([cd_projekt, valve, naughty])
    db.session.flush()   # отримуємо id перед commit

    # ── Ігри ──
    witcher3   = Game(title='The Witcher 3',       release_year=2015, genre='RPG',     developer=cd_projekt)
    cyberpunk  = Game(title='Cyberpunk 2077',      release_year=2020, genre='RPG',     developer=cd_projekt)
    cs2        = Game(title='Counter-Strike 2',    release_year=2023, genre='Shooter', developer=valve)
    dota2      = Game(title='Dota 2',              release_year=2013, genre='MOBA',    developer=valve)
    tlou2      = Game(title='The Last of Us Part II', release_year=2020, genre='Action', developer=naughty)

    db.session.add_all([witcher3, cyberpunk, cs2, dota2, tlou2])
    db.session.flush()

    # ── Гравці ──
    alice = Gamer(username='alice42',   email='alice@example.com')
    bob   = Gamer(username='bob_pro',   email='bob@example.com')
    carol = Gamer(username='carol_gg',  email='carol@example.com')

    db.session.add_all([alice, bob, carol])
    db.session.flush()

    # ── Профілі (One-to-one) ──
    db.session.add_all([
        Profile(gamer=alice, level=42, total_hours=1200, bio='Фанатка RPG та детективів'),
        Profile(gamer=bob,   level=88, total_hours=5400, bio='Про-гравець CS та Dota'),
        Profile(gamer=carol, level=15, total_hours=320,  bio='Люблю сюжетні одиночні ігри'),
    ])

    # ── Many-to-many: гравці грають у ігри ──
    alice.games = [witcher3, cyberpunk, tlou2]
    bob.games   = [cs2, dota2, witcher3]
    carol.games = [tlou2, cyberpunk]

    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'База даних заповнена тестовими даними!'})


# ════════════════════════════════════════════════════════
#  МАРШРУТ: читання даних  GET /data
# ════════════════════════════════════════════════════════
@app.route('/data')
def data():
    # 1. Розробники та їхні ігри
    developers_data = []
    for dev in GameDeveloper.query.all():
        developers_data.append({
            'id':      dev.id,
            'name':    dev.name,
            'country': dev.country,
            'founded': dev.founded,
            'games':   [
                {'id': g.id, 'title': g.title, 'year': g.release_year, 'genre': g.genre}
                for g in dev.games
            ],
        })

    # 2. Ігри та гравці
    games_data = []
    for game in Game.query.all():
        games_data.append({
            'id':        game.id,
            'title':     game.title,
            'genre':     game.genre,
            'developer': game.developer.name if game.developer else None,
            'gamers':    [
                {'id': gr.id, 'username': gr.username}
                for gr in game.gamers
            ],
        })

    # 3. Гравці та їхні профілі
    gamers_data = []
    for gamer in Gamer.query.all():
        profile = gamer.profile
        gamers_data.append({
            'id':       gamer.id,
            'username': gamer.username,
            'email':    gamer.email,
            'games':    [g.title for g in gamer.games],
            'profile':  {
                'level':       profile.level,
                'total_hours': profile.total_hours,
                'bio':         profile.bio,
            } if profile else None,
        })

    return jsonify({
        'developers': developers_data,
        'games':      games_data,
        'gamers':     gamers_data,
    })


# ════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True)