// lib/core/constants/app_strings.dart
// النصوص ثنائية اللغة: عربي / فرنسي

class AppStrings {
  final bool isArabic;
  const AppStrings({this.isArabic = true});

  // ─── عناوين عامة ────────────────────────────────────────────
  String get republic     => isArabic
      ? 'الجمهورية الجزائرية الديمقراطية الشعبية'
      : 'République Algérienne Démocratique et Populaire';

  String get electionTitle => isArabic
      ? 'الانتخابات الرئاسية 2026'
      : 'Élections Présidentielles 2026';

  String get ministryLabel => isArabic
      ? 'وزارة الداخلية والجماعات المحلية'
      : 'Ministère de l\'Intérieur et des Collectivités Locales';

  // ─── شاشة الترحيب ───────────────────────────────────────────
  String get welcomeTitle    => isArabic ? 'مرحباً بكم'         : 'Bienvenue';
  String get startVoting     => isArabic ? 'ابدأ التصويت'        : 'COMMENCER LE VOTE';
  String get secureSystem    => isArabic ? 'نظام تصويت آمن وشفاف' : 'Système de vote sécurisé et transparent';
  String get blockchainPowered => isArabic ? 'مدعوم بتقنية البلوكشين' : 'Propulsé par la blockchain';

  // ─── شاشة اللغة ─────────────────────────────────────────────
  String get chooseLanguage  => isArabic ? 'اختر اللغة'          : 'Choisissez la langue';
  String get arabic          => 'العربية';
  String get french          => 'Français';

  // ─── شاشة NFC ───────────────────────────────────────────────
  String get scanTitle       => isArabic ? 'تحقق من الهوية'      : 'Vérification d\'identité';
  String get scanInstruction => isArabic
      ? 'ضع بطاقتك الوطنية البيومترية على قارئ NFC'
      : 'Placez votre carte nationale biométrique sur le lecteur NFC';
  String get scanWaiting     => isArabic ? 'في انتظار البطاقة...' : 'En attente de la carte...';
  String get scanning        => isArabic ? 'جاري التحقق...'       : 'Vérification en cours...';
  String get scanManual      => isArabic ? 'أو أدخل الرمز يدوياً' : 'Ou saisissez le code manuellement';
  String get confirm         => isArabic ? 'تأكيد'                : 'CONFIRMER';

  // ─── شاشة التحقق ────────────────────────────────────────────
  String get verifiedTitle   => isArabic ? 'تم التحقق بنجاح'      : 'Vérification réussie';
  String get welcomeVoter    => isArabic ? 'أهلاً وسهلاً'          : 'Bienvenue';
  String get voterEligible   => isArabic
      ? 'أنت مؤهل للتصويت في هذه الانتخابات'
      : 'Vous êtes éligible à voter dans ces élections';
  String get proceedToVote   => isArabic ? 'المتابعة للتصويت'      : 'PROCÉDER AU VOTE';

  // ─── شاشة المرشحين ──────────────────────────────────────────
  String get candidatesTitle => isArabic ? 'اختر مرشحك'           : 'Choisissez votre candidat';
  String get candidatesHint  => isArabic
      ? 'المس بطاقة المرشح لاختياره، ثم اضغط تأكيد'
      : 'Touchez la carte du candidat pour le sélectionner, puis confirmez';
  String get selectedBadge   => isArabic ? 'محدد'                  : 'Sélectionné';
  String get noSelection     => isArabic ? 'لم تختر بعد'           : 'Aucun choix effectué';

  // ─── شاشة التأكيد ───────────────────────────────────────────
  String get confirmTitle    => isArabic ? 'تأكيد اختيارك'         : 'Confirmer votre choix';
  String get confirmWarning  => isArabic
      ? 'هذا الإجراء لا يمكن التراجع عنه.\nهل أنت متأكد من اختيارك؟'
      : 'Cette action est irréversible.\nÊtes-vous sûr de votre choix?';
  String get confirmBtn      => isArabic ? 'نعم، أؤكد صوتي'        : 'Oui, je confirme';
  String get cancelBtn       => isArabic ? 'إلغاء'                  : 'Annuler';
  String get yourChoice      => isArabic ? 'اختيارك:'               : 'Votre choix:';

  // ─── شاشة المعالجة ──────────────────────────────────────────
  String get processingTitle => isArabic ? 'جاري تسجيل صوتك'       : 'Enregistrement de votre vote';
  String get processingStep1 => isArabic ? 'تشفير الصوت بـ RSA-4096' : 'Chiffrement RSA-4096';
  String get processingStep2 => isArabic ? 'إضافة كتلة للبلوكشين'  : 'Ajout au bloc blockchain';
  String get processingStep3 => isArabic ? 'التحقق من سلامة السلسلة' : 'Vérification de la chaîne';
  String get processingStep4 => isArabic ? 'توليد إيصال التصويت'    : 'Génération du reçu';

  // ─── شاشة النجاح ────────────────────────────────────────────
  String get successTitle    => isArabic ? 'تم تسجيل صوتك!'         : 'Vote enregistré!';
  String get successSubtitle => isArabic
      ? 'شكراً لمشاركتك في العملية الديمقراطية'
      : 'Merci pour votre participation au processus démocratique';
  String get receiptTitle    => isArabic ? 'إيصال التصويت'           : 'Reçu de vote';
  String get receiptHint     => isArabic
      ? 'احتفظ بهذا الرمز للتحقق من صحة صوتك لاحقاً'
      : 'Conservez ce code pour vérifier votre vote ultérieurement';
  String get finishBtn       => isArabic ? 'إنهاء'                   : 'TERMINER';
  String get voteHashLabel   => isArabic ? 'رمز التحقق:'             : 'Code de vérification:';

  // ─── شاشات الخطأ ────────────────────────────────────────────
  String get alreadyVotedTitle => isArabic ? 'تم التصويت مسبقاً'    : 'Déjà voté';
  String get alreadyVotedMsg   => isArabic
      ? 'سجّلت صوتك بالفعل في هذه الانتخابات.\nلا يمكن التصويت مرتين.'
      : 'Vous avez déjà voté dans ces élections.\nIl est impossible de voter deux fois.';
  String get invalidCardTitle  => isArabic ? 'بطاقة غير مسجلة'      : 'Carte non enregistrée';
  String get invalidCardMsg    => isArabic
      ? 'هذه البطاقة غير مسجلة في منظومة التصويت.\nيرجى التواصل مع موظف مكتب التصويت.'
      : 'Cette carte n\'est pas enregistrée dans le système.\nVeuillez contacter un agent du bureau de vote.';
  String get backToStart       => isArabic ? 'العودة للبداية'         : 'Retour au début';
  String get retryBtn          => isArabic ? 'إعادة المحاولة'         : 'Réessayer';
  String get callAgent         => isArabic ? 'استدعاء موظف'           : 'Appeler un agent';

  // ─── مشترك ──────────────────────────────────────────────────
  String get secureConnection  => isArabic ? '🔒 اتصال آمن'          : '🔒 Connexion sécurisée';
  String get step              => isArabic ? 'الخطوة'                 : 'Étape';
  String get of                => isArabic ? 'من'                     : 'de';
  String get loading           => isArabic ? 'جاري التحميل...'        : 'Chargement...';
  String get connectionError   => isArabic
      ? 'خطأ في الاتصال — يرجى التواصل مع الموظف'
      : 'Erreur de connexion — contactez un agent';
}
