import streamlit as st
import SessionState  #   SessionState.py (https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92)
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
from PIL import Image
import math
import locale

#locale.setlocale(locale.LC_ALL, 'pt_BR') # força o locale do Brasil
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto; gets the locale from OS

st.set_page_config(layout='wide')  # <<== usa todo o espaço horizontal da janela do browser
#Para alternativa mais granular, via injeção de html, ver resposta de matthewsjones em:
# https://discuss.streamlit.io/t/custom-render-widths/81/8 

#ver: https://discuss.streamlit.io/t/where-to-set-page-width-when-set-into-non-widescreeen-mode/959/2
st.markdown( f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 2000px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }}
</style>
""",  unsafe_allow_html=True,)

@st.cache 
def get_dados_2020(): 
    #url = "indices_para_streamlit.xlsx"
    url = "índices2020_UTF8.csv"
    #df = pd.read_excel(url, sheet_name="Índices2020")
    df = pd.read_csv(url, sep=";", decimal=",", header=0,) # encoding='iso-8859-1')
    df.drop(["NOME DA EMPRESA", "id", "Nome"], axis=1, inplace = True) #não mostrar esses campos
    df["ID_RESP_2020"] = df["ID_RESP_2020"].astype(str) 
    return df

@st.cache 
def get_dados_FOC(): 
    #url = "indices_para_streamlit.xlsx"
    url = "índicesFOC_UTF8.csv"
    #df = pd.read_excel(url, sheet_name="ÍndicesFOC")
    df = pd.read_csv(url, sep=";", decimal=",", header=0,) # encoding='iso-8859-1')
    df.drop(["NOME"], axis=1, inplace = True) #não mostrar esses campos
    df["ID_RESP_2020"] = df["ID_RESP_2020"].astype(str) 
    return df

@st.cache 
def get_questoes(): 
    #url = "indices_para_streamlit.xlsx"
    url = "questões_UTF8.csv"
    #df = pd.read_excel(url, sheet_name="Questões")
    df = pd.read_csv(url, sep=";", decimal=",", header=0,) # encoding='iso-8859-1')
    return df

st.title("Transparência das empresas estatais") 
#st.header("Índices de Transparência e evolução no período 2016-2020") 

menu = [  "0 Introdução",
          "1 Ranking das empresas no Índice Geral de Transparência",
          "2 Grau de atendimento dos Assuntos (nota média do Assunto)",
          "3 Ranking das empresas em cada Assunto",
          "4 Grau de atendimento das Questões (nota média da Questão)",
          "5 Ranking das empresas em cada Questão",
          "6 Situação da empresa nos Assuntos vs Médias",
          "7 Situação da empresa nas Questões de um Assunto vs Médias",
          "8 Evolução 2016-2020 - Índice Geral de Transparência",
          "9 Evolução 2016-2020 - Situação da empresa por Assunto"
]

st.markdown('### Tipo de análise (selecione uma opção abaixo):')
sb_menu = st.selectbox("", menu)

#pega a opção/radio selecionado:
option = int(str(sb_menu)[0])

# obs: que os valores na session são INICIAIS (atualizados em outras partes do código)
#      (o objeto session abaixo deixou de ser utilizado neste código)
#session = SessionState.get(option=99999)     #valor INICIAL apenas

init_sizes_bars={1:[900, 1050], 2:[900, 500], 3:[944, 1033], 4:[950, 2750], 
                5:[900, 1050], 6:[950, 800], 7:[800, 700], 8:[900, 1050], 9:[950, 800], }
init_sizes_radars={6:[900, 500], 7:[600,600], 8:[900, 700], 9:[900, 500]}

assuntos = ["I. 1 – ADERÊNCIA À LAI",
        "I. 2 – INSTITUCIONAL",
        "I. 3 – AÇÕES E PROGRAMAS",
        "I. 4 – CONVÊNIOS E TRANSFERÊNCIAS",
        "I. 5 –RECEITAS E DESPESAS",
        "I. 6 – LICITAÇÕES E CONTRATOS",
        "I. 7 – DIÁRIAS E PASSAGENS",
        "I. 8 – SERVIDORES, EMPREGADOS PÚBLICOS E AUTORIDADES",
        "I. 9 – INFORMAÇÕES CLASSIFICADAS",
        "I.10 – PARTICIPAÇÃO SOCIAL",
        "I.11- INSTRUMENTOS DE GESTÃO FISCAL",
        "II.1 – SERVIÇO DE INFORMAÇÕES AO CIDADÃO – SIC e e-SIC",
        "III.1 – QUESTÕES ESPECÍFICAS PARA EMPRESAS ESTATAIS"]

mapa_questoes = {
    "I. 1 – ADERÊNCIA À LAI": ["Q01", "Q02",	"Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "Q09", "Q10"],
    "I. 2 – INSTITUCIONAL" : ["Q11", "Q12", "Q13", "Q14", "Q15", "Q16"],
    "I. 3 – AÇÕES E PROGRAMAS": ["Q17", "Q18", "Q19", "Q20"],
    "I. 4 – CONVÊNIOS E TRANSFERÊNCIAS" : ['Q21', 'Q22 [a]', 'Q22 [b]', 'Q22 [c]', 'Q22 [d]', 'Q22 [e]', 'Q22 [f]'],
    "I. 5 –RECEITAS E DESPESAS" : ['Q23', 'Q24 [a]', 'Q24 [b]', 'Q24 [c]', 'Q25', 'Q26 [a]', 'Q26 [b]', 'Q26 [c]', 'Q26 [d]', 'Q26 [e]', 'Q26 [f]', 'Q27', 'Q28', 'Q28_ii', 'Q28_iii', 'Q28_iv', 'Q28_v', 'Q29 [a]', 'Q29 [b]', 'Q29 [c]', 'Q29 [d]'],
    "I. 6 – LICITAÇÕES E CONTRATOS" : ['Q30', 'Q31 [a]', 'Q31 [b]', 'Q31 [c]', 'Q31 [d]', 'Q31 [e]', 'Q31 [f]', 'Q31 [g]', 'Q31 [h]', 'Q31 [i]', 'Q31 [j]', 'Q31 [k]', 'Q31 [l]', 'Q31_ii', 'Q32', 'Q33 [a]', 'Q33 [b]', 'Q33 [c]', 'Q33 [d]', 'Q33 [e]', 'Q33 [f]', 'Q33 [g]', 'Q33 [h]', 'Q33 [i]', 'Q33_ii', 'Q34', 'Q35 [a]', 'Q35 [b]', 'Q35 [c]', 'Q35 [d]'],
    "I. 7 – DIÁRIAS E PASSAGENS" : ['Q36', 'Q37 [a]', 'Q37 [b]', 'Q37 [c]', 'Q37 [d]', 'Q37 [e]', 'Q37 [f]', 'Q37 [g]', 'Q37 [h]', 'Q37 [i]', 'Q38',  'Q39 [a]', 'Q39 [b]', 'Q39 [c]', 'Q39 [d]', 'Q39 [e]', 'Q39 [f]', 'Q39 [g]', 'Q39 [h]', 'Q39 [i]', 'Q40 [a]', 'Q40 [b]', 'Q40 [c]'],
    "I. 8 – SERVIDORES, EMPREGADOS PÚBLICOS E AUTORIDADES" : ['Q41', 'Q42',  'Q43 [a]', 'Q43 [b]', 'Q43 [c]', 'Q43 [d]', 'Q43 [e]', 'Q43 [f]', 'Q43 [g]', 'Q43 [h]', 'Q46 [a]', 'Q46 [b]', 'Q46 [c]', 'Q46 [d]', 'Q46 [e]', 'Q47', 'Q48 [a]', 'Q48 [b]', 'Q48 [c]', 'Q48 [d]', 'Q48 [e]', 'Q49', 'Q50', 'Q51', 'Q52 [a]', 'Q52 [b]', 'Q52 [c]'],
    "I. 9 – INFORMAÇÕES CLASSIFICADAS": ['Q53 [a]', 'Q53 [b]', 'Q53 [c]', 'Q53 [d]', 'Q54'],
    "I.10 – PARTICIPAÇÃO SOCIAL" : ['Q55', 'Q56', 'Q57', 'Q58 [a]', 'Q58 [b]', 'Q58 [c]', 'Q58 [d]', 'Q58 [e]', 'Q58 [f]', 'Q58 [g]', 'Q58 [h]', 'Q58 [i]', 'Q59'],
    "I.11- INSTRUMENTOS DE GESTÃO FISCAL" : ["Q60 [a]", "Q60 [b]", "Q60 [c]"],
    "II.1 – SERVIÇO DE INFORMAÇÕES AO CIDADÃO – SIC e e-SIC": ['Q64 [a]', 'Q64 [b]', 'Q64 [c]', 'Q64 [d]', 'Q64 [e]', 'Q65', 'Q66', 'Q67'],
    "III.1 – QUESTÕES ESPECÍFICAS PARA EMPRESAS ESTATAIS" : ['Q68 [a]', 'Q68 [b]', 'Q68 [c]', 'Q68 [d]', 'Q68 [e]', 'Q68 [f]', 'Q68 [g]', 'Q68 [h]', 'Q68 [i]', 'Q68 [j]', 'Q68 [k]', 'Q68 [l]', 'Q68 [m]', 'Q68 [n]', 'Q68 [o]', 'Q68 [p]', 'Q68 [q]', 'Q68 [r]', 'Q69', 'Q70', 'Q71', 'Q72', 'Q73', 'Q74', 'Q75 [a]', 'Q75 [b]', 'Q75 [c]', 'Q75 [d]', 'Q75 [e]', 'Q75 [f]', 'Q75 [g]', 'Q75_ii', 'Q76 [a]', 'Q76 [b]', 'Q76 [c]', 'Q76 [d]', 'Q76 [e]', 'Q76 [f]', 'Q76 [g]', 'Q76 [h]', 'Q76 [i]', 'Q76 [j]', 'Q77', 'Q78 [a]', 'Q78 [b]', 'Q79 [a]', 'Q79 [b]']
}

#não mais usado, ver comentário em OLD_put_sliders_sidebar()
OLD_side_ph = [   #hack para forçar os sliders sempre no topo da sidebar
    st.sidebar.empty(),
    st.sidebar.empty(),
]

side_ph = ""     #just to keep signature of put_sliders_sidebar()

def put_sliders_sidebar(option, side_ph, is_radar):
    #coloca um slider na área lateral, abaixo do menu, para possibilitar 
    # ao usuário alterar os valores de altura/largura do gráfico, se quiser:
    if is_radar:
        chart_width = init_sizes_radars[option][0]
        chart_height = init_sizes_radars[option][1]
    else:
        chart_width = init_sizes_bars[option][0]
        chart_height = init_sizes_bars[option][1]

    #side_ph é uma lista que tem 2 placeholders no topo da sidebar
    st_width = st.sidebar.slider("Largura do gráfico:", 
                    min_value=300, max_value=2200, 
                    step=100, value=chart_width, )   #value aqui é o INICIAL apenas, ele vai
                                                    #sendo modificado ao se clicar no slider 
    st_height = st.sidebar.slider("Altura do gráfico:", 
                    min_value=300, max_value=3000, 
                    step=100, value=chart_height, )    #value aqui é o INICIAL apenas, ele vai
                                                    #sendo modificado ao se clicar no slider 
    return st_width, st_height

#Esta versão abaixo colocava sliders em placeholders no topo da sidebar,
# porém não estamos mais usando essa abordagem porque o comportamento
# ficou estranho (ao mudar a opção, os widgets ficam "saltando" na sidebar)
def OLD_put_sliders_sidebar(option, side_ph, is_radar):
    #coloca um slider na área lateral, abaixo do menu, para possibilitar 
    # ao usuário alterar os valores de altura/largura do gráfico, se quiser:
    if is_radar:
        chart_width = init_sizes_radars[option][0]
        chart_height = init_sizes_radars[option][1]
    else:
        chart_width = init_sizes_bars[option][0]
        chart_height = init_sizes_bars[option][1]

    #side_ph é uma lista que tem 2 placeholders no topo da sidebar
    st_width = side_ph[0].slider("Largura do gráfico:", 
                    min_value=400, max_value=2500, 
                    step=100, value=chart_width, )   #value aqui é o INICIAL apenas, ele vai
                                                    #sendo modificado ao se clicar no slider 
    st_height = side_ph[1].slider("Altura do gráfico:", 
                    min_value=400, max_value=2500, 
                    step=100, value=chart_height, )    #value aqui é o INICIAL apenas, ele vai
                                                    #sendo modificado ao se clicar no slider 
    return st_width, st_height


def plot_questoes():
    st.markdown('#### Questões avaliadas')
    st.markdown('  ') # line break
    datf = get_questoes().T.reset_index()
    datf.columns=["Questão", "Descrição"]
    datf["Descrição"] = datf["Descrição"].apply(lambda x: x.strip())

    #st.dataframe(datf) #visual ficou ruim, usaremos o go.Table abaixo

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(datf.columns),
                    align='left'
                    ),
        cells=dict(values=datf.transpose().values.tolist(),
                    align='left'
                    ),
    )])

    st.plotly_chart(fig)

    # No texto abaixo, 2 spaces = line break
    st.markdown('''_Observações sobre as questões_:  
- _O questionário acima é genérico e contém questões para outros tipos de instituições, 
não é exclusivo para as empresas estatais_  
- _As questões efetivamente aplicadas às empresas estatais é um subset do conjunto acima_  
- _Esse subset é apresentado nos gráficos e tabelas de dados de cada uma das análises disponíveis na caixa de seleção acima_
    ''')



#------------00000--------------
if option == 0:
    st.sidebar.write("")
    image = Image.open('imagem_transparencia.jpg')
    st.sidebar.image(image, caption='', use_column_width=True)    
    st.markdown('#### Introdução')
    st.markdown('  ') # line break
    st.markdown('''
Em 2016, iniciou-se a primeira avaliação da transparência do sítio de órgãos e entidades federais na internet.  
Em 2020, foi realizado acompanhamento para reavaliar a situação da transparência dessas instituições.  
Este aplicativo mostra os resultados das 57 empresas estatais avaliadas em 2020.  
Também é apresentada a evolução dos índices de transparência no período de 2016 a 2020.  
Para ver os resultados, selecione uma opção por vez na caixa de seleção acima.
    ''') #<<-- there are line breaks here (2 * two spaces)
    st.markdown('''_Observações gerais:_  
- _Para a avaliação dos sítios, as empresas inicialmente preencheram um questionário_
_no qual diversos temas e critérios específicos de transparência foram avaliados._
- _Posteriormente, os sítios das empresas foram objetivamente verificados pelos auditores _
_e as respostas da autoavaliação das empresas foram eventualmente ajustadas._
- _A divulgação dos nomes das empresas avaliadas em 2020 ainda não foi autorizada._
_Por essa razão, as empresas estão identificadas apenas pelo "ID" da sua resposta ao questionário._
- _O relatório deste trabalho ainda está em construção. Portanto, as informações aqui publicadas poderão sofrer alterações._
    ''')

    st_chk_quest = st.sidebar.checkbox('Marque aqui para visualizar as questões do questionário', value=False)
    if st_chk_quest:
        plot_questoes()


#------------11111--------------
if option == 1:
    df2 = get_dados_2020().copy() # necessário clonar, se for alterar algo cached pelo streamlit
    #Comentar o comando abaixo para revelar o nome da empresa na tabela plotada
    df2 = df2.append(df2.mean().rename("Médias"))
    df2["ID_RESP_2020"]["Médias"]="Média" 
 
    #plota a planilha de 2020:
    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True) #fake placeholder para manter o padrão com as outras opções
    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            #locale.format() faz usar "," como separador decimal, pois nosso locale é BR:
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    df2 = df2.sort_values(by='ÍNDICE DE TRANSPARÊNCIA CALCULADO', ascending=False)

    st_width, st_height = put_sliders_sidebar(option, side_ph, False) #poe sliders para altura/largura do gráfico

    #plota gráfico de barras do ranking do índice de transparência em 2020:                        
    fig = go.Figure(go.Bar(
        y='ID-RESP-' + df2['ID_RESP_2020'],
        x=df2['ÍNDICE DE TRANSPARÊNCIA CALCULADO'],
        #textposition='auto',
        hovertemplate='Empresa: %{y}<br>Índice Transp.: = %{x}<extra></extra>',
        #o <extra> vazio acima faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
        orientation='h')
    )

    fig.update_layout(
        separators = ',',  # força virgula como separador decimal
#        yaxis_tickformat = '.2%',
#        yaxis_hoverformat = '.2%',
        xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
        xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
        autosize=False,
        width=st_width, # 900, 
        height=st_height, #1050,
    )

    fig.update_yaxes(autorange="reversed") #mostra do maior para o menor valor de ÍNDICE 

    fig.update_xaxes(automargin = True)  #calcula autom. margin de modo a não cortar texto de labels
    fig.update_yaxes(automargin = True)  #idem
#    fig.update_xaxes(autorange = True)   #calcula autom. o range max e min dos valores
#    fig.update_yaxes(autorange = True)   #idem

    st.plotly_chart(fig)


#------------22222--------------
if option == 2:
    df2 = get_dados_2020()[["ID_RESP_2020"] + assuntos] # id e todos assuntos, para plotar planilha
    df2 = df2.append(df2.mean().rename('Médias'))
    df2["ID_RESP_2020"]["Médias"]="Média:" 

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True) #fake placeholder para manter o padrão com as outras opções
    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    #prepara para gráfico de barras com ranking pela nota média de cada Assunto.
    df3 = df2.drop("ID_RESP_2020", axis=1) #só precisava para visualização do datf
    df3 = df3.iloc[-1,:]  #pega só a última linha, que tem as médias
    #type(df3)  #df3 é só uma Series depois do acima
    df3 = pd.DataFrame(df3) #volta a ser dataframe
    df3 = df3.reset_index() #operação acima gera um index
    df3.rename(columns={"index": "Assunto"}, inplace=True)
    df3 = df3.sort_values(by="Médias", ascending=True)

    st_width, st_height = put_sliders_sidebar(option, side_ph, False) #poe sliders para altura/largura do gráfico

    #plota gráfico de barras do ranking dos assuntos:
    fig = go.Figure(go.Bar(
        y=df3["Assunto"], 
        x=df3["Médias"], 
        #textposition='auto',
        hovertemplate='%{y}<br>Nota média no assunto = %{x}<extra></extra>',
        #o <extra> vazio acima faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
        orientation='h')
    )

    fig.update_layout(
        separators = ',',  # força virgula como separador decimal
        xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
        xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
        autosize=False,
        width= st_width, # 950,
        height= st_height, #500,
    )
    fig.update_yaxes(autorange="reversed") #para mostrar na ordem de valor menor>>>maior 

    st.plotly_chart(fig)


#------------33333--------------
if option == 3:
    df2 = get_dados_2020()[["ID_RESP_2020"] + assuntos] # id e todos assuntos, para plotar planilha
    df2 = df2.append(df2.mean().rename('Médias'))
    df2["ID_RESP_2020"]["Médias"]="Média" #melhor para o gráfico de barras adiante

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True) #fake placeholder para manter o padrão com as outras opções
    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    #seleciona um assunto para o gráfico:
    st.markdown('#### Selecione o "Assunto" que será apresentado no gráfico:')
    st_assunto = st.selectbox("", assuntos)

    #prepara os dados para o gráfico de barras 
    df3 = df2[["ID_RESP_2020", st_assunto]]
    df3 = df3.sort_values(by=st_assunto, ascending=False)

    st_width, st_height = put_sliders_sidebar(option, side_ph, False) #poe sliders para altura/largura do gráfico

    #plota gráfico de barras do ranking das empresas no Assunto/dimensão:
    fig = go.Figure(go.Bar(
        y='ID-RESP-' + df3['ID_RESP_2020'],
        x=df3[st_assunto], 
        #textposition='auto',
        hovertemplate='Empresa: %{y}<br>' +
                       st_assunto + '<br>' +  
                       'Nota no assunto = %{x}<extra></extra>',
        #o <extra> vazio acima faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
        orientation='h')
    )

    fig.update_layout(
        separators = ',',  # força virgula como separador decimal
        xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
        xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
        autosize=False,
        width=st_width, # 900, 
        height=st_height, #1050,
    )
    fig.update_yaxes(autorange="reversed") #mostra do maior para o menor valor de ÍNDICE 

    st.plotly_chart(fig)


#------------44444--------------
if option == 4:
    colunas_manter = ["ID_RESP_2020"] #necessária para visualizar o datf apenas
    for key, arr in mapa_questoes.items():    
        colunas_manter = colunas_manter + arr  #concatena os vários arrays acima; gera um só

    #filtra só as colunas que tem as Questões:
    df2 = get_dados_2020().loc[:, colunas_manter]

    df2 = df2.append(df2.mean().rename('Médias'))
    df2["ID_RESP_2020"]["Médias"]="Média:" 

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True) #fake placeholder para manter o padrão com as outras opções
    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    #prepara para gráfico de barras com ranking pela nota média de cada Questão
    df3 = df2.drop("ID_RESP_2020", axis=1) #só precisava para visualização do datf
    df3 = df3.iloc[-1,:]  #pega só a última linha, que tem as médias
    #type(df3)  #df3 é só uma Series depois do acima
    df3 = pd.DataFrame(df3) #volta a ser dataframe
    df3 = df3.reset_index() #operação acima gera um index
    df3.rename(columns={"index": "Questão"}, inplace=True)
    df3 = df3.sort_values(by="Médias", ascending=True)

    st_width, st_height = put_sliders_sidebar(option, side_ph, False) #poe sliders para altura/largura do gráfico

    #plota gráfico de barras do ranking das questões:
    fig = go.Figure(go.Bar(
        y=df3["Questão"], 
        x=df3["Médias"], 
        #textposition='auto',
        hovertemplate='Questão %{y}<br>Nota média = %{x}<extra></extra>',
        #o <extra> vazio acima faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
        orientation='h')
    )

    fig.update_layout(
        separators = ',',  # força virgula como separador decimal
        xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
        xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
        yaxis = dict( tickfont = dict(size=9)), # gráfico muito longo, diminuímos fonte para aparecer todos os labels
        autosize=False,
        width= st_width, # 950,
        height= st_height, #1500,
    )
    fig.update_yaxes(autorange="reversed") #para mostrar na ordem de valor menor>>>maior 
    
    st.plotly_chart(fig)

    st_chk_quest = st.sidebar.checkbox('Marque aqui para visualizar as questões do questionário', value=False)
    if st_chk_quest:
        plot_questoes()


#------------55555--------------
if option == 5:
    colunas_manter = ["ID_RESP_2020"] # ID necessário para visualizar o datf apenas
    for key, arr in mapa_questoes.items():    
        colunas_manter = colunas_manter + arr  #concatena os vários arrays acima; gera um só

    #filtra só as colunas que tem o ID e as colunas das Questões:
    df2 = get_dados_2020().loc[:, colunas_manter]

    df2 = df2.append(df2.mean().rename('Médias'))
    df2["ID_RESP_2020"]["Médias"]="Média:" 

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True) #fake placeholder para manter o padrão com as outras opções
    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    #seleciona uma questão para o gráfico:
    st.markdown('#### Selecione a Questão que será apresentada no gráfico:')
    colunas_manter.remove("ID_RESP_2020")
    st_questao = st.selectbox("", colunas_manter)

    #prepara os dados para o gráfico de barras 
    df3 = df2[["ID_RESP_2020", st_questao]]
    df3 = df3.sort_values(by=st_questao, ascending=False)

    st_width, st_height = put_sliders_sidebar(option, side_ph, False) #poe sliders para altura/largura do gráfico

    #plota gráfico de barras do ranking das empresas na Questão:
    fig = go.Figure(go.Bar(
        y='ID-RESP-' + df3['ID_RESP_2020'],
        x=df3[st_questao], 
        #textposition='auto',
        hovertemplate='Empresa: %{y}<br>' +
                       'Questão ' + st_questao + '<br>' +  
                       'Nota = %{x}<extra></extra>',
        #o <extra> vazio acima faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
        orientation='h')
    )

    fig.update_layout(
        separators = ',',  # força virgula como separador decimal
        xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
        xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
        autosize=False,
        width=st_width, # 900, 
        height=st_height, #1050,
    )
    fig.update_yaxes(autorange="reversed") #mostra do maior para o menor valor de ÍNDICE 

    st.plotly_chart(fig)

    st_chk_quest = st.sidebar.checkbox('Marque aqui para visualizar as questões do questionário', value=False)
    if st_chk_quest:
        plot_questoes()
    

#------------66666--------------
if option == 6:
    df2 = get_dados_2020()[["ID_RESP_2020"] + assuntos] # id e todos assuntos, para plotar planilha
    df2 = df2.append(df2.mean().rename('Médias'))
    df2["ID_RESP_2020"]["Médias"]="Média" #melhor para o gráfico de barras adiante

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)
    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    #seleciona uma empresa para o gráfico:
    st.markdown('#### Selecione abaixo a empresa a ser apresentada no gráfico:')
    empresas = 'ID-RESP-' + df2["ID_RESP_2020"]  # nomes das empresas
    ids = df2["ID_RESP_2020"]
    dic_empresas = dict(zip(empresas, ids))
    st_empresa = st.selectbox("", empresas)      # apresenta pelo nome
    st_empresa = dic_empresas.get(st_empresa)    # mas usa só ID numérico

    #prepara os dados para o gráfico 
    ## pega só a linha da empresa selecionada e a linha da média:
    df3 = df2.loc[(df2["ID_RESP_2020"]==st_empresa) | (df2["ID_RESP_2020"]=="Média") ]
    df3 = df3.drop("ID_RESP_2020", axis = 1)
    #transpõe:
    df3 = df3.T.reset_index()  #isso gera uma coluna "index", outra <num-row> e outra "Médias"
    df3.columns=['assunto', 'nota', 'média']
    df3 = df3.sort_values(by='assunto', ascending=True)
    #df3=pd.melt(df3,id_vars=['assunto'],var_name='tipo', value_name='valor') #não precisa se Scatterpolar

    st_chk_radar = st.sidebar.checkbox('Marque aqui para ver este gráfico no formato "Radar" ', value=False)
    st_width, st_height = put_sliders_sidebar(option, side_ph, st_chk_radar) #poe sliders para altura/largura do gráfico

    # texto dos Assuntos é muito longo, diminuímos fonte para aparecer completo
    ang_font = 9
    if st_width >= 1100:
        ang_font = 11

    #plota gráfico tipo radar/barras do ranking das empresas no Assunto/dimensão
    if st_chk_radar: #plota gráfico no formato de radar
#         #Este método com Scatterpolar funciona, mas dá problemas ao fazer mouse-Hover         
#         fig = go.Figure()
#         fig.add_trace(go.Scatterpolar(
#             r=df3["nota"],
#             theta=df3["assunto"],
#             fill='toself',
#             hovertemplate = 'Nota da empresa: %{r:.2f} <br>%{theta} <br>',
# #            name='Nota da empresa'
#         ))
#         fig.add_trace(go.Scatterpolar(
#             r=df3["média"],
#             theta=df3["assunto"],
#             fill='toself',
#             hovertemplate = 'Média (todas empresas): %{r:.2f} <br>%{theta} <br>',
# #            name='Média (todas empresas)'
#         ))

#         fig.update_layout(
#         polar=dict(
#             radialaxis=dict(
#             visible=True,
#             range=[0, 1]   #de 0 a 1 (0 a 100%) é o valor de cada nota
#             ),
#             angularaxis = dict(direction = "clockwise")
#             ),
#         showlegend=False,
#         separators = ',',  # força virgula como separador decimal
#         autosize=False,
#         width= st_width, # 1110,    # fazer bem mais largo do que alto, senão "come" parte dos labels
#         height= st_height, # 550,
#         )
#         fig.update_xaxes(automargin = True, autorange = True)  #ajudam ???
#         fig.update_yaxes(automargin = True, autorange = True)  #ajudam ???
#         st.plotly_chart(fig)

        #para usar plotly express line_polar() é melhor o dataframe estar em formato 'long':
        df3_melted = pd.melt(df3,id_vars=['assunto'],var_name='tipo', value_name='valor')
        fig = go.Figure()
        fig = px.line_polar(df3_melted, r='valor', theta='assunto',  
            color = 'tipo', #faz linhas de cores diferentes para tipo=nota e para tipo=média
            line_close=True,
        )

        fig.update_layout(
            # força virgula como separador decimal:
            separators = ',',
            showlegend=True,
            autosize=False,  #?????? VER se MELHOR deixar True, pois não definimos width/height
            width= st_width, # 1110,
            height= st_height, #550,            
            # margin - pode ajustar para maior se textos de labels aparecerem cortados:
        #    margin=dict(l=20, r=20, t=20, b=20, pad=4),
            # obs: resultado ficou melhor com 'automargin' em fig.update_#axes() abaixo
        )

        fig.update_traces(
        #    fill='toself',  # Bug - NÃO usar isso; faz desaparecer info no hover do mouse 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{theta}<br>%{fullData.name}: %{r:.2f}<extra></extra>', 
            #hovertemplate = '%{theta} = %{r:.2f}',
            connectgaps=True,
        )    
        fig.update_polars(  #ver https://plotly.com/python/reference/layout/polar/
            radialaxis_tickmode='linear',
            radialaxis_tick0=0,
            radialaxis_dtick=0.25,
            # o keyword 'range' abaixo não é necessário porque usaremos 'autorange' lá abaixo
            radialaxis_range=[-0.02, 1.02], #de 0.00 a 1.00 é o valor min e max de cada nota
                                             #botamos margem inferior/superior senão a linha "some" no máx.
            angularaxis_direction = "clockwise",
            angularaxis_tickfont = dict(size=ang_font), #ang_font depende do width no slider
        )
        fig.update_xaxes(automargin = True)  #calcula autom. margin de modo a não cortar texto de labels
        fig.update_yaxes(automargin = True)  #idem
#        fig.update_xaxes(autorange = True)   #calcula autom. o range max e min dos valores
#        fig.update_yaxes(autorange = True)   #idem

        st.plotly_chart(fig)

    else: #plota gráfico no formato de barras
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df3['assunto'],
            x=df3["nota"],
            name='nota (da empresa)', 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>nota: %{x:.2f}<extra></extra>', 
            #textposition='auto',
            orientation='h'
        ))

        fig.add_trace(go.Bar(  #necessário adicionar a 2a série com valores das médias
            y=df3['assunto'],
            x=df3["média"], 
            name='média (todas empresas)', 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>média: %{x:.2f}<extra></extra>', 
            #textposition='auto',
            orientation='h'
        ))

        # alternativa ao add_trace() para adição da 2a série é usar o atributo data=[]
        # ver: https://dev.to/fronkan/stacked-and-grouped-bar-charts-using-plotly-python-a4p

        fig.update_layout(
            separators = ',',  # força virgula como separador decimal
            xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
            xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
            autosize=False,
            barmode = 'group', #necessário quando usado fig.add_trace para mais de uma série 
            width=st_width, # 950, 
            height=st_height, #860,
        )

        fig.update_yaxes(autorange="reversed") #mostra do maior para o menor valor 
        st.plotly_chart(fig)


#------------77777--------------
if option == 7:
    df2 = get_dados_2020().copy() # necessário clonar, se for alterar algo cached pelo streamlit
    df2 = df2.append(df2.mean().rename("Médias"))
    df2["ID_RESP_2020"]["Médias"]="Média" 

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)

    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)
        
    #seleciona uma empresa para o gráfico:
    st.markdown('#### Selecione abaixo a empresa a ser apresentada no gráfico:')
    empresas = 'ID-RESP-' + df2["ID_RESP_2020"]  # nomes das empresas
    ids = df2["ID_RESP_2020"]
    dic_empresas = dict(zip(empresas, ids))
    st_empresa = st.selectbox("", empresas)      # apresenta pelo nome
    st_empresa = dic_empresas.get(st_empresa)    # mas usa só ID numérico

    #seleciona um assunto/dimensão para o gráfico:
    st.markdown('#### Selecione abaixo um Assunto:')
    st_assunto = st.selectbox("", assuntos)

    #prepara os dados para o gráfico
    ## pega só a linha da empresa selecionada e a linha da média:
    df3 = df2.loc[(df2["ID_RESP_2020"]==st_empresa) | (df2["ID_RESP_2020"]=="Média") ]

    #mantém apenas as colunas das questões relativas ao Assunto selecionado:
    colunas_manter = mapa_questoes[st_assunto] #retorna a lista de questões do Assunto
    df3 = df3[colunas_manter] #filtra colunas

    #transpõe:
    df3 = df3.T.reset_index()  #isso gera uma coluna "index", outra <num-row> e outra "Médias"
    df3.columns=['questão', 'nota da empresa', 'média geral']
    df3 = df3.sort_values(by='questão', ascending=True)

    st_chk_radar = st.sidebar.checkbox('Marque aqui para ver este gráfico no formato "Radar" ', value=False)
    st_width, st_height = put_sliders_sidebar(option, side_ph, st_chk_radar) #poe sliders para altura/largura do gráfico

    #inicia plotagem do gráfico radar/barras das questões do assunto, para a empresa
    if st_chk_radar: #plota gráfico no formato de radar
        #para usar plotly express line_polar() é melhor o dataframe estar em formato 'long':
        df3_melted = pd.melt(df3,id_vars=['questão'],var_name='tipo', value_name='valor')
        fig = go.Figure()
        fig = px.line_polar(df3_melted, r='valor', theta='questão',  
            color = 'tipo', #faz linhas de cores diferentes para tipo=nota e para tipo=média
            line_close=True,
        )

        fig.update_layout(
            polar=dict( 
                # o keyword 'range' abaixo não é necessário porque usaremos 'autorange' lá abaixo
                radialaxis=dict(
                    range=[-0.02, 1.02]),   #de 0 a 1 é o valor min e max de cada nota
                                            #botamos margem inferior/superior senão a linha "some" no máx.
                angularaxis = dict(
                    direction = "clockwise"),
            ),
            # força virgula como separador decimal:
            separators = ',',
            showlegend=True,
            autosize=False,  #?????? VER se MELHOR deixar True, pois não definimos width/height
            width= st_width, # 600,
            height= st_height, #600,            
            # margin - pode ajustar para maior se textos de labels aparecerem cortados:
        #    margin=dict(l=20, r=20, t=20, b=20, pad=4),
            # obs: resultado ficou melhor com automargin em fig.update_#axes() abaixo
        )

        fig.update_traces(
        #    fill='toself',  # Bug - NÃO usar isso; faz desaparecer info no hover do mouse 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{theta}<br>%{fullData.name}: %{r:.2f}<extra></extra>', 
            #hovertemplate = '%{theta} = %{r:.2f}',
            connectgaps=True,
        )    
        fig.update_polars(  #ver https://plotly.com/python/reference/layout/polar/
            radialaxis_tickmode='linear',
            radialaxis_tick0=0,
            radialaxis_dtick=0.25,
        )
        fig.update_xaxes(automargin = True)  #calcula autom. margin de modo a não cortar texto de labels
        fig.update_yaxes(automargin = True)  #idem
#        fig.update_xaxes(autorange = True)   #calcula autom. o range max e min dos valores
#        fig.update_yaxes(autorange = True)   #idem

        st.plotly_chart(fig)

    else: #plota gráfico no formato de BARRAS
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df3['questão'],
            x=df3["nota da empresa"],
            name='nota da empresa', 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>nota: %{x:.2f}<extra></extra>', 
            #textposition='auto',
            orientation='h'
        ))

        fig.add_trace(go.Bar(  #necessário adicionar a 2a série com valores das médias
            y=df3['questão'],
            x=df3["média geral"], 
            name='média (todas empresas)', 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>média: %{x:.2f}<extra></extra>', 
            #textposition='auto',
            orientation='h'
        ))

        # alternativa ao add_trace() para adição da 2a série é usar o atributo data=[]
        # ver: https://dev.to/fronkan/stacked-and-grouped-bar-charts-using-plotly-python-a4p

        fig.update_layout(
            separators = ',',  # força virgula como separador decimal
            xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
            xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
            autosize=False,
            barmode = 'group', #necessário quando usado fig.add_trace para mais de uma série 
            width= st_width, # 900,
            height= st_height, #840,
        )

        fig.update_yaxes(autorange="reversed") #mostra do maior para o menor valor 
        st.plotly_chart(fig)

    st_chk_quest = st.sidebar.checkbox('Marque aqui para visualizar as questões do questionário', value=False)
    if st_chk_quest:
        plot_questoes()


#------------88888--------------
if option == 8:
    df2 = get_dados_2020()[["ID_RESP_2020", 'ÍNDICE DE TRANSPARÊNCIA CALCULADO']]
    df2.rename(columns={'ÍNDICE DE TRANSPARÊNCIA CALCULADO': "índice"}, inplace=True)
    dfoc = get_dados_FOC()[["ID_RESP_2020", 'ÍNDICE DE TRANSPARÊNCIA CALCULADO']]
    dfoc.rename(columns={'ÍNDICE DE TRANSPARÊNCIA CALCULADO': "índice"}, inplace=True)

    df2 = df2.merge(dfoc, on="ID_RESP_2020", suffixes=('_2020', '_2016'))

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)
    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df2
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    df3 = df2.sort_values(by='ID_RESP_2020', ascending=True)
    df3.rename(columns={'ID_RESP_2020': 'empresa'}, inplace=True)
    df3['empresa'] = 'ID-RESP-' + df3['empresa']

    st_chk_radar = st.sidebar.checkbox('Marque aqui para ver este gráfico no formato "Radar" ', value=False)
    st_width, st_height = put_sliders_sidebar(option, side_ph, st_chk_radar) #poe sliders para altura/largura do gráfico

    #plota gráfico tipo radar/barras do ranking das empresas no Assunto/dimensão
    if st_chk_radar: #plota gráfico no formato de radar

        #para usar plotly express line_polar() é melhor o dataframe estar em formato 'long':
        df3_melted = pd.melt(df3,id_vars=['empresa'],var_name='ano', value_name='valor')
        fig = go.Figure()
        fig = px.line_polar(df3_melted, r='valor', theta='empresa',  
            color = 'ano', #faz linhas de cores diferentes para ano=2016 e para ano=2020
            line_close=True,
        )

        fig.update_layout(
            # força virgula como separador decimal:
            separators = ',',
            showlegend=True,
            autosize=False,  #?????? VER se MELHOR deixar True, pois não definimos width/height
            width= st_width, # 1110,
            height= st_height, #550,            
            # margin - pode ajustar para maior se textos de labels aparecerem cortados:
        #    margin=dict(l=20, r=20, t=20, b=20, pad=4),
            # obs: resultado ficou melhor com 'automargin' em fig.update_#axes() abaixo
        )

        fig.update_traces(
        #    fill='toself',  # Bug - NÃO usar isso; faz desaparecer info no hover do mouse 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{theta}<br>%{fullData.name}: %{r:.2f}<extra></extra>', 
            #hovertemplate = '%{theta} = %{r:.2f}',
            connectgaps=True,
        )    
        fig.update_polars(  #ver https://plotly.com/python/reference/layout/polar/
            radialaxis_tickmode='linear',
            radialaxis_tick0=0,
            radialaxis_dtick=0.25,
            # o keyword 'range' abaixo não é necessário porque usaremos 'autorange' lá abaixo
            radialaxis_range=[-0.02, 1.02], #de 0.00 a 1.00 é o valor min e max de cada nota
                                             #botamos margem inferior/superior senão a linha "some" no máx.
            angularaxis_direction = "clockwise",
            angularaxis_tickfont = dict(size=10), #diminui acúmulo, tem muitos labels no gráfico
        )
        fig.update_xaxes(automargin = True)  #calcula autom. margin de modo a não cortar texto de labels
        fig.update_yaxes(automargin = True)  #idem
#        fig.update_xaxes(autorange = True)   #calcula autom. o range max e min dos valores
#        fig.update_yaxes(autorange = True)   #idem

        st.plotly_chart(fig)

    else: #plota gráfico no formato de barras
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df3['empresa'],
            x=df3["índice_2020"],  # "_2020" é o suffix antes especificado no merge()
            name='Índice Transparência 2020',
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>índice em 2020: %{x:.2f}<extra></extra>', 
            #textposition='auto',
            orientation='h'
        ))

        fig.add_trace(go.Bar(  #necessário adicionar a 2a série com valores das médias
            y=df3['empresa'],
            x=df3["índice_2016"], # "_2016" é o suffix antes especificado no merge()
            name='Índice Transparência foc2016)', 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>índice foc2016: %{x:.2f}<extra></extra>', 
            #textposition='auto',
            orientation='h'
        ))

        # alternativa ao add_trace() para adição da 2a série é usar o atributo data=[]
        # ver: https://dev.to/fronkan/stacked-and-grouped-bar-charts-using-plotly-python-a4p

        fig.update_layout(
            separators = ',',  # força virgula como separador decimal
            xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
            xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
            autosize=False,
            barmode = 'group', #necessário quando usado fig.add_trace para mais de uma série 
            width=st_width, # 950, 
            height=st_height, #860,
        )

        fig.update_yaxes(autorange="reversed") #mostra do maior para o menor valor 
        st.plotly_chart(fig)


#------------99999--------------
if option == 9:
    df2 = get_dados_2020()[["ID_RESP_2020"] + assuntos] # id e todos assuntos, para plotar planilha
    dfoc = get_dados_FOC()[["ID_RESP_2020"] + assuntos] # id e todos assuntos, para plotar planilha

    st_chk_dados = st.sidebar.checkbox('Marque aqui para visualizar a planilha de dados ', value=False)

    #seleciona uma empresa para o gráfico:
    st.markdown('#### Selecione abaixo a empresa a ser apresentada no gráfico:')
    empresas = 'ID-RESP-' + df2["ID_RESP_2020"]  # nomes das empresas
    ids = df2["ID_RESP_2020"]
    dic_empresas = dict(zip(empresas, ids))
    st_empresa = st.selectbox("", empresas)      # apresenta pelo "nome"
    st_empresa = dic_empresas.get(st_empresa)    # mas usa só ID numérico

    #prepara os dados para o gráfico 
    ## pega nos dados 2020 só a linha da empresa selecionada: 
    df3 = df2.loc[df2["ID_RESP_2020"]==st_empresa]
    ## pega nos dados da Foc2016 só a linha da empresa selecionada: 
    dfoc3 = dfoc.loc[dfoc["ID_RESP_2020"]==st_empresa]

    #se o loc acima é "vazio", é o caso de empresa que NÃO participou da foc2016:
    if len(dfoc3) == 0:
        col_names = ["ID_RESP_2020"] + assuntos # id e todos assuntos
        values = [st_empresa] + [pd.NA] * len(assuntos)
        dfoc3 = pd.DataFrame([values], columns = col_names)

    ## junta as linhas de dados de 2016 e 2020 da mesma empresa: 
    df3 = df3.append(dfoc3, ignore_index=True )

    if st_chk_dados:
        #usa locale para fazer os valores decimais aparecerem com separador "," na planilha plotada:
        datf = df3
        #datf = datf.style.format(lambda x: locale.format_string('%.4f', x) if isinstance(x, (int, float)) else x )  #só funciona em jupyter-notebook
        datf = datf.applymap( lambda x: 
            x if isinstance(x, (int, float)) and math.isnan(x) else
            locale.format_string('%.4f', x) if isinstance(x, float) else x)
        st.dataframe(datf)

    #transpõe, ajusta nome de colunas e ordena:
    df3 = df3.drop("ID_RESP_2020", axis=1) #não mais necessária esta coluna
    df3 = df3.T.reset_index()  #isso gera uma coluna "index", outra '0' e outra "1"
    df3.columns=['assunto', '2020', '2016']
    df3 = df3.sort_values(by='assunto', ascending=True)

    st_chk_radar = st.sidebar.checkbox('Marque aqui para ver este gráfico no formato "Radar" ', value=False)
    st_width, st_height = put_sliders_sidebar(option, side_ph, st_chk_radar) #poe sliders para altura/largura do gráfico

    # texto dos Assuntos é muito longo, diminuímos fonte para aparecer completo
    ang_font = 9
    if st_width >= 1100:
        ang_font = 11

    #plota gráfico tipo radar/barras do ranking das empresas no Assunto/dimensão
    if st_chk_radar: #plota gráfico no formato de radar

        #para usar plotly express line_polar() é melhor o dataframe estar em formato 'long':
        df3_melted = pd.melt(df3,id_vars=['assunto'],var_name='ano', value_name='valor')
        fig = go.Figure()
        fig = px.line_polar(df3_melted, r='valor', theta='assunto',  
            color = 'ano', #faz linhas de cores diferentes conforme o ano
            line_close=True,
        )

        fig.update_layout(
            # força virgula como separador decimal:
            separators = ',',
            showlegend=True,
            autosize=False,  #?????? VER se MELHOR deixar True, pois não definimos width/height
            width= st_width, # 1110,
            height= st_height, #550,            
            # margin - pode ajustar para maior se textos de labels aparecerem cortados:
        #    margin=dict(l=20, r=20, t=20, b=20, pad=4),
            # obs: resultado ficou melhor com 'automargin' em fig.update_#axes() abaixo
        )

        fig.update_traces(
        #    fill='toself',  # Bug - NÃO usar isso; faz desaparecer info no hover do mouse 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{theta}<br>%{fullData.name}: %{r:.2f}<extra></extra>', 
            #hovertemplate = '%{theta} = %{r:.2f}',
            connectgaps=True,
        )    
        fig.update_polars(  #ver https://plotly.com/python/reference/layout/polar/
            radialaxis_tickmode='linear',
            radialaxis_tick0=0,
            radialaxis_dtick=0.25,
            # o keyword 'range' abaixo não é necessário porque usaremos 'autorange' lá abaixo
            radialaxis_range=[-0.02, 1.02], #de 0.00 a 1.00 é o valor min e max de cada nota
                                             #botamos margem inferior/superior senão a linha "some" no máx.
            angularaxis_direction = "clockwise",
            angularaxis_tickfont = dict(size=ang_font), #ang_font depende do width no slider
        )
        fig.update_xaxes(automargin = True)  #calcula autom. margin de modo a não cortar texto de labels
        fig.update_yaxes(automargin = True)  #idem
#        fig.update_xaxes(autorange = True)   #calcula autom. o range max e min dos valores
#        fig.update_yaxes(autorange = True)   #idem

        st.plotly_chart(fig)

    else: #plota gráfico no formato de barras
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=df3['assunto'],
            x=df3["2020"],
            #textposition='auto',
            name='nota em 2020', 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>nota em 2020: %{x:.2f}<extra></extra>', 
            orientation='h'
        ))

        fig.add_trace(go.Bar(  #necessário adicionar a 2a série com valores das médias
            y=df3['assunto'],
            x=df3["2016"], 
            #textposition='auto',
            name='nota na Foc2016', 
            #o <extra> vazio abaixo faz sumir o 'name' ao lado direito do hover box (ver https://plotly.com/python/reference/)
            hovertemplate = '%{y}<br>nota foc2016: %{x:.2f}<extra></extra>', 
            orientation='h'
        ))

        # alternativa ao add_trace() para adição da 2a série é usar o atributo data=[]
        # ver: https://dev.to/fronkan/stacked-and-grouped-bar-charts-using-plotly-python-a4p

        fig.update_layout(
            separators = ',',  # força virgula como separador decimal
            xaxis_tickformat = '.0%',  # se barra horizontal, vale para valores em X e Hover
            xaxis_hoverformat = '.2%', # formato hover pega daqui ou, se ausente, de tickformat
            autosize=False,
            barmode = 'group', #necessário quando usado fig.add_trace para mais de uma série 
            width=st_width, # 950, 
            height=st_height, #860,
        )

        fig.update_yaxes(autorange="reversed") #mostra do maior para o menor valor 
        st.plotly_chart(fig)


