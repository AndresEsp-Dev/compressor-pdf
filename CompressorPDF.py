import io
import streamlit as st
import pymupdf

st.set_page_config(page_title="Compresor de PDF", page_icon="📄", layout="centered")

st.title("📄 Compresor de PDF Profesional")
st.write("Sube tu archivo PDF, selecciona el nivel de compresión y descárgalo optimizado.")

# Selector de archivo
uploaded_file = st.file_uploader("Elige un archivo PDF", type="pdf")

# Selector de nivel de compresión
nivel = st.selectbox(
    "Nivel de Compresión",
    options=["bajo", "medio", "maximo"],
    format_func=lambda x: {
        "bajo": "Bajo (Mejor calidad visual)", 
        "medio": "Medio (Recomendado para el día a día)", 
        "maximo": "Máximo (Menor peso posible - Ideal para pagarés)"
    }[x],
    index=1
)

if uploaded_file is not None:
    if st.button("Comprimir PDF", type="primary"):
        with st.spinner("Procesando y optimizando documento..."):
            # Parámetros según el nivel elegido
            configuraciones = {
                "bajo": {"dpi": 150, "quality": 80},
                "medio": {"dpi": 120, "quality": 60},
                "maximo": {"dpi": 90, "quality": 30}
            }
            params = configuraciones[nivel]
            
            # Leer el archivo desde la memoria
            bytes_data = uploaded_file.read()
            
            # Procesamiento con PyMuPDF en memoria
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
            
            st.success("¡PDF comprimido con éxito!")
            
            # Botón de descarga directa
            st.download_button(
                label="📥 Descargar PDF Comprimido",
                data=output_bytes,
                file_name=f"optimizado_{uploaded_file.name}",
                mime="application/pdf"
            )