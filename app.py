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


class MainTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtasks = db.relationship('SubTask', backref='main_task', lazy=True, cascade="all, delete-orphan")

    def is_all_completed(self):
        if not self.subtasks:
            return False
        return all(sub.is_done for sub in self.subtasks)


class SubTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    main_task_id = db.Column(db.Integer, db.ForeignKey('main_task.id'), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    main_tasks = MainTask.query.all()
    tasks_data = []
    for task in main_tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'is_completed': task.is_all_completed()
        })
    return render_template('index.html', main_tasks=tasks_data)


@app.route('/api/main-task/add', methods=['POST'])
def add_main_task():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Title required'}), 400

    new_main = MainTask(title=title)
    db.session.add(new_main)
    db.session.commit()
    return jsonify({'id': new_main.id, 'title': new_main.title, 'is_completed': False})


@app.route('/api/main-task/delete/<int:main_id>', methods=['DELETE'])
def delete_main_task(main_id):
    main_task = MainTask.query.get_or_404(main_id)
    db.session.delete(main_task)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/main-task/<int:main_id>/subtasks', methods=['GET'])
def get_subtasks(main_id):
    main_task = MainTask.query.get_or_404(main_id)
    subtasks = [{'id': sub.id, 'title': sub.title, 'is_done': sub.is_done} for sub in main_task.subtasks]
    return jsonify({
        'main_id': main_task.id,
        'main_title': main_task.title,
        'subtasks': subtasks,
        'is_completed': main_task.is_all_completed()
    })


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

    main_task = MainTask.query.get(main_id)
    return jsonify({
        'id': sub.id,
        'title': sub.title,
        'is_done': sub.is_done,
        'main_task_id': sub.main_task_id,
        'main_is_completed': main_task.is_all_completed()
    })


@app.route('/api/subtask/toggle/<int:sub_id>', methods=['POST'])
def toggle_subtask(sub_id):
    sub = SubTask.query.get_or_404(sub_id)
    sub.is_done = not sub.is_done
    db.session.commit()

    main_task = MainTask.query.get(sub.main_task_id)
    return jsonify({
        'id': sub.id,
        'title': sub.title,
        'is_done': sub.is_done,
        'main_task_id': sub.main_task_id,
        'main_is_completed': main_task.is_all_completed()
    })


@app.route('/api/subtask/delete/<int:sub_id>', methods=['DELETE'])
def delete_subtask(sub_id):
    sub = SubTask.query.get_or_404(sub_id)
    main_id = sub.main_task_id
    db.session.delete(sub)
    db.session.commit()

    main_task = MainTask.query.get(main_id)
    return jsonify({
        'success': True,
        'main_task_id': main_id,
        'main_is_completed': main_task.is_all_completed() if main_task else False
    })


if __name__ == '__main__':
    app.run(debug=True)