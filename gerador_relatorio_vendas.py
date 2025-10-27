import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def gerar_dados_vendas():
    # Configurações iniciais
    data_inicio = datetime(2025, 1, 1)
    data_fim = datetime(2025, 9, 30)
    num_dias = (data_fim - data_inicio).days + 1
    
    # Lista de fornecedores (A até J)
    fornecedores = [f"Fornecedor {chr(letra)}" for letra in range(65, 75)]  # A a J
    
    # Produtos por fornecedor
    produtos_por_fornecedor = {}
    for fornecedor in fornecedores:
        letra = fornecedor.split(" ")[1]  # Pega a letra do fornecedor
        produtos_por_fornecedor[fornecedor] = [f"Produto {letra}{i}" for i in range(1, 7)]  # 6 produtos por fornecedor
    
    # Lista para armazenar os dados
    dados = []
    
    # Gerar dados para cada dia no período
    for dia in range(num_dias):
        data_atual = data_inicio + timedelta(days=dia)
        
        # Para cada fornecedor, gerar vendas de alguns produtos aleatórios
        for fornecedor in fornecedores:
            # Selecionar aleatoriamente quantos produtos deste fornecedor venderam neste dia (1 a 4 produtos)
            num_produtos_vendidos = random.randint(1, 4)
            produtos_selecionados = random.sample(produtos_por_fornecedor[fornecedor], num_produtos_vendidos)
            
            for produto in produtos_selecionados:
                # Gerar quantidade vendida (1 a 120)
                quantidade = random.randint(1, 120)
                
                # Gerar preço de custo (R$ 1,50 a R$ 530,59)
                preco_custo = round(random.uniform(1.50, 530.59), 2)
                
                # Gerar preço de venda (sempre maior que o custo)
                # Margem de lucro entre 10% e 150%
                margem_lucro = random.uniform(0.10, 1.50)
                preco_venda = round(preco_custo * (1 + margem_lucro), 2)
                
                # Garantir que o preço de venda seja sempre maior que o custo
                while preco_venda <= preco_custo:
                    preco_venda = round(preco_venda * 1.1, 2)
                
                # Adicionar os dados à lista
                dados.append({
                    'Data': data_atual.strftime('%d/%m/%Y'),
                    'Fornecedor': fornecedor,
                    'Descrição': produto,
                    'Quantidade Vendida': quantidade,
                    'Preço de Venda': preco_venda,
                    'Preço de Custo': preco_custo
                })
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Ordenar por data
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    df = df.sort_values('Data')
    df['Data'] = df['Data'].dt.strftime('%d/%m/%Y')
    
    return df

def main():
    print("🔄 Gerando dados sintéticos de vendas...")
    print("📅 Período: 01/01/2025 a 30/09/2025")
    print("🏢 Fornecedores: A a J (10 fornecedores)")
    print("📦 Produtos: 6 produtos por fornecedor (60 produtos no total)")
    
    # Gerar dados
    df_vendas = gerar_dados_vendas()
    
    # CORREÇÃO: Calcular o faturamento total corretamente
    faturamento_total = (df_vendas['Quantidade Vendida'] * df_vendas['Preço de Venda']).sum()
    custo_total = (df_vendas['Quantidade Vendida'] * df_vendas['Preço de Custo']).sum()
    lucro_total = faturamento_total - custo_total
    margem_lucro = (lucro_total / faturamento_total * 100) if faturamento_total > 0 else 0
    
    # Estatísticas básicas
    print(f"\n📊 Estatísticas dos dados gerados:")
    print(f"   • Total de registros: {len(df_vendas):,}")
    print(f"   • Período: {df_vendas['Data'].min()} a {df_vendas['Data'].max()}")
    print(f"   • Fornecedores únicos: {df_vendas['Fornecedor'].nunique()}")
    print(f"   • Produtos únicos: {df_vendas['Descrição'].nunique()}")
    print(f"   • Quantidade total vendida: {df_vendas['Quantidade Vendida'].sum():,}")
    print(f"   • Faturamento total: R$ {faturamento_total:,.2f}")
    print(f"   • Custo total: R$ {custo_total:,.2f}")
    print(f"   • Lucro total: R$ {lucro_total:,.2f}")
    print(f"   • Margem de lucro: {margem_lucro:.1f}%")
    
    # Salvar como CSV
    nome_arquivo = "dados_venda.csv"
    df_vendas.to_csv(nome_arquivo, index=False, sep=',', encoding='utf-8')
    
    # Obter o caminho completo do arquivo
    caminho_completo = os.path.abspath(nome_arquivo)
    
    print(f"\n✅ Arquivo '{nome_arquivo}' gerado com sucesso!")
    print(f"📍 Localização: {caminho_completo}")
    
    # Mostrar amostra dos dados
    print(f"\n🔍 Amostra dos dados (primeiras 10 linhas):")
    print(df_vendas.head(10).to_string(index=False))
    
    # Estatísticas por fornecedor
    print(f"\n🏭 Estatísticas por fornecedor:")
    stats_fornecedor = df_vendas.groupby('Fornecedor').agg({
        'Quantidade Vendida': 'sum',
        'Preço de Venda': 'mean',
        'Preço de Custo': 'mean',
        'Descrição': 'nunique'
    }).round(2)
    stats_fornecedor.columns = ['Qtd Total', 'Preço Venda Médio', 'Preço Custo Médio', 'Produtos Únicos']
    print(stats_fornecedor)
    
    # Produtos mais vendidos
    print(f"\n🏆 Top 10 produtos mais vendidos:")
    top_produtos = df_vendas.groupby('Descrição').agg({
        'Quantidade Vendida': 'sum',
        'Preço de Venda': 'mean',
        'Fornecedor': 'first'
    }).nlargest(10, 'Quantidade Vendida').round(2)
    print(top_produtos)

if __name__ == "__main__":
    main()