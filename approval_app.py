import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
import datetime
import os

# ページ設定
st.set_page_config(page_title="物品受領承認依頼", layout="centered")

st.title("📦 物品受領承認依頼")
st.write("内容を確認し、受領者名を入力して受領ボタンを押してください。")

file_path = "sample.pdf"

# 日本語フォント設定
FONT_NAME = 'HeiseiMin-W3'
pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))

try:
    # 1. 書類確認
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

    # 2. 受領者入力
    recipient_name = st.text_input("受領者名を入力してください", placeholder="氏名を入力")
    
    if st.button("🔴 受領ボタン（受領印を押す）"):
        if recipient_name and recipient_name != "氏名を入力":
            existing_pdf = PdfReader(open(file_path, "rb"))
            output = PdfWriter()

            # 今日のお日付 (西暦表示)
            today_str = datetime.date.today().strftime("%Y/%m/%d")

            # --- 1ページ目の合成処理 ---
            packet1 = io.BytesIO()
            can1 = canvas.Canvas(packet1, pagesize=A4)
            
            # A. 3カ所の日付入力 (座標はアップロードされたPDFを元に推測)
            can1.setFont("Helvetica", 10)
            can1.drawString(450, 728, today_str) # 1カ所目: 右上付近 
            can1.drawString(450, 485, today_str) # 2カ所目: 中段右付近 
            
            # B. 受領印の設定 (さらに左へ移動: 525 -> 475)
            stamp_x = 475  
            stamp_y = 175  
            
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
            
            # 1ページ目に合成
            page1 = existing_pdf.pages[0]
            page1.merge_page(PdfReader(packet1).pages[0])
            output.add_page(page1)

            # --- 2ページ目の合成処理 ---
            if len(existing_pdf.pages) > 1:
                packet2 = io.BytesIO()
                can2 = canvas.Canvas(packet2, pagesize=A4)
                
                # 3カ所目の日付 (2ページ目)
                can2.setFont("Helvetica", 10)
                can2.drawString(480, 685, today_str) # 2ページ目の日付欄 
                
                can2.save()
                packet2.seek(0)
                
                page2 = existing_pdf.pages[1]
                page2.merge_page(PdfReader(packet2).pages[0])
                output.add_page(page2)

            # 残りのページがあれば追加
            for i in range(2, len(existing_pdf.pages)):
                output.add_page(existing_pdf.pages[i])

            output_pdf_data = io.BytesIO()
            output.write(output_pdf_data)
            output_pdf_data.seek(0)

            st.success(f"受領処理が完了しました（日付: {today_str}）")
            
            st.download_button(
                label="📩 受領印書類をダウンロード",
                data=output_pdf_data,
                file_name=f"received_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("受領者名を入力してください。")

except Exception as e:
    st.error("エラーが発生しました。ファイル名を確認してください。")