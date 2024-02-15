import mysql.connector
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from babel.numbers import format_currency
import time
import hashlib
from datetime import datetime
import plotly.express as px


 ###########################################################################################################
#################################### CONECTANDO AO BANCO DE DADOS ##########################################
############################################################################################################
def conn_mysql():
    config = {
        "user" : "root",
        "password" : "",
        "host" : "localhost",
        "port" : "3306",
        "database" : "empresa",
        "raise_on_warnings": True
    }    

    try:
        conexao = mysql.connector.connect(**config)
        #st.success("✅")
        return conexao
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco MySQL: {err}. Tente novamente!", icon="🚨")
        return None

#### CONFIGURAÇÃO DA PÁGINA ###

st.set_page_config(
    page_title="Nome da Empresa",
    page_icon="📊",
    layout = "wide",
     initial_sidebar_state="auto",
) 

with st.sidebar:
    st.image("logo.png")
    
    choose = option_menu ("", ["Home", "Funcionários", "Clientes", "Vendas", "Estoque", "Sobre Nós"])


 ###########################################################################################################
############################################# HOME ########################################################
############################################################################################################

if choose == ("Home"):
    def banners_automatico(): #Função para colocar várias imagens num lugar só
        img = [
        "banner1.png",
        "banner2.png",
        #"banner3.png",
        ]
        #Comentei o banner 3, pois estava pesando o site e deixando-o lento.
        # Mudando as fotos automáticamente ##############
        intervalo_segundos = 5  #Tempo para mudar
        imagem_display = st.empty()

        # Criando um Loop #######################
        while True:
            for imgs in img:
                imagem_display.image(imgs, use_column_width=True, width=750)
                time.sleep(intervalo_segundos)

    if __name__ == "__main__":
        banners_automatico()

##Para alterar a home ou adicionar outro conteudo... precisa desativar o loop que altera os banners da página.

 ###########################################################################################################
############################################# FUNCIONÁRIOS #################################################
############################################################################################################
if choose == ("Funcionários"):

    # Função para cadastrar usuário
    def usuario_cadastro():
        usuario = st.text_input("Usuário:")
        contato = st.text_input("Contato:")
        cargo = st.text_input("Cargo")
    
                       
        if st.button("Cadastrar Usuario"):
            conexao = conn_mysql()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("INSERT INTO usuario (Usuario, Contato, Cargo) VALUES (%s, %s, %s)", (usuario, contato, cargo))
                conexao.commit()
                st.success(f"User Cadastrado!!")
                cursor.close()
                conexao.close()
        

    # Função para listar usuários
    def lista_usuarios():
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM usuario")
            resultados = cursor.fetchall()
            if not resultados:
                st.info(":red[Nenhum usuário cadastrado.]")
            else:
            # Transformar os resultados em um DataFrame
                df = pd.DataFrame(resultados, columns=['Funcionário', 'Contato', 'Cargo'])
            # Exibir a tabela
                st.dataframe(df)

    pagina_atual = st.selectbox("Selecione uma opção:", ["Cadastrar Usuário", "Lista de Usuários"])
    if pagina_atual == "Cadastrar Usuário":
        usuario_cadastro()
    elif pagina_atual == "Lista de Usuários":
        lista_usuarios()    



 ###########################################################################################################
############################################# CLIENTES #####################################################
############################################################################################################   
if choose == ("Clientes"):
    #Função Cadastrar Clientes
    def pagina_cadastro(): 
        cpf = st.text_input("CPF:")
        cliente = st.text_input("Nome:")
        email = st.text_input("E-mail:")
        telefone = st.text_input("Telefone:")
        logradouro = st.text_input("Logradouro:")
        numero = st.text_input("Número:")
        bairro = st.text_input("Bairro:")
        cidade = st.text_input("Cidade:")
        uf = st.text_input("UF:")
        if st.button("Cadastrar Cliente"):
            conexao = conn_mysql()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("INSERT INTO cliente (cpf, cliente, email, telefone, logradouro, numero, bairro, cidade, uf) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (cpf, cliente, email, telefone, logradouro, numero, bairro, cidade, uf))
                conexao.commit()
                st.success(f"Cliente cadastrado com sucesso!!")
                cursor.close()
                conexao.close()


    def pesquisar_clientes(): #Função Pesquisa de Clientes Cadastrados
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM cliente")
            resultados = cursor.fetchall()
                

            if not resultados:
                st.info("Nenhum cliente cadastrado.")
            else:
            # Transformar os resultados em um DataFrame
                df = pd.DataFrame(resultados, columns=['CPF', 'Nome', 'E-mail', 'Telefone', 'Logradouro', 'Número', 'Bairro', 'Cidade', 'UF'])
            #Para exibir apenas números no campo CPF, tirar pontos e traços.
                df["CPF"] = df["CPF"].astype(str).str.replace(r'\D+', '', regex=True)
            # Exibir a tabela
                st.dataframe(df)

                    
    pagina_atual = st.selectbox("Selecione uma opção:", ["Cadastro de Cliente", "Pesquisar Cadastro"])

    if pagina_atual == "Cadastro de Cliente":
        pagina_cadastro()
    elif pagina_atual == "Pesquisar Cadastro":
        pesquisar_clientes()            


###########################################################################################################
############################################# VENDAS #####################################################
############################################################################################################ 
if choose == ("Vendas"):
    ##Verificar se o usuário (funcionario) no banco de dados, para autorizar a registrar venda.
    def encontrar_usuario(usuario):
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            # Buscar o usuario na tabela usuario
            cursor.execute("SELECT * FROM usuario WHERE usuario = %s", (usuario,))
            resultado = cursor.fetchone()
            if resultado:
                st.success("Verificado!")              
            else: 
                st.error("Vendedor não autorizado. Verifique o nome e tente novamente!")
        cursor.close()
        conexao.close()
        return usuario

#Verificar se o CPF do cliente está cadastrado no banco de dados, antes de registrar venda.
    def verificar_cpf(cpf):
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM cliente WHERE cpf = %s", (cpf,))
            resultado = cursor.fetchone()
            if resultado:
                st.success("Verificado!")              
            else: 
                st.error("CPF não encontrado. Por favor, cadastrar o cliente antes de realizar a venda!")

#Buscar o cliente pelo CPF cadastrado no banco de dados.               
    def buscar_cliente_por_cpf(cpf):
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
        cursor.execute("SELECT cliente FROM cliente WHERE cpf = %s", (cpf,))
        resultado = cursor.fetchone()
        return resultado

#Preencher o cliente automáticamente após informar o CPF.
    def preencher_cliente_por_cpf(cpf):
        resultado = buscar_cliente_por_cpf(cpf)
        if resultado:
            cliente = resultado[0]
            st.session_state.cliente = cliente
            st.success(f"Cliente: {cliente}")   
        else:
            st.error("Cliente não encontrado, verifique o CPF ou a conexão e tente novamente.")

#Buscar o produto no banco de dados pelo SKU ("Stock Keeping Unit").    
    def buscar_produto_por_sku(sku):
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
        cursor.execute("SELECT produto, preco_unitario FROM estoque WHERE sku = %s", (sku,))
        resultado = cursor.fetchone()
        return resultado

#Preencher automaticamente os campos produto e preço com base no SKU informado.
    def preencher_campos_com_sku(sku):
        resultado = buscar_produto_por_sku(sku)
        if resultado:
            produto, preco_unitario = resultado
            st.session_state.produto = produto
            st.session_state.preco_unitario = preco_unitario
            st.success(f"Produto: {produto}")
            st.number_input("Preço Unitário", value=preco_unitario, key="preco_unitario")
        else:
            st.error("Produto não encontrado para o SKU fornecido.")

#Apresentar erro caso o produto mencionado esteja com estoque igual ou menor a 0.
    def estoque_negativo(sku, quantidade):
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT quantidade FROM estoque WHERE sku = %s", (sku,))
            resultado = cursor.fetchone()
            if resultado is None or resultado[0] < quantidade:
                st.error("SEM ESTOQUE DISPONÍVEL!")
                return False
            elif quantidade <= 0:
                st.error("QUANTIDADE INVÁLIDA!")
                return False
            else:
                return True
        else:
            st.error("Erro de conexão com o banco de dados!")
            return False

##############################################################################################################
#########################  REGISTRAR A VENDA NO SISTEMA #############################
    def registrar_venda():
        cpf = st.text_input("CPF do Cliente")
        if cpf:  # Verifica se o campo do CPF foi preenchido
            verificar_cpf(cpf)
            preencher_cliente_por_cpf(cpf)
            cliente = st.session_state.get("cliente", "")
        else:
            cliente = ""  # Define cliente como vazio se o CPF estiver vazio
            
        usuario = st.text_input("Nome do Vendedor")
        if usuario:
            encontrar_usuario(usuario)
        else:
            usuario = ""
        data_venda = st.date_input("Data da Venda")
        descricao = st.text_input("Observação - opcional")

        # Listas para armazenar informações dos produtos
        skus = []
        quantidades = []
        precos_unitarios = []
        descontos = []
        produtos = [] 
        key_counter = 1  # Variável de contagem para gerar chaves únicas
        
        while True:
            sku_key = f"sku_input_{key_counter}"
            quantidade_key = f"quantidade_input_{key_counter}"
            desconto_key = f"desconto_input_{key_counter}"  
            sku = st.text_input(f"SKU do produto {key_counter}", key=sku_key)
            
            if not sku:  # Se o SKU estiver vazio, sai do loop
                break
            else:
                skus.append(sku)
                produto_info = buscar_produto_por_sku(sku)  # Obtém as informações do produto
                if produto_info:
                    produto, preco_unitario = produto_info
                    preco_unitario = float(preco_unitario)  # Converte para float, pois pode ser uma string
                    quantidade = st.number_input(f"Quantidade para {produto}:", min_value=1, key=quantidade_key)
                    desconto = float(st.number_input(f"Desconto para {produto}:", key=desconto_key))
                
                # Verifica se há estoque disponível
                    if not estoque_negativo(sku, quantidade):
                        st.error(f"Produto {produto} não possui estoque disponível!")
                        continue
                
                # Adiciona as informações à lista de produtos
                    produtos.append((produto, preco_unitario))
                    quantidades.append(quantidade)
                    descontos.append(desconto)
                    precos_unitarios.append(preco_unitario)
                    key_counter += 1  # Incrementa o contador de chaves
                else:
                    st.error("Produto não encontrado para o SKU fornecido.") 

        # Variável de soma para somar todos os valores total da compra.
        soma_precos_total = 0
        for i in range(len(skus)):
            preco_total = quantidades[i] * precos_unitarios[i] - descontos[i]
            st.text(f"Valor referente ao código: {skus[i]}: R$ {preco_total:.2f}")

        # Adiciona o valor atual à soma
            soma_precos_total += preco_total

        # Exibe a soma total da compra
        st.subheader(f"Valor Total da Compra é: R${soma_precos_total:.2f}")

        #Formas de Pagamentos    
        forma_pagamento = st.radio("Forma de Pagamento", ["Débito", "Crédito", "Alimentação", "Boleto", "Dinheiro", "Pix"])
        if forma_pagamento == "Crédito":            
            st.radio("Crédito", ["1X", "2X", "3X", "4X", "5X", "6X", "7X", "8X", "9X", "10X"])    
        if forma_pagamento == "Boleto":
            st.radio("Boleto", ["30 dias", "2X", "3X"])
        if forma_pagamento == "Pix":
            st.image("pix.png", width = 300)
        
        #Mandar para o banco de dados as informações da venda:
        if st.button("Registar Venda"):
            conexao = conn_mysql()
            if conexao:
                cursor = conexao.cursor()
                for i, sku in enumerate(skus):
                    cursor.execute("INSERT INTO vendas (cpf, cliente, usuario, data_venda, descricao, sku, produto, preco_unitario, quantidade, desconto, preco_total, forma_pagamento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (cpf, cliente, usuario, data_venda, descricao, sku, produtos[i][0], produtos[i][1], quantidades[i], descontos[i], round(quantidades[i] * produtos[i][1] - descontos[i], 2), forma_pagamento))
                    # Atualizar a tabela de estoque
                    cursor.execute("UPDATE estoque SET quantidade = quantidade - %s WHERE sku = %s", (quantidades[i], sku))
                conexao.commit()
                st.success("Venda registrada com sucesso!")
            else:
                st.error("Venda não registrada! Verifique a conexão e tente novamente.")

            #Queria colocar uma opção de recibo ou notinha aqui, mas não está gerando.


### CONSULTAR VENDAS REGISTRADAS
    def consultar_vendas():
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM vendas")
            resultados = cursor.fetchall()
                
            if not resultados:
                st.info("Nenhuma venda registrada.")
            else:
############################## TABELA REGISTRO DE VENDAS ##################################

                # Transformar os resultados em um DataFrame
                df = pd.DataFrame(resultados, columns=["id_venda", "cpf", "cliente", "usuario", "sku", "produto", "data_venda", "quantidade", "descricao", "preco_unitario", "preco_total", "desconto",  "forma_pagamento"])
                df["cpf"] = df["cpf"].str.replace(r'\D+', '', regex=True)
                # Aplicar filtros para pesquisar.
                filtro_cliente = st.text_input("Filtrar por cliente", "")
                filtro_forma_pagamento = st.text_input("Filtrar por Forma de Pagamento", "")
                filtro_data_inicio = st.date_input("Filtrar por data de venda (início)")
                filtro_data_fim = st.date_input("Filtrar por data de venda (fim)")

                # Converter os filtros de data para datetime64[ns]
                filtro_data_inicio = pd.Timestamp(filtro_data_inicio)
                filtro_data_fim = pd.Timestamp(filtro_data_fim)

                df_filtrado = df[
                (df["cliente"].str.contains(filtro_cliente, case=False)) &
                (df["forma_pagamento"].str.contains(filtro_forma_pagamento, case=False)) &
                (pd.to_datetime(df["data_venda"]) >= filtro_data_inicio) &
                (pd.to_datetime(df["data_venda"]) <= filtro_data_fim)
            ]

            # Formatar os valores da coluna "sku" para exibir apenas números
                df_filtrado["sku"] = df_filtrado["sku"].astype(str).str.replace(r'\D+', '', regex=True)

            # Formatar a coluna "data_venda" para o formato de data "dia, mês e ano"
                df_filtrado["data_venda"] = pd.to_datetime(df_filtrado["data_venda"]).dt.strftime("%d/%m/%Y")

            # Formatar Preço Unitário e Preço Total como valores monetários no formato "R$ 00,00"
                df_filtrado["preco_unitario"] = df_filtrado["preco_unitario"].map("R$ {:.2f}".format)
                df_filtrado["preco_total"] = df_filtrado["preco_total"].map("R$ {:.2f}".format)
                df_filtrado["desconto"] = df_filtrado["desconto"].map("R$ {:.2f}".format)

            # Renomear as colunas
                df_filtrado = df_filtrado.rename(columns={
                    "id_venda": "ID da Venda",
                    "cpf": "CPF",
                    "cliente": "Nome do Cliente",
                    "usuario": "Vendedor",
                    "sku": "SKU",
                    "produto": "Produto",
                    "data_venda": "Data da Venda",
                    "quantidade": "Quantidade",
                    "descricao": "Observação",
                    "preco_unitario": "Preço Unitário",
                    "preco_total": "Preço Total",
                    "desconto": "Desconto",
                    "forma_pagamento": "Forma de Pagamento"
                })

                # Exibir a tabela
                st.dataframe(df_filtrado)

###############################################################################################################
################### GRÁFICO DE ANÁLISE DE VENDAS #################################                

    def grafico_vendas():
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM vendas")
            resultados = cursor.fetchall()
            if resultados:
                df = pd.DataFrame(resultados, columns=["id_venda", "cpf", "cliente", "usuario", "sku", "produto", "data_venda", "quantidade", "descricao", "preco_unitario", "preco_total", "desconto",  "forma_pagamento"])
                df['data_venda'] = pd.to_datetime(df['data_venda'])

                df['data_venda'] = df['data_venda'].dt.date

            #Gráfico de dispersão com Plotly Express
                fig = px.scatter(df, x='data_venda', y='preco_total', size='quantidade', color='forma_pagamento', hover_data=["cliente", "produto", "preco_unitario", "desconto", "forma_pagamento"], title="Vendas ao longo do tempo")

                fig.update_layout(
                xaxis_title="Data da Venda",
                yaxis_title="Preço Total (R$)",
                legend_title="Forma de Pagamento",
                hovermode='closest'
            )

            # Para mostrar o gráfico.
                st.plotly_chart(fig)
    

    pagina_atual = st.selectbox("Painel de Vendas:", ["Registrar Venda", "Consultar Vendas", "Analisar Gráfico"])
    if pagina_atual == "Registrar Venda":
        registrar_venda()
    elif pagina_atual == "Consultar Vendas":
        consultar_vendas()
    elif pagina_atual == "Analisar Gráfico":
        grafico_vendas()
        

###########################################################################################################
############################################# ESTOQUE #####################################################
############################################################################################################ 
if choose == ("Estoque"):
  #Consultar Estoque  
    def consulta_estoque(): 
        conexao = conn_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM estoque")
            resultados = cursor.fetchall()
        if not resultados:
            st.info(["Nenhum produto cadastrado no sistema."])
        else:
            # Transformar os resultados em um DataFrame
            # Remover vírgulas dos números de código de barras e do SKU
            df = pd.DataFrame(resultados, columns=["SKU", "Cód. Barras", "Data de Entrada", "Qtd.", "Produto", "Modelo", "Marca", "Preço Custo", "Preço Venda", "Setor", "Cor", "Tamanho", "Detalhes"])
            df["SKU"] = df["SKU"].astype(str).str.replace(',', '')
            df["Cód. Barras"] = df["Cód. Barras"].astype(str).str.replace(',', '')
            # Deixar os valores no formato em real "R$XX,XX"
            df["Preço Custo"] = df["Preço Custo"].map("R$ {:.2f}".format)
            df["Preço Venda"] = df["Preço Venda"].map("R$ {:.2f}".format)
            # Exibir a tabela
            st.dataframe(df)

#Cadastrar Produtos no Estoque.
    def cadastro_produto():
        sku = st.text_input("SKU")
        cod_barras = st.text_input("Código de Barras:")
        data_entrada = st.date_input("Data de Entrada")
        quantidade = st.number_input("Quantidade:")
        produto = st.text_input("Produto")
        modelo = st.text_input("Modelo:")
        marca = st.text_input("Marca:")
        preco_custo = st.number_input("Preço de Custo:")
        preco_unitario = st.number_input("Preço Unitário de Venda:")
        setor = st.text_input("setor:")
        cor = st.text_input("Cor:")
        tamanho = st.text_input("Tamanho:")
        detalhes = st.text_input("Detalhes Adicionais (opcional):")
        
        if st.button("Cadastrar Entrada de Produto"):
            conexao = conn_mysql()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("INSERT INTO estoque (sku, cod_barras, data_entrada, quantidade, produto, modelo, marca, preco_custo, preco_unitario, setor, cor, tamanho, detalhes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE quantidade = quantidade + VALUES (quantidade)", (sku, cod_barras, data_entrada, quantidade, produto, modelo, marca, preco_custo, preco_unitario, setor, cor, tamanho, detalhes))
                conexao.commit()
                st.success(f"Produto Cadastrado com Sucesso!")   
                cursor.close()
                conexao.close()
            else:
                st.error("Produto não cadastrado. Verifique a conexão e tente novamente.")

    pagina_atual = st.selectbox("Selecione uma opção:", ["Consultar Estoque", "Cadastrar Produtos"])

    if pagina_atual == "Cadastrar Produtos":
        cadastro_produto()
    elif pagina_atual == "Consultar Estoque":
        if st.button("Pesquisar Todos"):
            consulta_estoque()
    
##########################################################################################################
############################################# SOBRE NÓS ###################################################
############################################################################################################ 
if choose == ("Sobre Nós"):

    ## COLUNAS PARA COLOCAR AS IMAGENS LADO A LADO ##
    col1, col2 = st.columns(2)

    with col1:
        st.image("atendimento.png")
        st.text("")
        st.text("")
        st.text("")
        st.image("sobre.png")

    with col2:
        st.image("equipe.png")
        st.text("")
        st.text("")
        st.text("")
        st.image("suporte.png")

    st.write("Site desenvolvido por Nataniely Quiosi.")
    st.write("Sistema Web de gerencimento de empresa. Nele é possível, cadastrar novos funcionários e clientes. \nRegistrar e gerenciar vendas, cadastrar e consultar estoque, analisar tabelas, gráficos, entre outros.")
    st.write("[Fale Comigo](https://api.whatsapp.com/send?phone=5543991087958&text=Ol%C3%A1%2C%20NattQ.%20Vi%20seu%20site%20de%20gerenciamento%20de%20empresa.)")
    