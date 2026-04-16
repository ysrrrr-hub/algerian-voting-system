content = (
    "import sys\n"
    "import os\n"
    "\n"
    "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
    "\n"
    "from core.config import Config\n"
    "from database.connection import db_manager\n"
    "from api.routes import app\n"
    "from api.socket_events import socketio\n"
    "\n"
    "\n"
    "def main():\n"
    "    db_manager.initialize()\n"
    "    socketio.init_app(app, cors_allowed_origins='*', async_mode='threading')\n"
    "    print('Server starting on port', Config.API_PORT)\n"
    "    socketio.run(app, host='0.0.0.0', port=Config.API_PORT, debug=Config.FLASK_DEBUG, use_reloader=False, allow_unsafe_werkzeug=True)\n"
    "\n"
    "\n"
    "if __name__ == '__main__':\n"
    "    main()\n"
)

with open('run.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('run.py created successfully!')