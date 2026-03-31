import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
import datetime
import os

st.set_page_config(page_title="物品受領承認依頼", layout="centered")

st.title("📦 物品受領承認依頼")
st.write("内容を確認し、受領者名を入力して受領ボタンを押してください。")

file_path = "sample.pdf"

# 日本語フォント設定
FONT_NAME = 'HeiseiMin-W3'
pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))

try:
    st.subheader("📄 納品書の確認")
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.download_button(
                label="📥 納品書（PDF）を開いて内容を確認する",
                data=f,
                file_name="delivery_note.pdf",
                mime="application/pdf"
            )
    
    st.divider()

    recipient_name = st.text_input("受領者名を入力してください", placeholder="氏名を入力")
    
    if st.button("🔴 受領ボタン（受領印を押す）"):
        if recipient_name and recipient_name != "氏名を入力":
            existing_pdf = PdfReader(open(file_path, "rb"))
            output = PdfWriter()
            today_str = datetime.date.today().strftime("%Y/%m/%d")

            # --- 1ページ目の合成 ---
            packet1 = io.BytesIO()
            can1 = canvas.Canvas(packet1, pagesize=A4)
            
            # 【日付位置の再修正】
            # 文字サイズを9に下げて、より正確な位置へ
            can1.setFont("Helvetica", 9)
            
            # 1. 右上の「日付」欄 (さらに右、さらに下へ)
            # 座標の重なりを回避
            can1.drawString(500, 793, today_str) 
            
            # 2. 中段の「日付」欄 (座標付近の空白へ)
            # 総重量570の下ではなく、日付の文字の真横(y=458付近)へ
            can1.drawString(500, 340, today_str) 
            
            # 【受領印の位置修正】
            # さらに左へ (465 -> 455)
            stamp_x = 500  
            stamp_y = 188  
            
            can1.setStrokeColorRGB(0.8, 0, 0)
            can1.setFillColorRGB(0.8, 0, 0)
            can1.setLineWidth(2)
            can1.circle(stamp_x, stamp_y, 32, stroke=1, fill=0)
            can1.line(stamp_x - 28, stamp_y + 10, stamp_x + 28, stamp_y + 10)
            can1.line(stamp_x - 28, stamp_y - 10, stamp_x + 28, stamp_y - 10)
            
            can1.setFont(FONT_NAME, 11)
            can1.drawCentredString(stamp_x, stamp_y + 16, "受領")
            can1.setFont("Helvetica-Bold", 10)
            can1.drawCentredString(stamp_x, stamp_y - 2, today_str)
            can1.setFont(FONT_NAME, 6)
            can1.drawCentredString(stamp_x, stamp_y - 18, "株式会社デジアイズ")
            can1.drawCentredString(stamp_x, stamp_y - 25, "ラベル課")
            
            can1.save()
            packet1.seek(0)
            
            page1 = existing_pdf.pages[0]
            page1.merge_page(PdfReader(packet1).pages[0])
            output.add_page(page1)

            # --- 2ページ目の合成 ---
            if len(existing_pdf.pages) > 1:
                packet2 = io.BytesIO()
                can2 = canvas.Canvas(packet2, pagesize=A4)
                
                # 3. 2ページ目「日付」欄 (座標付近)
                can2.setFont("Helvetica", 9)
                can2.drawString(500, 745, today_str) 
                
                can2.save()
                packet2.seek(0)
                
                page2 = existing_pdf.pages[1]
                page2.merge_page(PdfReader(packet2).pages[0])
                output.add_page(page2)

            for i in range(2, len(existing_pdf.pages)):
                output.add_page(existing_pdf.pages[i])

            output_pdf_data = io.BytesIO()
            output.write(output_pdf_data)
            output_pdf_data.seek(0)

            st.success(f"受領処理が完了しました")
            
            st.download_button(
                label="📩 受領印書類をダウンロード",
                data=output_pdf_data,
                file_name=f"received_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("受領者名を入力してください。")

except Exception as e:
    st.error("エラーが発生しました。")