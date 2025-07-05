import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import numpy as np
import plotly.express as px
import folium as fl
import warnings
import datetime
from haversine import haversine, Unit
from PIL import Image

# Desabilita todos os avisos
warnings.simplefilter("ignore")

st.set_page_config(
    page_title = "Visão Empresa",
    page_icon = "📈",
    layout = 'wide'
)

#=====================================================================================================================

# FUNÇÕES MODULARES

#=====================================================================================================================

def geo_vision( df1 ):

    ### É uma função que recebe a nossa base de dados e retorna um mapa com as medianas das entregas feitas pelos restaurantes
        
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'City', 'Road_traffic_density']
        df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
        map = fl.Map()
        for index, location_info in df_aux.iterrows():
            latitude = location_info['Delivery_location_latitude']
            longitude = location_info['Delivery_location_longitude']
            fl.Marker([latitude, longitude]).add_to(map)
        folium_static( map, width = 1024, height = 600 )
        return None
    
def order_share_by_week( df1 ):
    ### É uma função que recebe a nossa base de dados e retorna um gráfico de linhas em que mostra a quantidade média de entregas por entregador por 
    ### semana
    
    df_aux01 = (df1.loc[:,['ID','week_of_year']]
                   .groupby('week_of_year')
                   .count()
                   .reset_index())
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .nunique()
                   .reset_index())
    df_aux = pd.merge( df_aux01, df_aux02, how = 'inner')
    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    fig = px.line( df_aux, x = 'week_of_year', y = 'order_by_deliver')
    return fig

def order_by_week( df1 ):
    ### É uma função que recebe o nossa base de dados e retorna um gráfico de linhas em que mostra a quantidade de entregas por entregador por semana.
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = (df1.loc[:, ['ID','week_of_year']]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
    fig = px.line( df_aux, x = 'week_of_year', y = 'ID')
    return fig

def order_by_city_traffic( df1 ):
    ### É uma função que recebe a nossa base de dados e retorna um gráfico de dispersão da quantidade de entregas por cidade e por tipo de tráfego.
    
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                 .groupby(['City', 'Road_traffic_density'])
                 .count()
                 .reset_index())
    df_aux = df_aux.loc[ df_aux['City'] != 'NaN', : ]
    df_aux = df_aux.loc[ df_aux['Road_traffic_density'] != 'NaN', : ]
    fig = px.scatter( df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig

def deliver_by_traffic( df1 ):
    ### Esta função recebe a nossa base de dados e retorna um gráfico de seção da quantidade de entregas por tipo de tráfego.
    
    df_aux = (df1.loc[:,['ID','Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
    df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()
    fig = px.pie( df_aux, values = 'entregas_perc', names = 'Road_traffic_density' )
    return fig
    
def order_by_day( df1 ):
    ### Esta função recebe a nossa base de dados e retorna um gráfico de barras que tras a quantidade de entregas por dia da semana.
    
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
    return fig

def clear_dataframe( df1 ):
    ### Esta função é responsável pela limpeza de nosso Dataframe, seguindo os seguintes passos:
        # 1. Retirando os espaços das strings.
        # 2. Retirando as linhas em que não há informações.
        # 3. Mudando os tipos de variáveis de algumas features que estão como 'object' 
        # 4. Mudando a configuração da data da coluna 'Order_Date'
    ### Temos como retorno o nosso Dataframe limpo para a nossa análise.

    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'multiple_deliveries'] = df1.loc[:,'multiple_deliveries'].str.strip()
    df1.loc[:,'Delivery_person_Age'] = df1.loc[:,'Delivery_person_Age'].str.strip()
    
    linhas_selecionadas = df1.loc[ :, 'Delivery_person_Ratings' ] != 'NaN'
    df1 = df1.loc[ linhas_selecionadas, : ]
    linhas_selecionadas = df1[ 'multiple_deliveries' ] != 'NaN'
    df1 = df1.loc[ linhas_selecionadas, : ]
    linhas_selecionadas = df1[ 'Weatherconditions' ] != 'conditions NaN'
    df1 = df1.loc[ linhas_selecionadas, : ]
    linhas_selecionadas = df1[ 'Road_traffic_density' ] != 'NaN'
    df1 = df1.loc[ linhas_selecionadas, : ]
    linhas_selecionadas = df1[ 'City' ] != 'NaN'
    df1 = df1.loc[ linhas_selecionadas, : ]
    linhas_selecionadas = df1[ 'Festival' ] != 'NaN'
    df1 = df1.loc[ linhas_selecionadas, : ]
    linhas_selecionadas = df1[ 'Delivery_person_Age' ] != 'NaN'
    df1 = df1.loc[ linhas_selecionadas, : ]
    df1[ 'Time_taken(min)' ] = df1[ 'Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df1[ 'Time_taken(min)' ] = df1[ 'Time_taken(min)'].astype( int ) 
    df1 = df1.reset_index( drop = True )
    
    df1[ 'Delivery_person_Age' ] = df1[ 'Delivery_person_Age' ].astype( int )
    df1[ 'Delivery_person_Ratings' ] = df1[ 'Delivery_person_Ratings' ].astype( float )
    df1[ 'multiple_deliveries' ] = df1[ 'multiple_deliveries' ].astype( int )
    df1[ 'Order_Date' ] = pd.to_datetime( df1[ 'Order_Date' ], format = '%d-%m-%Y' )

    return( df1 )
#-----------------------------------INÍCIO DA ESTRUTURA DO CÓDIGO----------------------------------------
#--------------------------------------------------------------------------------------------------------
# O erro que estava ocorrendo e que me tomou um bom tempo, foi que eu não havia chamado a função 'clear_dataframe' # # para a limpeza, por isso o date_slider ainda estava com a estrutura de string, não podendo ser comparada com o si-
# nal '>'.

# Lendo o nosso Dataframe:
df = pd.read_csv( 'train.csv' )

# Primeiro fazemos a cópia de nosso Dataframe para preservar os dados iniciais, se algo fora de nosso escopo ocorrer:
df1 = df.copy()

df1 = clear_dataframe( df1 )
#========================================================================================================
# LAYOUT DA BARRA LATERAL
#========================================================================================================

# Colocação do cabeçalho de nosso site de entregas de comida indiana:
st.header( 'Marketplace - Visão Empresa' )

# Vamos colocar o nosso logotipo na barra lateral:
#image_path = 'logo.png'
image = Image.open('logo.png')
st.sidebar.image( image, width = 300 )

# Escrevendo o nome da empresa na barra lateral:
st.sidebar.markdown( '# Tasty Trials' )
st.sidebar.markdown( '# Fastest Delivery in the Town' )
st.sidebar.markdown( """___""" )

# Fazendo a seleção de datas na barra lateral:
st.sidebar.markdown( '## Selecione a data limite:' )
date_slider = st.sidebar.slider("Qual é a data para a visualização?", 
                                     value = datetime.datetime( 2022, 4, 13 ), 
                                     min_value = datetime.datetime( 2022, 2, 11 ),
                                     max_value = datetime.datetime( 2022, 6, 4 ),
                                     format = 'DD-MM-YYYY')

if date_slider is not None:
    data_formatada = date_slider.strftime( "%d/%m/%Y" )
    st.header( f"Data selecionada: {data_formatada}" )
else:
    st.header( "Nenhuma data selecionada" )
st.sidebar.markdown("""___""")

# Criando uma choice box com as opções de tipo de tráfego, para filtrar ainda mais os nossos gráficos:
st.sidebar.markdown( '## Selecione o tipo de tráfego:' )
selecionados = st.sidebar.multiselect( "Qual é o tipo de tráfego?", 
                                      [ 'Low', 'Medium', 'High', 'Jam' ], 
                                      default = [ 'Low', 'Medium', 'High', 'Jam' ] )
if selecionados:
    texto_formatado = ", ".join( selecionados )
    st.header( texto_formatado )
else:
    st.header( "Nenhuma opção selecionada" )

st.sidebar.markdown("""___""")

# Escrevendo quem criou a página:
st.sidebar.markdown( '## Criado pela Comunidade DS :heart:' )


# Filtros de Datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtros de Tipo de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( selecionados )
df1 = df1.loc[linhas_selecionadas, :]                                    

st.dataframe( df1 )

#=======================================================================================
# LAYOUT DO STREAMLIT
#=======================================================================================

abas = ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica']
tab1, tab2, tab3 = st.tabs(abas)

with tab1:
    with st.container():
        # Order Metric
        fig = order_by_day( df1 )
        st.markdown("# Orders by Day")
        st.plotly_chart(fig, use_container_width = True)
        
        with st.container():
            col1, col2 = st.columns( 2 )
           
            with col1:
                fig = deliver_by_traffic( df1 )
                st.markdown("# Divisão das entregas por Tráfego")
                st.plotly_chart(fig, use_container_width = True)
                
            with col2:
                fig = order_by_city_traffic( df1 )
                st.markdown("# Divisão das entregas por Cidade e Tráfego ")
                st.plotly_chart(fig, use_container_width = True)
        
with tab2:
    with st.container():
        fig = order_by_week( df1 )
        st.markdown("# Order by Week")
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        fig = order_share_by_week( df1 )
        st.markdown("# Order Share by Week")
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.markdown("# Visão Geográfica")
    geo_vision( df1 )
