import os

from flask import Flask, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.context_processor
def inject_cache_buster():
    def versioned_static(filename):
        file_path = os.path.join(app.static_folder, filename)
        try:
            version = int(os.path.getmtime(file_path))
        except OSError:
            version = 0
        return f"{url_for('static', filename=filename)}?v={version}"

    return dict(versioned_static=versioned_static)


# 1. Asosiy (Sirtqi) Vazifa Modeli
class MainTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtasks = db.relationship('SubTask', backref='main_task', lazy=True, cascade="all, delete-orphan")


# 2. Ichki (Mayda) Vazifa Modeli
class SubTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    main_task_id = db.Column(db.Integer, db.ForeignKey('main_task.id'), nullable=False)


# Bazani yaratish va barcha boshlang'ich ma'lumotlarni qo'shish
with app.app_context():
    db.create_all()

    if not MainTask.query.first():
        # 1. Maktab (Barcha fanlar)
        maktab = MainTask(title="Maktab")
        sub_m1 = SubTask(title="Algebra", main_task=maktab)
        sub_m2 = SubTask(title="Geometriya", main_task=maktab)
        sub_m3 = SubTask(title="Fizika", main_task=maktab)
        sub_m4 = SubTask(title="Kimyo", main_task=maktab)
        sub_m5 = SubTask(title="Biologiya", main_task=maktab)
        sub_m6 = SubTask(title="Tarix", main_task=maktab)
        sub_m7 = SubTask(title="O'zbek tili", main_task=maktab)

        # 2. Uy ishi (Maktab, Ingliz tili, IT)
        uy_ishi = MainTask(title="Uy ishi")
        sub_u1 = SubTask(title="Maktab: Matematika misollarini yechish", main_task=uy_ishi)
        sub_u2 = SubTask(title="Ingliz tili: 20 ta yangi so'z yodlash", main_task=uy_ishi)
        sub_u3 = SubTask(title="Ingliz tili: Grammar mashqlarini bajarish", main_task=uy_ishi)
        sub_u4 = SubTask(title="IT: Python Flask loyihasini yakunlash", main_task=uy_ishi)
        sub_u5 = SubTask(title="IT: JavaScript loyiha ustida ishlash", main_task=uy_ishi)

        # 3. Telefon (Telegram, Instagram, YouTube)
        telefon = MainTask(title="Telefon")
        sub_t1 = SubTask(title="Telegram: Muhim xabarlarga javob berish", main_task=telefon)
        sub_t2 = SubTask(title="Instagram: Yangi post tayyorlash", main_task=telefon)
        sub_t3 = SubTask(title="YouTube: Dasturlash darslarini ko'rish", main_task=telefon)

        # 4. Kitob (Kitob nomlari)
        kitob = MainTask(title="Kitoblar")
        sub_k1 = SubTask(title="Atom Odatlari (James Clear)", main_task=kitob)
        sub_k2 = SubTask(title="Sariq devni minib (Xudoyberdi To'xtaboyev)", main_task=kitob)
        sub_k3 = SubTask(title="Boy ota, kambag'al ota (Robert Kiyosaki)", main_task=kitob)
        sub_k4 = SubTask(title="Diqqat (Cal Newport)", main_task=kitob)

        db.session.add_all([
            maktab, uy_ishi, telefon, kitob,
            sub_m1, sub_m2, sub_m3, sub_m4, sub_m5, sub_m6, sub_m7,
            sub_u1, sub_u2, sub_u3, sub_u4, sub_u5,
            sub_t1, sub_t2, sub_t3,
            sub_k1, sub_k2, sub_k3, sub_k4
        ])
        db.session.commit()


@app.route('/')
def index():
    main_tasks = MainTask.query.all()
    return render_template('index.html', main_tasks=main_tasks)


@app.route('/api/main-task/add', methods=['POST'])
def add_main_task():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Title required'}), 400

    new_main = MainTask(title=title)
    db.session.add(new_main)
    db.session.commit()
    return jsonify({'id': new_main.id, 'title': new_main.title})


@app.route('/api/main-task/<int:main_id>/subtasks', methods=['GET'])
def get_subtasks(main_id):
    main_task = MainTask.query.get_or_404(main_id)
    subtasks = [{'id': sub.id, 'title': sub.title, 'is_done': sub.is_done} for sub in main_task.subtasks]
    return jsonify({'main_id': main_task.id, 'main_title': main_task.title, 'subtasks': subtasks})


@app.route('/api/subtask/add', methods=['POST'])
def add_subtask():
    data = request.get_json(silent=True) or {}
    main_id = data.get('main_task_id')
    title = (data.get('title') or '').strip()

    if not main_id or not title:
        return jsonify({'error': 'Main task va Title kiritilishi shart'}), 400

    sub = SubTask(title=title, main_task_id=main_id)
    db.session.add(sub)
    db.session.commit()
    return jsonify({'id': sub.id, 'title': sub.title, 'is_done': sub.is_done, 'main_task_id': sub.main_task_id})


@app.route('/api/subtask/toggle/<int:sub_id>', methods=['POST'])
def toggle_subtask(sub_id):
    sub = SubTask.query.get_or_404(sub_id)
    sub.is_done = not sub.is_done
    db.session.commit()
    return jsonify({'id': sub.id, 'title': sub.title, 'is_done': sub.is_done})


if __name__ == '__main__':
    app.run(debug=True)
