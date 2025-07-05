import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = 'Home',
    page_icon = '🎲'
)

# Vamos colocar o nosso logotipo na barra lateral:
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image( image, width = 300 )

# Escrevendo o nome da empresa na barra lateral:
st.sidebar.markdown( '# Tasty Trials' )
st.sidebar.markdown( '# Fastest Delivery in the Town' )
st.sidebar.markdown( """___""" )

# Aqui vamos escrever o título da página de nosso Dashboard.
st.write( '# Tasty Trials Growth Dashboard')

# Vamos escrever uma descrição de nossa análise, um manual de instruções para que o usuário possa aproveitar da
# melhor maneira o nosso trabalho:
st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help:
    - Time de Data Science no Discord:
        - @marcoaureliop85
    """)
