from flask import Flask, render_template, request, redirect
import socket
import json
from datetime import datetime
import threading
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message_text = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        
        send_to_socket_server({"username": username, "message": message_text, "timestamp": timestamp})

        return redirect('/')
    return render_template('message.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html'), 404


def send_to_socket_server(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server_address = ('localhost', 5000)
        message = json.dumps(data).encode('utf-8')
        sock.sendto(message, server_address)


def run_flask_app():
    app.run(port=3000)


def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server_address = ('localhost', 5000)
        sock.bind(server_address)

        while True:
            data, address = sock.recvfrom(4096)
            data_dict = json.loads(data.decode('utf-8'))
            save_to_json_file(data_dict)


def save_to_json_file(data):
    storage_dir = 'storage'
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)

    file_path = os.path.join(storage_dir, 'data.json')

    with open(file_path, 'a') as file:
        json.dump({data['timestamp']: {'username': data['username'], 'message': data['message']}}, file)
        file.write('\n')

if __name__ == '__main__':
    
    flask_thread = threading.Thread(target=run_flask_app)
    socket_thread = threading.Thread(target=run_socket_server)

    flask_thread.start()
    socket_thread.start()