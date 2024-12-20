import streamlit as st
import gdown
import tensorflow as tf
import io
from PIL import Image
import numpy as np
import pandas as pd
import plotly.express as px

@st.cache_resource
def carrega_modelo():
    #https://drive.google.com/file/d/1S6IlmSmbkunszTumqmrvsPa_gJM2vqC8/view?usp=drive_link
    url = 'https://drive.google.com/uc?id=1S6IlmSmbkunszTumqmrvsPa_gJM2vqC8'
    gdown.download(url, 'modelo_quantizado16bits.tflite')
    interpreter = tf.lite.Interpreter(model_path='modelo_quantizado16bits.tflite')
    interpreter.allocate_tensors()
    return interpreter

def carrega_imagem():
    uploaded_file = st.file_uploader('Arraste e solte uma imagem aqui ou clique para selecionar uma', type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data))

        # Garantir que a imagem tenha 3 canais (convertendo para RGB)
        if image.mode != "RGB":
            image = image.convert("RGB")

        image = image.resize((256, 256))

        st.image(image, caption="Imagem redimensionada para 256x256")
        st.success('Imagem foi carregada com sucesso')

        # Converter para array NumPy com normalização
        image = np.array(image, dtype=np.float32)
        image = image / 255.0

        # Adicionar dimensão extra (para batch)
        image = np.expand_dims(image, axis=0)

        return image

def previsao(interpreter,image):

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    interpreter.set_tensor(input_details[0]['index'],image) 
    
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])

    classes = ['ComMarca', 'SemMarca']
    df = pd.DataFrame()
    df['classes'] = classes
    df['probabilidades (%)'] = 100*output_data[0]
    
    fig = px.bar(df,y='classes',x='probabilidades (%)',  orientation='h', text='probabilidades (%)', title='Sla fodasse kkk teste sla')
    st.plotly_chart(fig)

def main():
    st.set_page_config(
        page_title="Classifica Carros"
    )
    st.write("# Classifica Carros!")
    interpreter = carrega_modelo()
    image = carrega_imagem()
    
    if image is not None:
        previsao(interpreter,image)

if __name__ == "__main__":
    main()