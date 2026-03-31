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
st.write("納品内容をご確認のうえ、受領ボタンを押してください。")

file_path = "sample.pdf"

# --- 日本語フォント設定（最も互換性の高い平成明朝を使用） ---
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
    else:
        st.error("sample.pdf が見つかりません。GitHubにアップロードされているか確認してください。")
    
    st.divider()

    # 2. 受領者入力
    recipient_name = st.text_input("受領者名を入力してください", placeholder="氏名を入力")
    
    if st.button("🔴 受領ボタン（受領印を押す）"):
        if recipient_name and recipient_name != "氏名を入力":
            existing_pdf = PdfReader(open(file_path, "rb"))
            output = PdfWriter()

            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # --- 印影デザイン（大きく、はっきりと） ---
            # 位置調整：x=525, y=175 付近（受領印枠の中心）
            stamp_x = 525  
            stamp_y = 175  
            
            # 赤い色を指定
            can.setStrokeColorRGB(0.8, 0, 0)
            can.setFillColorRGB(0.8, 0, 0)
            can.setLineWidth(2)
            
            # 円を描く（半径32）
            can.circle(stamp_x, stamp_y, 32, stroke=1, fill=0)
            # 中の仕切り線
            can.line(stamp_x - 28, stamp_y + 10, stamp_x + 28, stamp_y + 10)
            can.line(stamp_x - 28, stamp_y - 10, stamp_x + 28, stamp_y - 10)
            
            # 上段：受領（日本語）
            can.setFont(FONT_NAME, 11)
            can.drawCentredString(stamp_x, stamp_y + 16, "受領")
            
            # 中段：日付（英数字は標準フォントで確実に出す）
            can.setFont("Helvetica-Bold", 10)
            can.drawCentredString(stamp_x, stamp_y - 2, f"{datetime.date.today()}")
            
            # 下段：社名・部署名（日本語）
            can.setFont(FONT_NAME, 6)
            can.drawCentredString(stamp_x, stamp_y - 18, "株式会社デジアイズ")
            can.drawCentredString(stamp_x, stamp_y - 25, "ラベル課")

            can.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)

            # 1ページ目にスタンプを合成
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            # 2ページ目以降を維持
            for i in range(1, len(existing_pdf.pages)):
                output.add_page(existing_pdf.pages[i])

            output_pdf_data = io.BytesIO()
            output.write(output_pdf_data)
            output_pdf_data.seek(0)

            # 3. 完了通知
            st.success("受領印の合成に成功しました！")
            
            st.download_button(
                label="📩 受領印書類をダウンロード",
                data=output_pdf_data,
                file_name=f"received_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )

        else:
            st.warning("受領者名を入力してください。")

except Exception as e:
    st.error(f"エラーが発生しました。")
    st.info("GitHubのリポジトリに sample.pdf が正しい名前で存在するか確認してください。")