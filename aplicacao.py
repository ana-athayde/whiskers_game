import os
import io
import json
import base64

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Where's Whiskers?",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Tamanho lógico do quadro (as coordenadas dos itens usam essa escala)
BOARD_WIDTH = 1120

# Fator aplicado ao tamanho recortado do PNG para o tamanho inicial no quadro
DEFAULT_SCALE = {
    "furniture": 0.7,
    "object": 0.5,
    "character": 0.45,
}

ROOM_LABELS = {
    "bedroom": "🛏️ Bedroom",
    "living_room": "🛋️ Living Room",
    "kitchen": "🍳 Kitchen",
    "bathroom": "🛁 Bathroom",
    "garden": "🌳 Garden",
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def pretty(name):
    return name.replace("_", " ").title()


def encode_image(path, max_size, quality=85):
    """
    Abre o PNG, recorta as bordas transparentes, reduz para
    no máximo `max_size` px e devolve (data_url, largura, altura)
    do recorte em tamanho original.
    """
    image = Image.open(path).convert("RGBA")

    bbox = image.getchannel("A").getbbox()
    if bbox:
        image = image.crop(bbox)

    width, height = image.size

    preview = image.copy()
    preview.thumbnail((max_size, max_size), Image.LANCZOS)

    buffer = io.BytesIO()
    preview.save(buffer, format="WEBP", quality=quality)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/webp;base64,{encoded}", width, height


def list_pngs(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(
        file_name for file_name in os.listdir(folder)
        if file_name.lower().endswith(".png")
    )


@st.cache_data(show_spinner="Loading maps...")
def load_game_data(assets_dir):
    """
    Cada subpasta de assets/ com um background.png vira um mapa.
    Dentro dela, furniture/ e objects/ viram os itens disponíveis.
    """
    assets = {}
    rooms = []

    def add_asset(key, path, name, kind):
        src, width, height = encode_image(path, max_size=420)
        scale = DEFAULT_SCALE[kind]
        assets[key] = {
            "name": pretty(name),
            "kind": kind,
            "src": src,
            "ratio": height / width,
            "width": round(width * scale),
        }

    character_path = os.path.join(assets_dir, "characters", "whiskers.png")
    if os.path.exists(character_path):
        add_asset("characters/whiskers", character_path, "whiskers", "character")

    for room in sorted(os.listdir(assets_dir)):
        background_path = os.path.join(assets_dir, room, "background.png")
        if not os.path.exists(background_path):
            continue

        background_src, bg_width, bg_height = encode_image(
            background_path, max_size=1600
        )

        palette = []
        for kind, folder in (("furniture", "furniture"), ("object", "objects")):
            for file_name in list_pngs(os.path.join(assets_dir, room, folder)):
                name = os.path.splitext(file_name)[0]
                key = f"{room}/{folder}/{name}"
                add_asset(key, os.path.join(assets_dir, room, folder, file_name), name, kind)
                palette.append(key)

        rooms.append({
            "id": room,
            "label": ROOM_LABELS.get(room, pretty(room)),
            "background": background_src,
            "ratio": bg_height / bg_width,
            "palette": palette,
        })

    return {"rooms": rooms, "assets": assets, "boardWidth": BOARD_WIDTH}


def render_board(game_data, height):
    template_path = os.path.join(BASE_DIR, "frontend", "html", "board.html")
    css_path = os.path.join(BASE_DIR, "frontend", "css", "board.css")
    js_path = os.path.join(BASE_DIR, "frontend", "js", "board.js")
    with open(template_path, encoding="utf-8") as file:
        template = file.read()
    with open(css_path, encoding="utf-8") as file:
        css = file.read()
    with open(js_path, encoding="utf-8") as file:
        js = file.read()

    payload = json.dumps(game_data).replace("</", "<\\/")
    html = (
        template
        .replace("/*__CSS__*/", css)
        .replace("/*__JS__*/", js)
        .replace("__GAME_DATA__", payload)
    )

    # st.iframe substitui components.html a partir do Streamlit 1.5x
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height, scrolling=False)


# ============================================================
# ESTILIZAÇÃO
# ============================================================

st.markdown("""
<style>
    .main-title {
        text-align: center;
        margin: 0 0 4px 0;
    }

    .subtitle {
        text-align: center;
        opacity: 0.7;
        margin-bottom: 12px;
    }

    .vocab-card {
        background-color: #fffbe6;
        border: 1px solid #ffe58f;
        color: #2c2c2c;
        padding: 12px 15px;
        border-radius: 10px;
        font-size: 15px;
    }

    .vocab-card h3 {
        margin-top: 0;
        color: #2c2c2c;
    }

    .vocab-card ul {
        padding-left: 20px;
        line-height: 1.8;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR - VOCABULÁRIO E RESPOSTA DO ALUNO
# ============================================================

with st.sidebar:

    st.markdown("""
    <div class='vocab-card'>
        <h3>Place Prepositions</h3>
        <ul>
            <li><b>on</b> (em cima de)</li>
            <li><b>under</b> (embaixo de)</li>
            <li><b>in</b> (dentro de)</li>
            <li><b>next to</b> (ao lado de)</li>
            <li><b>between</b> (entre)</li>
            <li><b>behind</b> (atrás de)</li>
            <li><b>in front of</b> (na frente de)</li>
            <li><b>near</b> (perto de)</li>
            <li><b>above</b> (acima de)</li>
            <li><b>below</b> (abaixo de)</li>
            <li><b>inside</b> (dentro)</li>
            <li><b>outside</b> (fora)</li>
            <li><b>beside</b> (ao lado de)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("🎙️ Student's Answer")

    audio_file = st.audio_input("Where's Whiskers? Record your answer:")

    if audio_file:
        st.audio(audio_file)
        st.success("Audio recorded successfully!")


# ============================================================
# QUADRO INTERATIVO
# ============================================================

st.markdown(
    "<h1 class='main-title'>🐱 Where's Whiskers?</h1>"
    "<div class='subtitle'>Pick a map, arrange the furniture and objects, "
    "hide Whiskers and describe where the cat is.</div>",
    unsafe_allow_html=True
)

game_data = load_game_data(ASSETS_DIR)

if not game_data["rooms"]:
    st.error("No maps found. Add a folder with a background.png inside assets/.")
else:
    render_board(game_data, height=780)
