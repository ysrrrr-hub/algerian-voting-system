"""
backend/utils/qr_generator.py
QR Code Generator — توليد إيصالات QR للناخبين

يُحوّل vote_hash (64 حرف hex) إلى صورة PNG مشفرة بـ Base64
جاهزة للعرض مباشرةً في تطبيق Flutter.
"""

import base64
from io import BytesIO

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer


def generate_vote_qr(vote_hash: str) -> str:
    """
    توليد QR Code من hash الصوت.

    التصميم:
      - وحدات دائرية (RoundedModuleDrawer) للمظهر الاحترافي
      - خطأ تصحيح عالي (ERROR_CORRECT_H) لضمان القراءة حتى لو غُطّي 30%

    Args:
        vote_hash : SHA-256 hash (64 حرف hex)

    Returns:
        data URI بصيغة  data:image/png;base64,<base64_string>
    """
    qr = qrcode.QRCode(
        version=None,                              # تلقائي حسب الحجم
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(vote_hash)
    qr.make(fit=True)

    try:
        # مظهر احترافي بوحدات دائرية
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            fill_color="#006233",   # أخضر جزائري
            back_color="white",
        )
    except Exception:
        # fallback إذا لم تتوفر المكتبات الاختيارية
        img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def generate_receipt_text(vote_hash: str, candidate_name: str = "") -> str:
    """
    توليد نص الإيصال المطبوع للناخب.

    Returns:
        نص منسّق يحتوي: الـ hash المختصر + وقت التصويت
    """
    short_hash = vote_hash[:16].upper()
    return (
        f"╔══════════════════════════════╗\n"
        f"║   إيصال التصويت الإلكتروني  ║\n"
        f"║   Reçu de vote électronique  ║\n"
        f"╠══════════════════════════════╣\n"
        f"║  رمز التحقق:                 ║\n"
        f"║  {short_hash}...              ║\n"
        f"╚══════════════════════════════╝\n"
    )
