"""
backend/core/exceptions.py
Custom Exceptions — استثناءات مخصصة ثنائية اللغة
"""


class VotingSystemError(Exception):
    """الاستثناء الأساسي لجميع أخطاء النظام."""

    def __init__(self, message_ar: str, message_fr: str, status_code: int = 400):
        self.message_ar  = message_ar
        self.message_fr  = message_fr
        self.status_code = status_code
        super().__init__(f"{message_ar} / {message_fr}")


class VoterNotFoundError(VotingSystemError):
    def __init__(self):
        super().__init__(
            "بطاقة غير مسجلة",
            "Carte non enregistrée",
            404,
        )


class AlreadyVotedError(VotingSystemError):
    def __init__(self):
        super().__init__(
            "تم التصويت مسبقاً",
            "Déjà voté",
            403,
        )


class InvalidCandidateError(VotingSystemError):
    def __init__(self):
        super().__init__(
            "مرشح غير صالح",
            "Candidat invalide",
            400,
        )


class VotingClosedError(VotingSystemError):
    def __init__(self):
        super().__init__(
            "باب التصويت مغلق",
            "Le scrutin est fermé",
            423,
        )


class BlockchainIntegrityError(VotingSystemError):
    def __init__(self, details: str = ""):
        super().__init__(
            f"خلل في سلامة البلوكشين: {details}",
            f"Erreur d'intégrité blockchain: {details}",
            500,
        )


class DecryptionError(VotingSystemError):
    def __init__(self):
        super().__init__(
            "فشل فك التشفير — كلمة مرور خاطئة أو بيانات تالفة",
            "Échec du déchiffrement — mot de passe incorrect ou données corrompues",
            400,
        )


class AuthenticationError(VotingSystemError):
    def __init__(self):
        super().__init__(
            "غير مصرح — يرجى تسجيل الدخول",
            "Non autorisé — veuillez vous connecter",
            401,
        )


class SessionExpiredError(VotingSystemError):
    def __init__(self):
        super().__init__(
            "انتهت صلاحية الجلسة — يرجى تسجيل الدخول مجدداً",
            "Session expirée — veuillez vous reconnecter",
            401,
        )
