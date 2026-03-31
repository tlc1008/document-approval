import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import datetime

# ページ設定
st.set_page_config(page_title="書類承認システム", layout="centered")

st.title("📄 書類承認システム")
st.write("内容を確認し、問題なければ「承認」ボタンを押してください。")

file_path = "sample.pdf"

try:
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    
    st.download_button("📥 書類をダウンロードして確認", data=pdf_data, file_name="target_document.pdf")
    st.divider()

    # 入力フォーム
    customer_name = st.text_input("承認者のお名前を入力してください", placeholder="例：千葉 彰")
    
    if st.button("✅ この内容で承認する"):
        if customer_name:
            # 1. 日本語フォントの読み込み
            try:
                # Windows標準のMSゴシックを使用
                pdfmetrics.registerFont(TTFont('JapaneseFont', 'C:/Windows/Fonts/msgothic.ttc'))
                FONT_NAME = 'JapaneseFont'
            except:
                FONT_NAME = 'Helvetica' # 失敗時のバックアップ

            # 2. 既存のPDF読み込み
            existing_pdf = PdfReader(open(file_path, "rb"))
            output = PdfWriter()

            # 3. スタンプ（印影）の作成
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # --- 印影デザイン（データネーム印風） ---
            # 位置調整（前回の「完璧な位置」を基準に微調整）
            stamp_x = 500
            stamp_y = 180  
            
            can.setLineWidth(1.5)
            can.setStrokeColorRGB(0.8, 0, 0) # 印影の赤
            can.setFillColorRGB(0.8, 0, 0)
            
            # 円と仕切り線
            can.circle(stamp_x, stamp_y, 28, stroke=1, fill=0)
            can.line(stamp_x - 24, stamp_y + 8, stamp_x + 24, stamp_y + 8)
            can.line(stamp_x - 24, stamp_y - 8, stamp_x + 24, stamp_y - 8)
            
            # 文字の配置
            # 上段
            can.setFont(FONT_NAME, 9)
            can.drawCentredString(stamp_x, stamp_y + 13, "受領")
            
            # 中段（日付）
            can.setFont("Helvetica", 8)
            can.drawCentredString(stamp_x, stamp_y - 3, f"{datetime.date.today()}")
            
            # 下段（社名・部署名）
            can.setFont(FONT_NAME, 5)
            can.drawCentredString(stamp_x, stamp_y - 16, "株式会社デジアイズ")
            can.drawCentredString(stamp_x, stamp_y - 23, "ラベル課")

            can.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)

            # 4. 合成処理
            page = existing_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)

            # 2ページ目以降があれば追加
            for i in range(1, len(existing_pdf.pages)):
                output.add_page(existing_pdf.pages[i])

            # メモリ上にPDFを書き出し
            output_pdf_data = io.BytesIO()
            output.write(output_pdf_data)
            output_pdf_data.seek(0)

            st.success("承認が完了しました！")
            st.balloons()
            
            # ダウンロードボタン
            st.download_button(
                label="📩 承認済み書類を保存する",
                data=output_pdf_data,
                file_name=f"approved_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )

        else:
            st.warning("お名前を入力してください。")

except FileNotFoundError:
    st.error("sample.pdf が見つかりません。同じフォルダに置いてください。")
except Exception as e:
    st.error(f"エラーが発生しました: {e}")