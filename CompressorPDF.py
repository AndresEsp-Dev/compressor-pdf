import io
import zipfile
import streamlit as st
import pymupdf

# Configuración de la página en modo ancho (wide)
st.set_page_config(
    page_title="Compresor de PDF | AppLogic Solutions", 
    page_icon="⚡", 
    layout="wide"
)

# Estilos CSS profesionales
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .hero-container h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .hero-container p {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 0;
    }
    .company-badge {
        display: inline-block;
        background: #38bdf8;
        color: #0f172a;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .file-card {
        background: #1e293b;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #334155;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #64748b;
        font-size: 0.9rem;
        border-top: 1px solid #1e293b;
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

# Inicializar variables de estado en la sesión
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}
if "file_stats" not in st.session_state:
    st.session_state.file_stats = {}
if "uploader_counter" not in st.session_state:
    st.session_state.uploader_counter = 0

# Clave dinámica para forzar el reseteo del file_uploader
uploader_key = f"uploader_{st.session_state.uploader_counter}"

# Contenedor de subida de archivos vinculado a la clave dinámica
uploaded_files = st.file_uploader(
    "📂 Selecciona o arrastra tus archivos PDF aquí", 
    type="pdf", 
    accept_multiple_files=True,
    key=uploader_key
)

# Selector de nivel de compresión
nivel_opcion = st.selectbox(
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

# Botón de compresión
if uploaded_files:
    if st.button("🚀 Comprimir Archivos Ahora", type="primary", use_container_width=True):
        configuraciones = {
            "bajo": {"dpi": 150, "quality": 80},
            "medio": {"dpi": 120, "quality": 60},
            "maximo": {"dpi": 90, "quality": 30}
        }
        params = configuraciones[nivel_opcion]
        
        st.session_state.processed_files = {}
        st.session_state.file_stats = {}
        
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            with st.spinner(f"Procesando: {uploaded_file.name}..."):
                bytes_data = uploaded_file.read()
                size_orig = len(bytes_data) / 1024
                
                doc_orig = pymupdf.open(stream=bytes_data, filetype="pdf")
                doc_nuevo = pymupdf.open()
                
                for pagina in doc_orig:
                    pix = pagina.get_pixmap(dpi=params["dpi"])
                    img_bytes = pix.tobytes("jpeg", jpg_quality=params["quality"])
                    
                    nueva_pagina = doc_nuevo.new_page(width=pagina.rect.width, height=pagina.rect.height)
                    nueva_pagina.insert_image(nueva_pagina.rect, stream=img_bytes)
                    
                output_bytes = doc_nuevo.tobytes()
                size_comp = len(output_bytes) / 1024
                
                doc_orig.close()
                doc_nuevo.close()
                
                nombre_salida = f"Optimizado-{nivel_opcion}-{uploaded_file.name}"
                st.session_state.processed_files[nombre_salida] = output_bytes
                
                ahorro = 100 - (size_comp / size_orig * 100) if size_orig > 0 else 0
                st.session_state.file_stats[nombre_salida] = {
                    "orig": f"{size_orig / 1024:.2f} MB" if size_orig > 1024 else f"{size_orig:.2f} KB",
                    "comp": f"{size_comp / 1024:.2f} MB" if size_comp > 1024 else f"{size_comp:.2f} KB",
                    "ahorro": f"{ahorro:.1f}%"
                }
                
                progress_bar.progress((i + 1) / total_files)
                
        st.success("¡Todos los archivos han sido optimizados con éxito!")

# Sección de resultados y descargas
if st.session_state.processed_files:
    st.markdown("---")
    st.subheader("📦 Resultados Listos para Descargar")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, data in st.session_state.processed_files.items():
            zip_file.writestr(filename, data)
    zip_buffer.seek(0)
    
    col_zip, col_reset = st.columns([3, 1])
    with col_zip:
        st.download_button(
            label="📥 Descargar Todos los Archivos (.ZIP)",
            data=zip_buffer,
            file_name="pdfs_optimizados_applogic.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
        
    with col_reset:
        confirmar_limpieza = st.checkbox("⚠️ Confirmar limpieza")
        if st.button("🔄 Limpiar y Reiniciar", use_container_width=True):
            if confirmar_limpieza:
                st.session_state.processed_files = {}
                st.session_state.file_stats = {}
                # Incrementamos el contador para cambiar la clave del file_uploader y vaciarlo
                st.session_state.uploader_counter += 1
                st.rerun()
            else:
                st.warning("Marca la casilla de confirmación.")

    st.write("")
    
    with st.expander("📂 Ver detalles de compresión y descargar archivos uno a uno", expanded=True):
        for filename, data in st.session_state.processed_files.items():
            stats = st.session_state.file_stats.get(filename, {"orig": "N/A", "comp": "N/A", "ahorro": "N/A"})
            
            st.markdown(f"""
                <div class="file-card">
                    <b>📄 {filename}</b><br>
                    <span style="color: #94a3b8; font-size: 0.9rem;">
                        Peso original: <b>{stats['orig']}</b> | 
                        Peso final: <b style="color: #38bdf8;">{stats['comp']}</b> | 
                        Reducción: <b style="color: #4ade80;">Ahorro del {stats['ahorro']}</b>
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            col_info, col_btn = st.columns([3, 1])
            with col_btn:
                st.download_button(
                    label="⬇️ Descargar",
                    data=data,
                    file_name=filename,
                    mime="application/pdf",
                    key=filename,
                    use_container_width=True
                )
            st.write("")

# Pie de página corporativo
st.markdown("""
    <div class="footer">
        Desarrollado con pasión por <b>AppLogic Solutions</b> 🚀 | Todos los derechos reservados.
    </div>
""", unsafe_allow_html=True)
