import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.lib.colors as colors
import urllib.request

class PVGenerator:
    @staticmethod
    def _get_font_path(font_name):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        fonts_dir = os.path.join(base_dir, 'assets', 'fonts')
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)
            
        font_path = os.path.join(fonts_dir, f"{font_name}.ttf")
        if not os.path.exists(font_path):
            # Download Amiri font if not exists for Arabic support
            # Use Amiri as it supports Arabic well
            if font_name == 'Amiri-Regular':
                url = "https://github.com/alifuser/amiri/raw/master/fonts/ttf/amiri-regular.ttf"
            elif font_name == 'Amiri-Bold':
                url = "https://github.com/alifuser/amiri/raw/master/fonts/ttf/amiri-bold.ttf"
            else:
                return None
            try:
                urllib.request.urlretrieve(url, font_path)
            except Exception as e:
                print(f"Failed to download font {font_name}: {e}")
                return None
                
        return font_path

    @staticmethod
    def generate_pv(election_data, stats, output_path):
        import arabic_reshaper
        from bidi.algorithm import get_display
        
        # Setup fonts
        reg_font_path = PVGenerator._get_font_path('Amiri-Regular')
        bold_font_path = PVGenerator._get_font_path('Amiri-Bold')
        
        has_arabic_font = False
        if reg_font_path and bold_font_path and os.path.exists(reg_font_path) and os.path.exists(bold_font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arabic-Regular', reg_font_path))
                pdfmetrics.registerFont(TTFont('Arabic-Bold', bold_font_path))
                has_arabic_font = True
            except:
                pass
                
        def format_ar(text):
            if not text: return ""
            if has_arabic_font:
                try:
                    reshaped = arabic_reshaper.reshape(str(text))
                    return get_display(reshaped)
                except:
                    return str(text)
            return str(text)

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        font_reg = 'Arabic-Regular' if has_arabic_font else 'Helvetica'
        font_bold = 'Arabic-Bold' if has_arabic_font else 'Helvetica-Bold'
        
        # Colors
        dz_green = colors.HexColor('#006233')
        dz_red = colors.HexColor('#D21034')
        dark_grey = colors.HexColor('#333333')

        # Header
        c.setFont(font_bold, 16)
        c.setFillColor(dz_green)
        c.drawCentredString(width / 2.0, height - 50, format_ar("الجمهورية الجزائرية الديمقراطية الشعبية"))
        
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2.0, height - 70, "Republique Algerienne Democratique et Populaire")
        
        c.setFont(font_bold, 14)
        c.setFillColor(dark_grey)
        c.drawCentredString(width / 2.0, height - 100, format_ar("السلطة الوطنية المستقلة للانتخابات (ANIE)"))
        
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width / 2.0, height - 120, "Autorite Nationale Independante des Elections")
        
        # Line
        c.setStrokeColor(dz_red)
        c.setLineWidth(2)
        c.line(50, height - 140, width - 50, height - 140)

        # Title
        c.setFont(font_bold, 18)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2.0, height - 170, format_ar("محضر إقفال الانتخابات الرسمي"))
        
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2.0, height - 190, "Proces-Verbal Officiel de Cloture des Elections")

        # Election Info
        c.setFont(font_bold, 14)
        c.drawCentredString(width / 2.0, height - 220, format_ar(election_data.get('name_ar', '')))
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2.0, height - 240, election_data.get('name_fr', ''))

        c.setFont(font_bold, 12)
        c.drawString(width - 250, height - 280, format_ar(f"تاريخ البداية: {election_data.get('start_date', '')}"))
        c.drawString(width - 250, height - 300, format_ar(f"تاريخ النهاية: {election_data.get('end_date', '')}"))
        c.drawString(width - 250, height - 320, format_ar(f"تاريخ الإقفال: {election_data.get('official_close_date', '')}"))
        
        c.drawString(50, height - 280, format_ar(f"إجمالي المسجلين: {stats.get('total_voters', 0)}"))
        c.drawString(50, height - 300, format_ar(f"المصوتين فعليا: {stats.get('total_voted', 0)}"))
        c.drawString(50, height - 320, format_ar(f"نسبة المشاركة: {stats.get('turnout_percent', 0)}%"))

        # Table Header
        y = height - 380
        c.setFillColor(dz_green)
        c.rect(50, y, width - 100, 30, fill=1)
        c.setFillColor(colors.white)
        c.setFont(font_bold, 12)
        
        c.drawString(width - 90, y + 10, format_ar("الترتيب"))
        c.drawString(width - 200, y + 10, format_ar("المرشح"))
        c.drawString(width - 350, y + 10, format_ar("الحزب"))
        c.drawString(150, y + 10, format_ar("الأصوات"))
        c.drawString(70, y + 10, format_ar("النسبة"))

        # Table Rows
        c.setFillColor(colors.black)
        y -= 30
        
        votes_list = stats.get('votes_per_candidate', [])
        # Sort descending
        votes_list.sort(key=lambda x: x['votes_count'], reverse=True)
        
        for idx, row in enumerate(votes_list):
            if y < 150:
                c.showPage()
                y = height - 50
                c.setFont(font_reg, 12)
            
            c.setFont(font_reg, 12)
            rank = format_ar(f"{idx + 1}")
            is_winner = election_data.get('final_winner_id') == row['candidate_id']
            if is_winner:
                rank += " *"
                c.setFont(font_bold, 12)
                
            c.drawString(width - 80, y + 10, rank)
            c.drawString(width - 200, y + 10, format_ar(row['name_ar']))
            party = row.get('party_ar', '') or ''
            c.drawString(width - 350, y + 10, format_ar(party[:20]))
            c.drawString(150, y + 10, str(row['votes_count']))
            c.drawString(70, y + 10, f"{row['percent']}%")
            
            # Row line
            c.setStrokeColor(colors.lightgrey)
            c.setLineWidth(1)
            c.line(50, y, width - 50, y)
            y -= 30
            c.setFillColor(colors.black)

        # Blockchain & Integrity
        y -= 40
        c.setFont(font_bold, 12)
        c.setFillColor(dz_green)
        c.drawString(width - 200, y, format_ar("التحقق التقني (Blockchain)"))
        y -= 25
        c.setFont(font_reg, 10)
        c.setFillColor(colors.black)
        c.drawString(width - 250, y, format_ar(f"الكُتل المُسجلة: {stats.get('blockchain_blocks', 0)}"))
        c.drawString(50, y, f"Blockchain Integrity: {'VERIFIED OK' if stats.get('blockchain_valid') else 'FAILED'}")
        y -= 20
        c.drawString(50, y, f"Timestamp: {datetime.utcnow().isoformat()}Z")
        
        # Signatures
        y -= 70
        c.setFont(font_bold, 12)
        c.drawString(width - 150, y, format_ar("رئيس اللجنة"))
        c.drawString(width / 2.0 - 20, y, format_ar("المقرر"))
        c.drawString(80, y, format_ar("مراقب ANIE"))
        
        # Footer
        c.setFont(font_reg, 9)
        c.setFillColor(colors.gray)
        c.drawCentredString(width / 2.0, 30, format_ar("تمّ توليد هذا المحضر آلياً بواسطة نظام التصويت الإلكتروني الجزائري"))
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2.0, 15, "Document genere automatiquement par e-Voting Algeria System")

        c.save()
        return output_path
