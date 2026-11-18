
import threading
import time
import webview

from app import app


def start_flask():
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )


if __name__ == "__main__":

    flask_thread = threading.Thread(
        target=start_flask,
        daemon=True
    )

    flask_thread.start()

    time.sleep(2)

    window = webview.create_window(
        title="MediSense AI",
        url="http://127.0.0.1:5000/",
        width=1280,
        height=800,
        min_size=(900, 600),
        resizable=True
    )

    webview.start()

