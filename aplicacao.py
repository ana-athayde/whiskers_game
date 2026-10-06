
import os
import io
import base64
import copy

import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Whiskers Exploration Game",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def image_to_data_url(image_path):
    """
    Converte uma imagem local para Data URL.
    Isso permite que o Fabric.js carregue a imagem
    como um objeto dentro do canvas.
    """
    with open(image_path, "rb") as file:
        image_bytes = file.read()

    encoded = base64.b64encode(image_bytes).decode("utf-8")

    extension = os.path.splitext(image_path)[1].lower()

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    mime_type = mime_types.get(extension, "image/png")

    return f"data:{mime_type};base64,{encoded}"


def create_image_object(image_path, asset_name, asset_type):
    """
    Cria um objeto de imagem compatível com o JSON do Fabric.js.
    """

    image = Image.open(image_path).convert("RGBA")

    original_width, original_height = image.size

    # Tamanho máximo inicial do objeto no canvas
    max_size = 160

    scale = min(
        max_size / original_width,
        max_size / original_height,
        1.0
    )

    return {
        "type": "image",
        "version": "7.0.0",

        "originX": "left",
        "originY": "top",

        # Posição inicial
        "left": 270,
        "top": 160,

        # Escala inicial
        "scaleX": scale,
        "scaleY": scale,

        "angle": 0,

        "flipX": False,
        "flipY": False,

        "opacity": 1,

        "visible": True,

        "backgroundColor": "",

        "fill": "rgb(0,0,0)",

        "stroke": None,
        "strokeWidth": 1,

        "selectable": True,
        "evented": True,

        "asset_name": asset_name,
        "asset_type": asset_type,

        "src": image_to_data_url(image_path),

        "crossOrigin": "anonymous",

        "width": original_width,
        "height": original_height,

        "cropX": 0,
        "cropY": 0,

        "shadow": None,
        "filters": [],
    }


def empty_canvas():
    """
    Estado inicial vazio do canvas.
    """
    return {
        "version": "7.0.0",
        "objects": []
    }


# ============================================================
# SESSION STATE
# ============================================================

if "canvas_drawing" not in st.session_state:
    st.session_state.canvas_drawing = empty_canvas()

if "current_room" not in st.session_state:
    st.session_state.current_room = None


# ============================================================
# ESTILIZAÇÃO
# ============================================================

st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 15px;
    }

    .vocab-card {
        background-color: #fffbe6;
        border: 1px solid #ffe58f;
        padding: 15px;
        border-radius: 10px;
        font-size: 15px;
    }

    .vocab-card ul {
        padding-left: 20px;
        line-height: 1.8;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    "<h1 class='main-title'>🐱 Whiskers Exploration - Prepositions Game</h1>",
    unsafe_allow_html=True
)


# ============================================================
# LAYOUT
# ============================================================

col_left, col_center, col_right = st.columns([1, 2.5, 1.3])


# ============================================================
# COLUNA ESQUERDA - VOCABULÁRIO
# ============================================================

with col_left:

    st.markdown("""
    <div class='vocab-card'>
        <h3>Place Prepositions</h3>

        <ul>
            <li><b>on</b> (em cima de)</li>
            <li><b>under</b> (embaixo de)</li>
            <li><b>in</b> (dentro de)</li>
            <li><b>next to</b> (ao lado de)</li>
            <li><b>between</b> (entre)</li>

            <br>

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


# ============================================================
# DIRETÓRIO BASE
# ============================================================

base_dir = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# COLUNA DIREITA
# ============================================================

with col_right:

    # --------------------------------------------------------
    # SELEÇÃO DE AMBIENTE
    # --------------------------------------------------------

    st.subheader("🏠 Select Environment")

    selected_room = st.selectbox(
        "Choose a room:",
        ["bedroom", "living_room"],
        format_func=lambda x:
            "🛏️ Bedroom"
            if x == "bedroom"
            else "🛋️ Living Room"
    )


    # --------------------------------------------------------
    # DETECTA MUDANÇA DE AMBIENTE
    # --------------------------------------------------------

    if st.session_state.current_room != selected_room:

        st.session_state.current_room = selected_room

        # Começa o novo ambiente vazio
        st.session_state.canvas_drawing = empty_canvas()


    st.markdown("---")


    # --------------------------------------------------------
    # ASSETS DA SALA
    # --------------------------------------------------------

    furniture_dir = os.path.join(
        base_dir,
        selected_room,
        "furniture"
    )

    objects_dir = os.path.join(
        base_dir,
        selected_room,
        "objects"
    )

    character_path = os.path.join(
        base_dir,
        "characters",
        "whiskers.png"
    )


    # --------------------------------------------------------
    # PERSONAGEM
    # --------------------------------------------------------

    st.subheader("🐱 Character")

    if os.path.exists(character_path):

        character_col1, character_col2 = st.columns([1, 1])

        with character_col1:
            st.image(
                character_path,
                width=80
            )

        with character_col2:

            if st.button(
                "➕ Add Whiskers",
                key=f"add_character_{selected_room}"
            ):

                new_object = create_image_object(
                    character_path,
                    "whiskers",
                    "character"
                )

                st.session_state.canvas_drawing["objects"].append(
                    new_object
                )

                st.rerun()


    # --------------------------------------------------------
    # MÓVEIS
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("🛋️ Furniture")

    if os.path.exists(furniture_dir):

        furniture_files = sorted([
            file_name
            for file_name in os.listdir(furniture_dir)
            if file_name.lower().endswith(".png")
        ])

        for file_name in furniture_files:

            asset_path = os.path.join(
                furniture_dir,
                file_name
            )

            asset_name = os.path.splitext(
                file_name
            )[0]

            label = asset_name.replace(
                "_",
                " "
            ).title()

            asset_col1, asset_col2 = st.columns([1, 1])

            with asset_col1:

                st.image(
                    asset_path,
                    width=70
                )

            with asset_col2:

                if st.button(
                    f"➕ {label}",
                    key=f"add_furniture_{selected_room}_{asset_name}"
                ):

                    new_object = create_image_object(
                        asset_path,
                        asset_name,
                        "furniture"
                    )

                    st.session_state.canvas_drawing["objects"].append(
                        new_object
                    )

                    st.rerun()


    # --------------------------------------------------------
    # OBJETOS
    # --------------------------------------------------------

    st.markdown("---")
    st.subheader("🧸 Objects")

    if os.path.exists(objects_dir):

        object_files = sorted([
            file_name
            for file_name in os.listdir(objects_dir)
            if file_name.lower().endswith(".png")
        ])

        for file_name in object_files:

            asset_path = os.path.join(
                objects_dir,
                file_name
            )

            asset_name = os.path.splitext(
                file_name
            )[0]

            label = asset_name.replace(
                "_",
                " "
            ).title()

            asset_col1, asset_col2 = st.columns([1, 1])

            with asset_col1:

                st.image(
                    asset_path,
                    width=70
                )

            with asset_col2:

                if st.button(
                    f"➕ {label}",
                    key=f"add_object_{selected_room}_{asset_name}"
                ):

                    new_object = create_image_object(
                        asset_path,
                        asset_name,
                        "object"
                    )

                    st.session_state.canvas_drawing["objects"].append(
                        new_object
                    )

                    st.rerun()


    # --------------------------------------------------------
    # CONTROLES
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑️ Clear Scene",
        key=f"clear_scene_{selected_room}"
    ):

        st.session_state.canvas_drawing = empty_canvas()

        st.rerun()


    # --------------------------------------------------------
    # ÁUDIO
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader("🎙️ Student's Answer")

    audio_file = st.audio_input(
        "Record your explanation:"
    )

    if audio_file:
        st.success("Audio recorded successfully!")


# ============================================================
# BACKGROUND
# ============================================================

bg_path = os.path.join(
    base_dir,
    selected_room,
    "background.png"
)


if os.path.exists(bg_path):

    bg_image = Image.open(bg_path)

else:

    bg_image = Image.new(
        "RGB",
        (700, 450),
        color=(245, 245, 245)
    )


# ============================================================
# CANVAS
# ============================================================

with col_center:

    st.subheader(
        f"📍 Current Location: "
        f"{selected_room.replace('_', ' ').title()}"
    )

    st.info(
        "💡 Add a furniture or object using the buttons on the right. "
        "Then use the canvas editing tool to move, resize or rotate it."
    )


    canvas_result = st_canvas(

        fill_color="rgba(255, 165, 0, 0.3)",

        stroke_width=3,

        stroke_color="#000000",

        background_image=bg_image,

        update_streamlit=True,

        height=450,

        width=700,

        # IMPORTANTE:
        # "transform" NÃO existe mais como drawing_mode.
        # O modo de edição é controlado pela toolbar.
        drawing_mode="freedraw",

        initial_drawing=st.session_state.canvas_drawing,

        display_toolbar=True,

        return_image_data=False,

        key=f"canvas_{selected_room}",

    )


    # --------------------------------------------------------
    # SALVA ALTERAÇÕES FEITAS NO CANVAS
    # --------------------------------------------------------

    if canvas_result.json_data is not None:

        st.session_state.canvas_drawing = copy.deepcopy(
            canvas_result.json_data
        )


    # --------------------------------------------------------
    # INFORMAÇÕES DOS OBJETOS
    # --------------------------------------------------------

    objects = st.session_state.canvas_drawing.get(
        "objects",
        []
    )

    if objects:

        st.markdown("---")

        st.write(
            f"### 📦 Objects in scene: {len(objects)}"
        )

        for index, obj in enumerate(objects):

            asset_name = obj.get(
                "asset_name",
                "Unknown"
            )

            asset_type = obj.get(
                "asset_type",
                "object"
            )

            st.caption(
                f"{index + 1}. "
                f"{asset_name.replace('_', ' ').title()} "
                f"({asset_type})"
            )
