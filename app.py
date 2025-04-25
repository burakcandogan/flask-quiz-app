from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)#flask uygulaması oluştur
app.secret_key = 'secret_key'#session için gizli anahtarı

# Veritabanı konfigürasyonu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# kullanıcı modeli, sınav sonunda göstermek için last ve high skor tutuor
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    high_score = db.Column(db.Integer, default=0)
    last_score = db.Column(db.Integer, default=0)

# soru modeli soru, şıklar ve doru cevapları tutuyor
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_exam', methods=['POST'])#sınava başla butonuna tıklandığında bu çalışcak
def start():
    username = request.form.get('username')#form üzerinden kullanıcı adı al
    if not username:#kullanıcı adı boş mu kontrol et
        return redirect(url_for('index'))

    user = User.query.filter_by(username=username).first()#kullanıcı adı db'de var mı kontrol et
    if not user:#yoksa yenisini oluştur
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    session['username'] = username#girinlen kullanıcı her türlü db'de var artık kullanıcı adı bilgisini al ve tarayıcıda tutmak için sakla
    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():#soruları db'den çek ve quiz ekranını bastır
    username = session.get('username')#en yüksek skorları sayfada göstermek için bilgileri al
    user = User.query.filter_by(username=username).first()
    highest_score = db.session.query(db.func.max(User.high_score)).scalar()
    questions = Question.query.all()
    return render_template('quiz.html', questions=questions,user=user, highest_score=highest_score)#quiz.html'de kullanabilmek için çekilen soruları gönder

@app.route('/submit', methods=['POST'])
def submit():
    username = session.get('username')#giriş yaparken kaydedilen kullanıcı adını al
    if not username:
        return redirect(url_for('index'))#kullanıcı adı kontrolü

    user = User.query.filter_by(username=username).first()#kullanıcının bütün bilgilerini al ki db'de max skor ve güncel skoru güncelleyebil
    questions = Question.query.all()#bastırılan soruları db'den al
    score = 0

    for q in questions:
        current_question = request.form.get(f'question_{q.id}')#formdaki soruyu al ve kontrol edeceğin soru olarak değişkene ata
        if current_question and current_question == q.correct_answer:#soru varsa ve doğru cevap ile eşleşiyorsa skoru arttır
            score += 20

    #skor güncelleme lojiği
    user.last_score = score
    if score > user.high_score:
        user.high_score = score
    db.session.commit()#db'e kaydet
    return redirect(url_for('result'))

@app.route('/result')#son skoru önceki sayfada kaydettiğimiz için artık db'den bütün verileri alabiliriz
def result():
    username = session.get('username')#kullanıcının bilgilerini çekmek için oturumdan kullanıcı adını iste
    user = User.query.filter_by(username=username).first()#bilgileri al
    highest_score = db.session.query(db.func.max(User.high_score)).scalar()
    return render_template('result.html', user=user, highest_score=highest_score)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
