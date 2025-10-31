# app.py
from __future__ import annotations
import io
import qrcode
import base64
from PIL import Image
import streamlit as st
from streamlit import components
from datetime import datetime

# ============================================================================
# Helfer
# ============================================================================

def build_vcard(
    full_name: str,
    title: str,
    company: str,
    phone: str,
    email: str,
    location: str,
    website: str,
) -> str:
    lines = ["BEGIN:VCARD", "VERSION:3.0"]

    if full_name:
        lines.append(f"N:{full_name};;;;")
        lines.append(f"FN:{full_name}")
    if company:
        lines.append(f"ORG:{company}")
    if title:
        lines.append(f"TITLE:{title}")
    if phone:
        lines.append(f"TEL;TYPE=CELL:{phone}")
    if email:
        lines.append(f"EMAIL;TYPE=WORK:{email}")
    if location:
        # ADR;TYPE=WORK:;;Street;City;Region;Zip;Country
        lines.append(f"ADR;TYPE=WORK:;;{location};;;;")
    if website:
        lines.append(f"URL:{website}")

    lines.append("END:VCARD")
    return "\n".join(lines)


def make_qr_image(data: str, box_size: int = 8) -> Image.Image:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img.convert("RGB")


def img_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def bytes_to_data_url_png(b: bytes) -> str:
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:image/png;base64,{b64}"


def inject_base_css():
    st.markdown(
        """
        <style>
            body {
                background-color:#0f172a;
            }
            .main .block-container {
                padding-top:2rem;
                padding-bottom:2rem;
                max-width:900px;
            }
            .download-hint {
                font-size:.7rem;
                color:#6b7280;
                line-height:1.4;
                margin-top:.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# Page Setup
# ============================================================================

st.set_page_config(
    page_title="Digitale Visitenkarte Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_base_css()

# ============================================================================
# Sidebar Eingabeparameter
# ============================================================================

with st.sidebar:
    st.markdown("## Kontakt Daten")
    st.caption("Felder ausfüllen. QR und Downloads generieren.")

    full_name = st.text_input("Name / Full Name", value="Christoph Schantl")
    title = st.text_input("Titel / Role", value="Investment Management / Advisory")
    company = st.text_input("Firma / Company", value="SHI Capital")
    phone = st.text_input("Telefon", value="+34 600 000 000")
    email = st.text_input("E-Mail", value="christoph@example.com")
    location = st.text_input("Ort / Location", value="Palma de Mallorca, Spain")
    website = st.text_input("Website / Link", value="https://shi-capital.example")
    linkedin = st.text_input("LinkedIn URL", value="https://www.linkedin.com/in/christophschantl")

    st.markdown("---")
    qr_mode = st.radio(
        "QR Inhalt",
        ["vCard (Kontakt speichern)", "Website/Link"],
        index=0,
        help="vCard erzeugt direkten Kontakt-Import ins Handy. Website nur Link.",
    )

    st.markdown("---")
    st.caption("Branding Farben (HEX)")
    color_card = st.text_input("Card Background HEX", value="#1e293b")
    color_accent = st.text_input("Accent HEX", value="#16a34a")
    color_text_main = "#f8fafc"
    color_text_sub = "#cbd5e1"

# ============================================================================
# Daten generieren
# ============================================================================

# vCard Text
vcard_str = build_vcard(
    full_name=full_name.strip(),
    title=title.strip(),
    company=company.strip(),
    phone=phone.strip(),
    email=email.strip(),
    location=location.strip(),
    website=website.strip(),
)

# QR Payload
if qr_mode == "vCard (Kontakt speichern)":
    qr_payload = vcard_str
else:
    qr_payload = website.strip() or linkedin.strip() or " "

# QR Bild
qr_img = make_qr_image(qr_payload, box_size=8)
qr_png_bytes = img_to_png_bytes(qr_img)
qr_data_url = bytes_to_data_url_png(qr_png_bytes)

# vCard Bytes
vcard_bytes = vcard_str.encode("utf-8")

# Filenamen
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
vcf_filename = f"{full_name.strip().replace(' ', '_')}_{timestamp_str}.vcf"
qr_filename = f"qr_{timestamp_str}.png"

# ============================================================================
# HTML Karte bauen (als echtes HTML via components.html)
# ============================================================================

card_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
.card {{
  background:{color_card};
  border-radius:1rem;
  padding:1.5rem;
  box-shadow:0 30px 80px rgba(0,0,0,.6);
  border:1px solid rgba(255,255,255,.07);
  color:{color_text_main};
  font-family:-apple-system,BlinkMacSystemFont,"Inter",Roboto,"Helvetica Neue",sans-serif;
  display:flex;
  flex-wrap:wrap;
  gap:1.5rem;
}}
.leftcol {{
  flex:1 1 250px;
  min-width:250px;
}}
.rightcol {{
  flex:0 0 200px;
  min-width:200px;
  text-align:center;
}}
.name {{
  color:{color_text_main};
  font-size:1.4rem;
  font-weight:700;
  line-height:1.2;
  margin:0;
}}
.title-line {{
  color:{color_accent};
  font-size:.9rem;
  font-weight:500;
  margin:.15rem 0 .6rem 0;
}}
.block {{
  margin-bottom:.9rem;
}}
.label {{
  color:{color_text_sub};
  font-size:.7rem;
  text-transform:uppercase;
  letter-spacing:.05em;
  font-weight:500;
  margin-bottom:.2rem;
}}
.val {{
  color:{color_text_main};
  font-size:.9rem;
  font-weight:500;
  line-height:1.3;
  word-break:break-word;
}}
.divider {{
  border-bottom:1px solid rgba(255,255,255,.07);
  margin:1rem 0 1rem 0;
}}
.footer-note {{
  color:{color_text_sub};
  font-size:.7rem;
  line-height:1.4;
  margin-top:1rem;
}}
.qr-label {{
  color:{color_text_sub};
  font-size:.7rem;
  font-weight:500;
  margin-top:.5rem;
  text-align:center;
}}
a.card-link {{
  color:{color_text_main};
  text-decoration:none;
  word-break:break-all;
}}
a.card-link:hover {{
  color:{color_accent};
}}
.qr-box {{
  background:#fff;
  border-radius:.5rem;
  padding:.5rem;
  line-height:0;
  border:1px solid rgba(0,0,0,.1);
  box-shadow:0 20px 40px rgba(0,0,0,.4);
  display:inline-block;
}}
.qr-box img {{
  display:block;
  width:160px;
  height:160px;
  object-fit:contain;
}}
</style>
</head>
<body style="margin:0;background:transparent;">
<div class="card">

  <div class="leftcol">
    <p class="name">{full_name}</p>
    <p class="title-line">{title}<br>{company}</p>

    <div class="block">
      <div class="label">Phone</div>
      <div class="val">{phone}</div>
    </div>

    <div class="block">
      <div class="label">Email</div>
      <div class="val">{email}</div>
    </div>

    <div class="block">
      <div class="label">Location</div>
      <div class="val">{location}</div>
    </div>

    <div class="block">
      <div class="label">Web</div>
      <div class="val"><a class="card-link" href="{website}" target="_blank" rel="noopener noreferrer">{website}</a></div>
    </div>

    <div class="block">
      <div class="label">LinkedIn</div>
      <div class="val"><a class="card-link" href="{linkedin}" target="_blank" rel="noopener noreferrer">{linkedin}</a></div>
    </div>

    <div class="divider"></div>

    <div class="footer-note">
      Digitale Visitenkarte<br>
      QR scannen oder .vcf importieren
    </div>
  </div>

  <div class="rightcol">
    <div class="label" style="text-align:center;">QR Code</div>
    <div class="qr-box">
      <img src="{qr_data_url}" alt="QR Code">
    </div>
    <div class="qr-label">{qr_mode}</div>
  </div>

</div>
</body>
</html>
"""

# ============================================================================
# Layout in Streamlit
# ============================================================================

left_col, right_col = st.columns([2, 1], gap="large")

with left_col:
    # echtes HTML rendern
    components.v1.html(card_html, height=360, scrolling=False)

with right_col:
    st.subheader("Export")

    st.write("1. Kontakt (.vcf) speichern")
    st.download_button(
        label="Download Kontakt (.vcf)",
        data=vcard_bytes,
        file_name=vcf_filename,
        mime="text/vcard",
        use_container_width=True,
    )

    st.write("2. QR Code speichern")
    st.download_button(
        label="Download QR (.png)",
        data=qr_png_bytes,
        file_name=qr_filename,
        mime="image/png",
        use_container_width=True,
    )

    st.markdown(
        """
        <div class="download-hint">
        .vcf auf dem Handy öffnen. iOS / Android fragt dann ob neuer Kontakt angelegt werden soll.<br><br>
        QR.png ist druckfähig / sharefähig.
        </div>
        """,
        unsafe_allow_html=True,
    )
