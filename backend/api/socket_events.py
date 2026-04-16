"""
backend/api/socket_events.py
Socket.IO Events — تحديثات حية للوحة المراقبين

يُرسل حدث "new_vote" للـ dashboard فور تسجيل كل صوت.
يتكامل مع routes.py عبر emit() من داخل cast_vote endpoint.
"""

from datetime import datetime
from flask_socketio import SocketIO, emit

# Instance وحيدة يستخدمها التطبيق
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="eventlet",
    logger=False,
    engineio_logger=False,
)


def emit_new_vote(blockchain_length: int, timestamp: datetime) -> None:
    """
    إرسال حدث تصويت جديد لجميع الـ clients المتصلين.

    Args:
        blockchain_length : الطول الحالي للسلسلة بعد إضافة الكتلة
        timestamp         : وقت التصويت
    """
    try:
        socketio.emit(
            "new_vote",
            {
                "blockchain_length": blockchain_length,
                "timestamp":         timestamp.isoformat() + "Z",
            },
            namespace="/",
        )
    except Exception as exc:
        print(f"⚠️  Socket emit failed: {exc}")


# ─── معالجات الأحداث الواردة ────────────────────────────────────

@socketio.on("connect")
def on_connect():
    print(f"🔌 Dashboard client connected")
    emit("connected", {"status": "ok", "message": "متصل بالخادم"})


@socketio.on("disconnect")
def on_disconnect():
    print(f"🔌 Dashboard client disconnected")


@socketio.on("ping_server")
def on_ping():
    """يُستخدم للتحقق من حيوية الاتصال (keepalive)."""
    emit("pong_server", {"timestamp": datetime.utcnow().isoformat()})
