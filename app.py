from flask import Flask, render_template, Response, jsonify
from quiz_camera import QuizCamera

app    = Flask(__name__)
camera = QuizCamera()


def generate_frames():
    while True:
        try:
            frame = camera.get_frame()
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception:
            continue


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def status():
    try:
        return jsonify(camera.get_status())
    except Exception:
        return jsonify({'done': False, 'question': '', 'q_num': 0,
                        'total': 0, 'score': 0, 'feedback': '',
                        'fb_color': 'green', 'remaining': 0})


@app.route('/restart')
def restart():
    global camera
    try:
        camera.release()
    except Exception:
        pass
    camera = QuizCamera()
    return jsonify({'success': True})


if __name__ == "__main__":
    app.run(debug=True)