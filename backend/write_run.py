import pathlib
pathlib.Path('run.py').write_text('''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.config import Config
from database.connection import db_manager
from api.routes import app
from api.socket_events import socketio
def main():
    db_manager.initialize()
    socketio.init_app(app, cors_allowed_origins='*', async_mode='threading')
    print('Server starting on port', Config.API_PORT)
    socketio.run(app, host='0.0.0.0', port=Config.API_PORT, debug=Config.FLASK_DEBUG, use_reloader=False, allow_unsafe_werkzeug=True)
if __name__ == '__main__':
    main()
'''.strip(), encoding='utf-8')
print('run.py created!')
