import io
import zipfile
import streamlit as st
import pymupdf

# Configuración de la página
st.set_page_config(
    page_title="Compresor de PDF | AppLogic Solutions", 
    page_icon="⚡", 
    layout="centered"
)

# Estilos CSS personalizados para mantener la interfaz profesional y atractiva
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 750px;
        margin: 0 auto;
    }
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 35px 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .hero-container h1 {
        font-size: 2.2rem;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .hero-container p {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 0;
    }
    .company-badge {
        display: inline-block;
        background: #38bdf8;
        color: #0f172a;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .footer {
        text-align: center;
        margin-top: 40px;
        color: #64748b;
        font-size: 0.9rem;
        border-top: 1px solid #e2e8f0;
        padding-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado visual de AppLogic Solutions
st.markdown("""
    <div class="hero-container">
        <div class="company-badge">AppLogic Solutions</div>
        <h1>Compresor de PDF Inteligente</h1>
        <p>Optimiza el peso de tus documentos al instante conservando la mejor calidad visual.</p>
    </div>
""", unsafe_allow_html=True)

# Inicializar memoria de sesión
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}

# Contenedor de subida de archivos
uploaded_files = st.file_uploader("📂 Selecciona o arrastra tus archivos PDF aquí", type="pdf", accept_multiple_files=True)

# Selector de nivel con las opciones exactas solicitadas
nivel = st.selectbox(
    "⚙️ Selecciona el Nivel de Compresión",
    options=["bajo", "medio", "maximo"],
    format_func=lambda x: {
        "bajo": "Bajo (Mejor Calidad Visual / Minima Reducción del Peso)", 
        "medio": "Medio (Recomendado / Peso Equilibrado)", 
        "maximo": "Maximo (Menor Calidad Visual / Menor Peso)"
    }[x],
    index=1
)

st.write("")

if uploaded_files:
    if st.button("🚀 Comprimir Archivos Ahora", type="primary", use_container_width=True):
        configuraciones = {
            "bajo": {"dpi": 150, "quality": 80},
            "medio": {"dpi": 120, "quality": 60},
            "maximo": {"dpi": 90, "quality": 30}
        }
        params = configuraciones[nivel]
        
        st.session_state.processed_files = {}
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            with st.spinner(f"Procesando: {uploaded_file.name}..."):
                bytes_data = uploaded_file.read()
                
                doc_orig = pymupdf.open(stream=bytes_data, filetype="pdf")
                doc_nuevo = pymupdf.open()
                
                for pagina in doc_orig:
                    pix = pagina.get_pixmap(dpi=params["dpi"])
                    img_bytes = pix.tobytes("jpeg", jpg_quality=params["quality"])
                    
                    nueva_pagina = doc_nuevo.new_page(width=pagina.rect.width, height=pagina.rect.height)
                    nueva_pagina.insert_image(nueva_pagina.rect, stream=img_bytes)
                    
                output_bytes = doc_nuevo.tobytes()
                doc_orig.close()
                doc_nuevo.close()
                
                # Formato de nombre dinámico: Optimizado-{nivel}-{nombre_original}.pdf
                nombre_salida = f"Optimizado-{nivel}-{uploaded_file.name}"
                st.session_state.processed_files[nombre_salida] = output_bytes
                
                progress_bar.progress((i + 1) / total_files)
                
        st.success("¡Todos los archivos han sido optimizados con éxito!")

# Sección de resultados y descargas
if st.session_state.processed_files:
    st.markdown("---")
    st.subheader("📦 Resultados Listos para Descargar")
    
    # Botón global para descargar todo en un archivo ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, data in st.session_state.processed_files.items():
            zip_file.writestr(filename, data)
    zip_buffer.seek(0)
    
    st.download_button(
        label="📥 Descargar Todos los Archivos (.ZIP)",
        data=zip_buffer,
        file_name="pdfs_optimizados_applogic.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True
    )
    
    st.write("")
    
    # Menú desplegable para descargas individuales uno a uno
    with st.expander("📂 Ver y descargar archivos de forma individual", expanded=True):
        for filename, data in st.session_state.processed_files.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(filename)
            with col2:
                st.download_button(
                    label="⬇️ Descargar",
                    data=data,
                    file_name=filename,
                    mime="application/pdf",
                    key=filename,
                    use_container_width=True
                )

# Pie de página corporativo
st.markdown("""
    <div class="footer">
        Desarrollado con pasión por <b>AppLogic Solutions</b> 🚀 | Todos los derechos reservados.
    </div>
""", unsafe_allow_html=True)
