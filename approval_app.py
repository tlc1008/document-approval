import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import datetime
import base64

# ページ設定
st.set_page_config(page_title="物品受領システム", layout="centered")

st.title("📦 物品受領依頼")
st.write("納品内容をご確認のうえ、受領印を押してください。")

file_path = "sample.pdf"

def display_pdf(file_path):
    """PDFを画面上にプレビュー表示する関数"""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

try:
    # 1. 納品書のプレビュー表示
    st.subheader("📄 納品書プレビュー")
    display_pdf(file_path)
    st.divider()

    # 2. 入力フォーム
    recipient_name = st.text_input("受領者名を入力してください", placeholder="例：氏名")
    
    if st.button("🔴 受領ボタン（受領印を押す）"):
        if recipient_name and recipient_name != "氏名":
            # 日本語フォントの読み込み
            try:
                pdfmetrics.registerFont(TTFont('JapaneseFont', 'C:/Windows/Fonts/msgothic.ttc'))
                FONT_NAME = 'JapaneseFont'
            except:
                FONT_NAME = 'Helvetica'

            existing_pdf = PdfReader(open(file_path, "rb"))
            output = PdfWriter()

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # --- 印影デザイン（受領印を大きく・濃く調整） ---
            # 前回の完璧な位置から少し左(x)・下(y)にずらして中央を調整
            stamp_x = 475  
            stamp_y = 175  
            
            can.setLineWidth(2.5) # 線を太く
            can.setStrokeColorRGB(0.9, 0, 0) # より鮮やかな赤
            can.setFillColorRGB(0.9, 0, 0)
            
            # 円を大きく（半径28→35）
            can.circle(stamp_x, stamp_y, 35, stroke=1, fill=0)
            can.line(stamp_x - 30, stamp_y + 10, stamp_x + 30, stamp_y + 10)
            can.line(stamp_x - 30, stamp_y - 10, stamp_x + 30, stamp_y - 10)
            
            # 文字（サイズを大きく、太字に）
            can.setFont(FONT_NAME, 11)
            can.drawCentredString(stamp_x, stamp_y + 18, "受領")
            
            can.setFont("Helvetica-Bold", 10)
            can.drawCentredString(stamp_x, stamp_y - 2, f"{datetime.date.today()}")
            
            can.setFont(FONT_NAME, 6)
            can.drawCentredString(stamp_x, stamp_y - 19, "株式会社デジアイズ")
            can.drawCentredString(stamp_x, stamp_y - 28, "ラベル課")

            can.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)

            # 合成処理
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            for i in range(1, len(existing_pdf.pages)):
                output.add_page(existing_pdf.pages[i])

            output_pdf_data = io.BytesIO()
            output.write(output_pdf_data)
            output_pdf_data.seek(0)

            # 3. 成功時のポップアップ表示
            st.success("受領しました。") # 一時的なメッセージとして表示
            
            # ダウンロードボタンの名称変更
            st.download_button(
                label="📩 受領印書類をダウンロード",
                data=output_pdf_data,
                file_name=f"received_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )

        else:
            st.warning("受領者名を入力してください。")

except FileNotFoundError:
    st.error("納品書ファイル(sample.pdf)が見つかりません。")
except Exception as e:
    st.error(f"システムエラー: {e}")