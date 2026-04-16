# backend/tests/conftest.py
# إعداد pytest المشترك لجميع الاختبارات

import sys
import os

# إضافة مجلد backend لمسار الاستيراد
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
