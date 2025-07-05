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
import plotly.graph_objects as go

# Desabilita todos os avisos
warnings.simplefilter("ignore")

st.set_page_config(
    page_title = "Visão Restaurantes",
    page_icon = "🍽️",
    layout = 'wide'
)

#=====================================================================================================================

# FUNÇÕES MODULARES

#=====================================================================================================================

def distance_distribution( df ):
    """
    Esta função constrói um novo DataFrame com o tempo médio de entrega e o desvio padrão deste tempo, agrupados por cidade e por tipo de pedido.

    Parâmetros:
    - df: DataFrame com as colunas 'City', 'Time_taken(min)' e 'Type_of_order'.

    Retorno:
    _ df_aux: um novo DataFrame com o tempo médio e o desvio padrão do tempo das entregas.
    """
    df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                 .groupby(['City', 'Type_of_order'])
                 .agg({'Time_taken(min)':['mean', 'std']}))
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    return( df_aux )
    
def sunburst_chart( df ):
    """
    Esta função retorna um gráfico ao estilo 'sunburst' com a distribuição do tempo de entrega por cidade e densidade
    de tráfego.

    Parâmetros:
    - df: DataFrame com as colunas 'City', 'Time_taken(min)' e 'Road_traffic_density'.

    Retorno:
    - Um gráfico ao estilo 'sunburst' com a distribuição do tempo de entrega por cidade e densidade de tráfego.
    """
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                  .groupby(['City', 'Road_traffic_density'])
                  .agg({'Time_taken(min)' : ['mean', 'std']}) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], 
                      values = 'avg_time', color = 'std_time', 
                      color_continuous_scale = 'RdBu', 
                      color_continuous_midpoint = np.average(df_aux['std_time']))
    return( fig )
    
def bar_chart( df ):
    """
    Esta função retorna um gráfico de barras com a distribuição do tempo, por cidade.

    Parâmetros:
    - df: DataFrame com as colunas 'City' e 'Time_taken(min)'.

    Retorno:
    - Um gráfico de barras com a distribuição do tempo de entrega por cidade.
    """
    df_aux = (df1.loc[:, ['City', 'Time_taken(min)']]
                 .groupby('City')
                 .agg({'Time_taken(min)':['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'control', 
                         x = df_aux['City'], y = df_aux['avg_time'], 
                         error_y = dict(type = 'data', 
                                        array = df_aux['std_time'])))
    fig.update_layout(barmode = 'group')
    return( fig )
            
def section_chart( df ):
    """
    Esta função retorna um gráfico de seção com o tempo médio de entrega por cidade.

    Parâmetros:
    - df: DataFrame com as colunas 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude',      'Delivery_location_longitude'.

    Retorno:
    - Gráfico de seção com o tempo médio de entrega por cidade.
    """
    
    cols = ([ 'Restaurant_latitude', 
              'Restaurant_longitude', 
              'Delivery_location_latitude', 
              'Delivery_location_longitude' ])

    df1[ 'distance' ] = df1.loc[ :, cols].apply( lambda x :  haversine( (x['Restaurant_latitude'], 
                                                                         x['Restaurant_longitude']), 
                                                                        (x['Delivery_location_latitude'], 
                                                                         x['Delivery_location_longitude']), 
                                                                         unit = Unit.KILOMETERS), axis = 1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data = [go.Pie(labels = avg_distance['City'], 
                                   values = avg_distance['distance'], 
                                   pull = [0, 0.1, 0])])
    return( fig )


def mean_std_time_festival(df, funcao='mean', Festival=True):
    """
    Função que calcula o tempo médio ou o desvio padrão do tempo das entregas,
    durante ou fora do período de festival.

    Parâmetros:
    - df: DataFrame com as colunas 'Time_taken(min)' e 'Festival'
    - funcao: 'mean' para média ou 'std' para desvio padrão
    - Festival: True para entregas durante o festival, False para fora dele

    Retorno:
    - Valor float com 2 casas decimais, de acordo com a função e condição escolhidas
    """
    
    df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    # Define a linha do DataFrame com base na escolha do festival
    if Festival:
        condicao = 'Yes'
    else:
        condicao = 'No'

    # Aplica a função escolhida
    if funcao == 'mean':
        resultado = np.round(df_aux.loc[df_aux['Festival'] == condicao, 'avg_time'], 2)
    elif funcao == 'std':
        resultado = np.round(df_aux.loc[df_aux['Festival'] == condicao, 'std_time'], 2)
    else:
        raise ValueError("A função deve ser 'mean' ou 'std'.")

    return resultado.values[0]  # retorna apenas o número, não uma Series


def distancia_media( df ):
    """
        Função que calcula a distância média das entregas tomando como referência a localização dos restaurantes e das entregas.

        Parâmetros:
        - df: DataFrame.

        Retorna:
        - A distância média das entregas em relação à localização dos restaurantes.
    """
    cols = ([ 'Restaurant_latitude', 
             'Restaurant_longitude', 
             'Delivery_location_latitude', 
             'Delivery_location_longitude' ])
    
    df1[ 'distance' ] = df.loc[ :, cols].apply( lambda x :  haversine( (x['Restaurant_latitude'], 
                                                                         x['Restaurant_longitude']), 
                                                                        (x['Delivery_location_latitude'], 
                                                                         x['Delivery_location_longitude']), 
                                                                        unit = Unit.KILOMETERS), axis = 1)
    
    # Cálculo da média da distância das cidades
    distancia_media = df['distance'].mean()
    return ( distancia_media )

def clear_dataframe( df1 ):
    """
        Função que provoca uma limpeza de nosso DataFrame: tirando espaços, mudando os tipos de variáveis e dropando as linhas em que não há dados.

        Parâmetros:
        - df: Nosso DataFrame bruto.

        Retorna:
        - df: Novo DataFrame com todas as limpezas necessárias.        
    """
    # Vamos retirar os espaços das strings:
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
    
    # Agora vamos retirar aquelas linhas em que não há informações, para isso vamos usar uma condição nas linhas de todas as colunas e verificar em quantas linhas não há informações
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
    
    # Vamos mudar os tipos de variáveis de algumas features que estão como 'object' e mudar a configuração da data da coluna 'Order_Date'
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
df = pd.read_csv( '/home/marco/Marco/marco_ftc_python_jupiter_lab/train.csv' )
# marco_ftc_python/dataset/train.csv

# Primeiro fazemos a cópia de nosso Dataframe para preservar os dados iniciais, se algo fora de nosso escopo ocorrer:
df1 = df.copy()

df1 = clear_dataframe( df1 )

#========================================================================================================
# LAYOUT DA BARRA LATERAL
#========================================================================================================

# Colocação do cabeçalho de nosso site de entregas de comida indiana:
st.header( 'Marketplace - Visão Restaurantes' )

# Vamos colocar o nosso logotipo na barra lateral:
#image_path = 'logo.png'
#marco_ftc_python/projeto_ftc_dashboard/logo.png
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

#===============================================================================
# LAYOUT DO STREAMLIT
#===============================================================================

# Primeiro criamos as abas das diferentes visões possíveis de nossa análise
abas = [ 'Visão Gerencial', '_', '_' ]
tab1, tab2, tab3 = st.tabs(abas)

# Aqui começamos a construir a primeira aba
with tab1:
    # Separamos um espaço que irá conter as nossas colunas e já definimos o título deste espaço:
    with st.container():
        st.title( 'Overall Metrics' )
        
        # Construção das seis colunas
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            # A coluna 1 nos traz a quantidade de entregadores únicos em nossa base de dados:
            st.markdown( '### Entregadores Únicos' )
            delivery_unique = df1.loc[:, 'Delivery_person_ID'].nunique()
            st.metric(label = "", value = delivery_unique)
            
        with col2:
            # A coluna 2 nos traz a distância média das entregas em relação à localização dos restaurantes
            st.markdown( '### Distância Média' )
            mean_distance = distancia_media( df1 )
            st.metric( label = "", value = f"{mean_distance:.2f} km" )
            
        with col3:
            # A coluna 3 nos traz o tempo médio das entregas quando está ocorrendo o Festival:
            st.markdown( '### Tempo médio com Festival' )
            tempo_medio = mean_std_time_festival( df1, funcao = 'mean', Festival = True )
            st.metric( label = "", value = tempo_medio )
            
        with col4:
            # A coluna 4 nos traz o desvio padrão médio quando está ocorrendo o Festival:
            st.markdown( '### Desvio padrão médio com Festival' )
            desvpad = mean_std_time_festival( df1, funcao = 'std', Festival = True )
            st.metric( label = "", value = desvpad )
            
        with col5:
            # A coluna 5 nos traz o tempo médio quando não há Festival:
            st.markdown( '### Tempo médio sem Festival' )
            tempo_medio = mean_std_time_festival( df1, funcao = 'mean', Festival = False )
            st.metric( label = "", value = tempo_medio )
            
        with col6:
            # A coluna 6 nos traz o desvio padrão médio quando não há Festival:
            st.markdown( '### Desvio padrão médio sem Festival' )
            desvpad = mean_std_time_festival( df1, funcao = 'std', Festival = False )
            st.metric( label = "", value = desvpad )
            
    with st.container():
        st.markdown( """___""" )
        st.title( "Tempo Médio de Entrega por Cidade" )
        fig = section_chart( df1 )
        st.plotly_chart( fig )
        
    with st.container():
        st.markdown( """___""" )
        st.title( "Distribuição do Tempo por Cidade" )
        fig = bar_chart( df1 )
        st.plotly_chart( fig )
        
    with st.container():
        st.markdown( """___""" )
        st.title("Distribuição do Tempo por Cidade e Densidade de Tráfego")
        fig = sunburst_chart( df1 )
        st.plotly_chart( fig )
        
    with st.container():
        st.markdown( """___""" )
        st.title( "Distribuição da Distância" )
        df_aux = distance_distribution( df )        
        st.dataframe( df_aux )