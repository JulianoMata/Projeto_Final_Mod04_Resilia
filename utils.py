from fileinput import filename
from tkinter import font
import pandas as pd
import matplotlib.pyplot as plt


nome_arquivos = {
    'junho': "2021-06-gasolina-etanol.csv",
    'julho': "2021-07-gasolina-etanol.csv",
}


def unir_tabelas():
    junho = pd.read_csv(nome_arquivos['junho'], sep=';')
    junho['Valor de Venda'] = junho['Valor de Venda'].apply(
        lambda x: x.replace(',', '.')).astype(float)

    julho = pd.read_csv(nome_arquivos['julho'], sep=';')
    julho['Valor de Venda'] = julho['Valor de Venda'].apply(
        lambda x: x.replace(',', '.')).astype(float)

    del junho['Valor de Compra']
    del julho['Valor de Compra']

    tudo = junho.append(julho)

    tudo.to_csv("Tudo.csv", index=False, sep=';')


def carregar_dados():
    dado = pd.read_csv('Tudo.csv', parse_dates=[
                       'Data da Coleta'], sep=';', dayfirst=True)
    dado['Semana'] = (dado[Colunas.data_coleta] +
                      pd.Timedelta(days=1)).dt.isocalendar().week
    return dado


def produto_agrupado_por_estado(df, produto):
    return df.loc[df['Produto'] == produto].groupby('Estado - Sigla')


def n_maiores_medias(agrupamento, n_medias):
    return agrupamento.mean().nlargest(n_medias, 'Valor de Venda')


def segmentar_por_bandeira(bandeiras, df):
    return df.loc[df['Bandeira'].isin(bandeiras)]


class Colunas():
    regiao = 'Região - Sigla'
    estado = 'Estado - Sigla'
    municipio = 'Município'
    revenda = 'Revenda'
    cnpj = 'CNPJ da Revenda'
    nome_rua = 'Nome da Rua'
    numero_rua = 'Número da Rua'
    complemento = 'Complemento'
    bairro = 'Bairro'
    cep = ' Cep'
    produto = 'Produto'
    data_coleta = 'Data da Coleta'
    valor_venda = 'Valor de Venda'
    unidade_medida = 'Unidade de Medida'
    bandeira = 'Bandeira'
    semana = 'Semana'


def ranking_agrupamentos(agrupamento):
    return agrupamento.map(lambda x: len(x)).sort_values(ascending=False)


def listar_unicos_da_coluna(dataframe, coluna):
    return dataframe[coluna].unique()


def lista_itens_por_agrupamento_unicos(dataframe, nome_coluna_agrupada, nome_coluna_itens):
    return dataframe.groupby(nome_coluna_agrupada, observed=True).apply(
        (lambda x: list(x[nome_coluna_itens].unique()))
    )


def lista_itens_por_agrupamento(dataframe, nome_coluna_agrupada, nome_coluna_itens):
    return dataframe.groupby(nome_coluna_agrupada, observed=True).apply(
        (lambda x: list(x[nome_coluna_itens]))
    )


def localizar_pelo_cnpj(dataframe, lista_cnpjs):
    return dataframe.loc[dataframe[Colunas.cnpj].isin(lista_cnpjs)]


def localizar_por_empresa_revenda(dataframe, list_nome_empresa_revenda):
    return dataframe.loc[dataframe[Colunas.revenda].isin(list_nome_empresa_revenda)]


def localizar_pela_bandeira(dataframe, bandeiras):
    return dataframe.loc[dataframe[Colunas.bandeira].isin(bandeiras)]


def medias_valores_produtos_por_semana(df):
    _medias_valores_produtos_por_semana = df.groupby(
        [Colunas.produto, Colunas.semana]).mean()
    _medias_valores_produtos_por_semana = _medias_valores_produtos_por_semana.unstack(
        Colunas.produto)
    _medias_valores_produtos_por_semana = _medias_valores_produtos_por_semana.droplevel(
        0, axis=1)
    return _medias_valores_produtos_por_semana


def anotar_eixo_y(figura, eixo_x, valores, precisao, desvio_x, desvio_y, fontsize=12):
    for valor in valores:
        coordenadas = (eixo_x + desvio_x, valor + desvio_y)
        figura.annotate(round(valor, precisao), coordenadas, fontsize=fontsize)


def anotar_valores_grafico(dataframe, figura, precisao, desvio_x, desvio_y, fontsize=12):
    for x, valores in dataframe.iterrows():
        anotar_eixo_y(figura, x, valores, precisao,
                      desvio_x, desvio_y, fontsize)


def grafico_valores_produtos_por_semana(df, precisao=2, desvio_x=0.05, desvio_y=0.001, figsize=(16, 9), nome='', fontsize=12):
    fig, ax = plt.subplots()
    color = ['green', 'yellow', 'red', 'blue', 'black']
    df.plot(style='-o', ax=ax, figsize=figsize,
            title=nome, color=color).legend(loc='best')
    anotar_valores_grafico(df, ax, precisao, desvio_x, desvio_y, fontsize)
    plt.show()


def media_por_produto(df, desempilhar=False):
    group_by_keys = df.columns.difference([Colunas.valor_venda]).to_list()
    group = df.groupby(group_by_keys).mean()

    if desempilhar:
        return group.reset_index()

    return group.unstack(Colunas.produto).droplevel(0, axis=1)


def grafico_por_agrupamento(dataframe_grouped, values, index, columns, precisao=2, desvio_x=0.05, desvio_y=0.001, figsize=(16, 9), fontsize=12):
    for nome, group in dataframe_grouped:
        pivot = pd.pivot_table(group, values=values,
                               index=index, columns=columns)

        grafico_valores_produtos_por_semana(
            pivot, precisao, desvio_x, desvio_y, figsize, nome, fontsize)
