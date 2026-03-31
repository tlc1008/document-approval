import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
import datetime
import os

# --- ページ基本設定 ---
st.set_page_config(page_title="物品受領承認依頼", layout="centered")

st.title("📦 物品受領承認依頼")
st.write("内容を確認し、受領日と受領者名を入力して受領ボタンを押してください。")

file_path = "sample.pdf"

# 日本語フォント設定
FONT_NAME = 'HeiseiMin-W3'
pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))

try:
    # 1. 書類確認セクション
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

    # 2. 受領入力セクション
    # 【追加】カレンダー機能：初期値は当日
    selected_date = st.date_input("受領日を選択してください", datetime.date.today())
    # 西暦表示用（YYYY/MM/DD）
    receipt_date_str = selected_date.strftime("%Y/%m/%d")

    recipient_name = st.text_input("受領者名を入力してください", placeholder="氏名を入力")
    
    if st.button("🔴 受領ボタン（受領印を押す）"):
        if recipient_name and recipient_name != "氏名を入力":
            existing_pdf = PdfReader(open(file_path, "rb"))
            output = PdfWriter()

            # --- 1ページ目の合成処理 ---
            packet1 = io.BytesIO()
            can1 = canvas.Canvas(packet1, pagesize=A4)
            
            # 【A. 3カ所の日付入力】選択された日付を使用
            can1.setFont("Helvetica", 9)
            can1.drawString(500, 793, receipt_date_str) # 右上の「日付」
            can1.drawString(500, 335, receipt_date_str) # 中段の「日付」
            
            # 【B. 印影のデザインと位置】
            stamp_x = 500  
            stamp_y = 190  
            
            can1.setStrokeColorRGB(0.8, 0, 0)
            can1.setFillColorRGB(0.8, 0, 0)
            can1.setLineWidth(2)
            
            can1.circle(stamp_x, stamp_y, 32, stroke=1, fill=0)
            can1.line(stamp_x - 28, stamp_y + 11, stamp_x + 28, stamp_y + 11)
            can1.line(stamp_x - 28, stamp_y - 11, stamp_x + 28, stamp_y - 11)
            
            can1.setFont(FONT_NAME, 10)
            can1.drawCentredString(stamp_x, stamp_y + 18, "受領")
            
            can1.setFont(FONT_NAME, 8)
            can1.drawCentredString(stamp_x, stamp_y + 4, recipient_name)
            
            # 【日付】選択された日付を印影に反映
            can1.setFont("Helvetica-Bold", 9)
            can1.drawCentredString(stamp_x, stamp_y - 7, receipt_date_str)
            
            can1.setFont(FONT_NAME, 5)
            can1.drawCentredString(stamp_x, stamp_y - 18, "株式会社デジアイズ")
            can1.drawCentredString(stamp_x, stamp_y - 25, "ラベル課")
            
            can1.save()
            packet1.seek(0)
            
            page1 = existing_pdf.pages[0]
            page1.merge_page(PdfReader(packet1).pages[0])
            output.add_page(page1)

            # --- 2ページ目の合成処理 ---
            if len(existing_pdf.pages) > 1:
                packet2 = io.BytesIO()
                can2 = canvas.Canvas(packet2, pagesize=A4)
                
                # 2ページ目の日付も選択された日付に
                can2.setFont("Helvetica", 9)
                can2.drawString(500, 748, receipt_date_str) 
                
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

            st.success(f"受領処理が完了しました（受領日：{receipt_date_str}）")
            
            st.download_button(
                label="📩 受領印済み書類をダウンロード",
                data=output_pdf_data,
                file_name=f"received_{receipt_date_str.replace('/','-')}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("受領者名を入力してください。")

except Exception as e:
    st.error(f"システムエラーが発生しました。")