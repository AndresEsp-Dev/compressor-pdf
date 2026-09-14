import io
import zipfile
import streamlit as st
import pymupdf

st.set_page_config(page_title="Compresor de PDF", page_icon="📄", layout="centered")

st.title("📄 Compresor de PDF Profesional")
st.write("Sube uno o varios archivos PDF, selecciona el nivel de compresión y descárgalos optimizados.")

# Inicializar session_state para mantener los archivos procesados visibles tras las descargas
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}

uploaded_files = st.file_uploader("Elige uno o más archivos PDF", type="pdf", accept_multiple_files=True)

nivel = st.selectbox(
    "Nivel de Compresión",
    options=["bajo", "medio", "maximo"],
    format_func=lambda x: {
        "bajo": "Bajo (Mejor Calidad Visual / Minima Reducción del Peso)", 
        "medio": "Medio (Recomendado / Peso Equilibrado)", 
        "maximo": "Maximo (Menor Calidad Visual / Menor Peso)"
    }[x],
    index=1
)

if uploaded_files:
    if st.button("Comprimir Archivos", type="primary"):
        configuraciones = {
            "bajo": {"dpi": 150, "quality": 80},
            "medio": {"dpi": 120, "quality": 60},
            "maximo": {"dpi": 90, "quality": 30}
        }
        params = configuraciones[nivel]
        
        st.session_state.processed_files = {}
        
        for uploaded_file in uploaded_files:
            with st.spinner(f"Procesando {uploaded_file.name}..."):
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
                
                st.session_state.processed_files[f"optimizado_{uploaded_file.name}"] = output_bytes

# Mostrar resultados almacenados en session_state para evitar que desaparezcan al interactuar
if st.session_state.processed_files:
    st.write("---")
    st.subheader("📦 Archivos listos para descargar:")
    
    # Botón principal para descargar todo en un archivo ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, data in st.session_state.processed_files.items():
            zip_file.writestr(filename, data)
    zip_buffer.seek(0)
    
    st.download_button(
        label="📥 Descargar Todos en un ZIP",
        data=zip_buffer,
        file_name="pdfs_optimizados.zip",
        mime="application/zip",
        type="primary"
    )
    
    st.write("")
    
    # Menú desplegable (Expander) con la lista de archivos para descarga individual
    with st.expander("📂 Ver archivos individuales para descargar uno a uno", expanded=True):
        for filename, data in st.session_state.processed_files.items():
            st.download_button(
                label=f"⬇️ Descargar {filename}",
                data=data,
                file_name=filename,
                mime="application/pdf",
                key=filename
            )
