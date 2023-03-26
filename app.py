import flask
from datetime import datetime, date
import json
import os
import uuid

app = flask.Flask(__name__)

def load_events():
    try:
        with open('events.json', 'r') as f:
            events = json.load(f)
    except FileNotFoundError:
        events = []
    # Convert the date string to a datetime object
    for event in events:
        event['due_date'] = datetime.strptime(event['due_date'], '%Y-%m-%d').date()
        event['time_left'] = (event['due_date'] - datetime.now().date()).days
    return events


def save_events(events):
    with open('events.json', 'w') as f:
        json.dump(events, f, default=str)


def add_event(title, description, due_date, goal_type):
    event = {
        'id': str(uuid.uuid4()),
        'title': title,
        'description': description,
        'due_date': due_date.strftime('%Y-%m-%d') if due_date else None,
        'goal_type': goal_type,
    }
    events = load_events()
    events.append(event)
    save_events(events)



def delete_event(event_id):
    events = load_events()
    events = [event for event in events if event['id'] != event_id]
    save_events(events)


def render_template():
    events = load_events()
    short_term_tasks = []
    long_term_tasks = []
    agenda_entries = []
    for event in events:
        if 'due_date' not in event:
            agenda_entries.append(event)
        elif event['goal_type'] == 'short_term':
            short_term_tasks.append(event)
        else:
            long_term_tasks.append(event)
    sorted_short_term_tasks = sorted(short_term_tasks, key=lambda x: x['due_date'])
    sorted_long_term_tasks = sorted(long_term_tasks, key=lambda x: x['due_date'])
    sorted_tasks = sorted_short_term_tasks + sorted_long_term_tasks + agenda_entries
    return flask.render_template('index.html', tasks=sorted_tasks)


@app.route('/add_task', methods=['POST'])
def add_task():
    title = flask.request.form['title']
    description = flask.request.form['description']
    due_date_str = flask.request.form['due_date']
    if due_date_str:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    else:
        due_date = None
    goal_type = flask.request.form['goal_type']
    add_event(title, description, due_date, goal_type)
    return flask.redirect('/')




@app.route('/delete_task', methods=['POST'])
def delete_task():
    event_id = flask.request.form['event_id']
    events = load_events()
    for event in events:
        if event['id'] == event_id:
            events.remove(event)
            save_events(events)
            break
    return flask.redirect('/')




@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'POST':
        title = flask.request.form.get('title')
        description = flask.request.form.get('description')
        due_date_str = flask.request.form.get('due_date')
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            due_date = None
        add_event(title, description, due_date, None)
    return render_template()


if __name__ == '__main__':
    app.run(port=5000, debug=True)
