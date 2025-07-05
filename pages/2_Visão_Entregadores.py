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
    page_title = "Visão Entregadores",
    page_icon = "🏍️",
    layout = 'wide'
)

#=====================================================================================================================

# FUNÇÕES MODULARES

#=====================================================================================================================

def rapidez_entregadores( df, high_speed = True ):
    """
        Agrupa os dados pelas colunas de agrupamento e ordena os entregadores mais rápidos por cidade.

        Parâmetros:
        - df: DataFrame de entrada
        - high_speed (bool): Se 'True' calcula o tempo dos entregadores mais rápidos, por cidade. Se 'False' calcula o tempo dos entregadores mais lentos, por cidade 

        Retorna: um DataFrame com os 10 entregadores mais rápidos agrupados por cidade ou com os 10 entregadores mais lentos, dependendo do valor do segundo parâmetro.
        
    """
    if high_speed:
        cols = ['Time_taken(min)', 'City', 'Delivery_person_ID']
    
        df2 = (df1.loc[:, cols]
                  .groupby(['City', 'Delivery_person_ID'])
                  .min()
                  .sort_values( ['City', 'Time_taken(min)'] )
                  .reset_index())
        df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
        df_aux02 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
        df_aux03 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_resultado = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index()
    
    else:
        cols = ['Time_taken(min)', 'City', 'Delivery_person_ID']

        df2 = (df1.loc[:, cols].groupby(['City', 'Delivery_person_ID'])
                  .max()
                  .sort_values( ['City', 'Time_taken(min)'], ascending = False )
                  .reset_index())
        df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
        df_aux02 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
        df_aux03 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_resultado = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index()
    return df_resultado

def agrupar_media_std( df, col_ref, col_agrupamento ):
    """
        Agrupa os dados pela coluna de agrupamento e calcula a média e o desvio padrão
        da coluna de referência.

        Parâmetros:
        - df: DataFrame de entrada
        - col_ref: coluna de referência que terá a média e o desvio padrão calculados
        - col_agrupamento: coluna para agrupar os dados

        Retorna:
        - DataFrame com índice col_agrupamento e colunas: 'media' e 'desvio_padrao'
    """
    df_resultado = ( df[[ col_ref, col_agrupamento]]
                    .groupby( col_agrupamento )
                    .agg( media = ( col_ref, 'mean' ), desvio_padrao = ( col_ref, 'std' ) )
                    .reset_index()
                   )
    return df_resultado

def ratings_per_delivers( df ):
    """
        Retorna um Dataframe com a média das avaliações de cada entregador.

        Parâmetros:
        - df: Dataframe

        Retorna: 
        - df_avg_ratings_per_deliver: um novo Dataframe com as médias de todos os entregadores.

    """
        
    df_avg_ratings_per_deliver = ( df1.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']]
                                      .groupby( ['Delivery_person_ID'] )
                                      .mean()
                                      .reset_index() )
    return( df_avg_ratings_per_deliver )
    
def buscar_extremo( df, coluna, funcao ):
    """
        Retorna o valor mínimo ou máximo de uma coluna, conforme a
        função passada.

        Parâmetros:
        - df: DataFrame
        - coluna: nome da coluna (str)
        - funcao: função a ser usada (ex: min ou max)

        Retorna:
        - Valor extremo da coluna.
    """
    if coluna not in df.columns:
        raise ValueError( f"A coluna '{coluna}' não existe no Dataframe" )
    return funcao( df[ coluna ] )

def clear_dataframe( df1 ):
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
    
     # Corrigir a coluna Time_taken(min):
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).str.extract(r'(\d+)')  # extrai o número
    df1 = df1.dropna(subset=['Time_taken(min)'])  # remove linhas sem número
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
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
df = pd.read_csv( 'train.csv' )

# Primeiro fazemos a cópia de nosso Dataframe para preservar os dados iniciais, se algo fora de nosso escopo ocorrer:
df1 = df.copy()

df1 = clear_dataframe( df1 )

#========================================================================================================
# LAYOUT DA BARRA LATERAL
#========================================================================================================

# Colocação do cabeçalho de nosso site de entregas de comida indiana:
st.header( 'Marketplace - Visão Entregadores' )

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

abas = ['Visão Gerencial', '_', '_']
tab1, tab2, tab3 = st.tabs(abas)

with tab1:
    st.write( "Conteúdo da aba 1" )
    with st.container():
        st.title( "Overall Metrics" )
        
        col1, col2, col3, col4 = st.columns( 4, gap = 'large' )
        
        with col1:
            # Maior idade dos Entregadores
            st.markdown( '### Maior Idade' )
            maior_idade = buscar_extremo( df1, 'Delivery_person_Age', max )                
            col1.metric( 'Maior Idade', maior_idade )
            
        with col2:
            # Menor idade dos Entregadores
            st.markdown( '### Menor Idade' )
            menor_idade = buscar_extremo( df1, 'Delivery_person_Age', min )
            col2.metric( 'Menor Idade', menor_idade )
            
        with col3:
            #Melhor condição de veículos
            st.markdown( '### Melhor condição de veículos' )
            melhor_condicao = buscar_extremo( df1, 'Vehicle_condition',max )
            col3.metric( 'Melhor condição', melhor_condicao )
            
        with col4:
            #Pior condição de veículos
            st.markdown( '### Pior condição de veículos' )
            pior_condicao = buscar_extremo( df1, 'Vehicle_condition', min )
            col4.metric( 'Pior condição', pior_condicao )
            
    with st.container():
        st.markdown("""___""")
        st.title( "Avaliações" )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.subheader( "Avaliações Médias por Entregador" )
            media_entregadores = ratings_per_delivers( df1 )  
            st.dataframe( media_entregadores )
            
        with col2:
            st.markdown( '### Avaliações Médias por Trânsito' )
            media_std_trafego = agrupar_media_std( df1, 'Delivery_person_Ratings', 'Road_traffic_density' )
            st.dataframe( media_std_trafego )
            
            
            st.markdown( '### Avaliações Médias por Clima' )
            media_std_clima = agrupar_media_std( df1, 'Delivery_person_Ratings', 'Weatherconditions' )
            st.dataframe( media_std_clima )
   
    with st.container():
        st.markdown( """___""" )
        st.title( "Velocidade de Entrega" )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( "### Top Entregadores Mais Rápidos" )
            df3 = rapidez_entregadores( df1, high_speed = True )
            st.dataframe( df3 )
            
        with col2:
            st.markdown( "### Top Entregadores Mais Lentos" )
            df3 = rapidez_entregadores( df1, high_speed = False )
            st.dataframe( df3 )

with tab2:
    st.write( "Conteúdo da aba 2" )

with tab3:
    st.write( "Conteúdo da aba 3" )
