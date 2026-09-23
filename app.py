import os

from flask import Flask, render_template, request, redirect, url_for, jsonify
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


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='qilinmagan')


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    qilinganlar = Todo.query.filter_by(status='qilingan').all()
    qilinmaganlar = Todo.query.filter_by(status='qilinmagan').all()
    return render_template('index.html', qilinganlar=qilinganlar, qilinmaganlar=qilinmaganlar)


@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    if title and title.strip():
        new_todo = Todo(title=title.strip(), status='qilinmagan')
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/toggle/<int:todo_id>')
def toggle(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.status == 'qilinmagan':
        todo.status = 'qilingan'
    else:
        todo.status = 'qilinmagan'
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/api/add', methods=['POST'])
def api_add():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'title required'}), 400
    todo = Todo(title=title, status='qilinmagan')
    db.session.add(todo)
    db.session.commit()
    return jsonify({'id': todo.id, 'title': todo.title, 'status': todo.status})


@app.route('/api/toggle/<int:todo_id>', methods=['POST'])
def api_toggle(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.status = 'qilingan' if todo.status == 'qilinmagan' else 'qilinmagan'
    db.session.commit()
    return jsonify({'id': todo.id, 'title': todo.title, 'status': todo.status})


@app.route('/api/delete/<int:todo_id>', methods=['POST'])
def api_delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
