import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont # CIDフォントを使用
import io
import datetime
import os

# ページ設定
st.set_page_config(page_title="物品受領承認依頼", layout="centered")

st.title("📦 物品受領承認依頼")
st.write("納品内容をご確認のうえ、受領ボタンを押してください。")

file_path = "sample.pdf"

# --- 日本語フォントの設定（CIDフォント：ダウンロード不要で最も安定） ---
try:
    font_name = 'HeiseiMin-W3' # 平成明朝
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))
except:
    font_name = 'Helvetica'

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
    else:
        st.error("納品書ファイル(sample.pdf)が見つかりません。")
    
    st.divider()

    # 2. 受領入力セクション
    recipient_name = st.text_input("受領者名を入力してください", placeholder="氏名を入力")
    
    if st.button("🔴 受領ボタン（受領印を押す）"):
        if recipient_name and recipient_name != "氏名を入力":
            existing_pdf = PdfReader(open(file_path, "rb"))
            output = PdfWriter()

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # --- 印影デザイン ---
            stamp_x = 525  # 座標を右寄りに再調整
            stamp_y = 175  
            
            can.setLineWidth(2)
            can.setStrokeColorRGB(0.8, 0, 0)
            can.setFillColorRGB(0.8, 0, 0)
            
            # 円（半径30：大きすぎず小さすぎず）
            can.circle(stamp_x, stamp_y, 30, stroke=1, fill=0)
            can.line(stamp_x - 26, stamp_y + 8, stamp_x + 26, stamp_y + 8)
            can.line(stamp_x - 26, stamp_y - 8, stamp_x + 26, stamp_y - 8)
            
            # 文字（日本語フォント適用）
            can.setFont(font_name, 11)
            can.drawCentredString(stamp_x, stamp_y + 15, "受領")
            
            can.setFont("Helvetica-Bold", 10)
            can.drawCentredString(stamp_x, stamp_y - 2, f"{datetime.date.today()}")
            
            can.setFont(font_name, 6)
            can.drawCentredString(stamp_x, stamp_y - 17, "株式会社デジアイズ")
            can.drawCentredString(stamp_x, stamp_y - 24, "ラベル課")

            can.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)

            # 1ページ目に合成
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            # 2ページ目以降を追加
            for i in range(1, len(existing_pdf.pages)):
                output.add_page(existing_pdf.pages[i])

            output_pdf_data = io.BytesIO()
            output.write(output_pdf_data)
            output_pdf_data.seek(0)

            # 3. 完了通知とダウンロード
            st.success("受領印の合成が完了しました。")
            
            st.download_button(
                label="📩 受領印済み書類をダウンロード",
                data=output_pdf_data,
                file_name=f"received_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )

        else:
            st.warning("受領者名を入力してください。")

except Exception as e:
    st.error("エラーが発生しました。リポジトリに sample.pdf があるか確認してください。")