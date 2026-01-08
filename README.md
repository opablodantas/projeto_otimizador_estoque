
# Otimizador de Estoque com IA

Aplicação web desenvolvida em Python com Streamlit para análise de histórico de vendas e apoio à decisão de compra de produtos. O sistema utiliza um modelo de linguagem (LLM) via API da Groq para gerar recomendações de estoque com base em dados agregados de vendas semanais.

## Funcionalidade principal

A aplicação permite:
- Importar um arquivo CSV com dados históricos de vendas
- Filtrar dados por fornecedor e intervalo de semanas
- Selecionar produtos para análise individual
- Gerar relatórios automáticos com recomendações de compra
- Visualizar gráficos de tendência por quantidade ou faturamento
- Consolidar um resumo final das recomendações

As recomendações possíveis são:
- Comprar
- Não Comprar
- Analisar com Mais Cuidado

## Tecnologias utilizadas

- Python 3.10+
- Streamlit
- Pandas
- Altair
- python-dotenv
- Groq API (LLM)

## Estrutura esperada do arquivo CSV

A aplicação foi projetada para ter o ponto e vírgula (`;`) como separador e conter as seguintes colunas:

| Coluna                | Descrição |
|-----------------------|----------|
| Data                  | Data da venda (formato DD/MM/AAAA) |
| Fornecedor            | Nome do fornecedor |
| Descrição             | Nome do produto |
| Quantidade Vendida    | Quantidade vendida |
| Preço de Venda        | Valor total faturado |
| Preço de Custo        | Coluna opcional |

Exemplo:

```

Data;Fornecedor;Descrição;Quantidade Vendida;Preço de Venda;Preço de Custo
01/01/2024;Fornecedor A;Produto X;10;250,00;18,00

```

## Como a análise funciona

1. Os dados são carregados e normalizados
2. A data é convertida em semana ISO
3. As vendas são agregadas por produto e semana
4. São calculadas métricas como:
   - Quantidade total
   - Faturamento total
   - Médias semanais
5. Um resumo é enviado ao modelo de linguagem da Groq
6. O modelo retorna uma recomendação textual estruturada

## Requisitos de ambiente

É necessário definir a variável de ambiente com a chave da Groq:

```

GROQ_API_KEY=seu_token_aqui

```

Recomenda-se o uso de um arquivo `.env`.

## Instalação das dependências

```

pip install streamlit pandas altair python-dotenv groq

```

## Execução da aplicação

```

streamlit run app.py

```

## Observações

- A análise é baseada apenas em dados históricos
- Não há previsão de demanda futura
- O sistema não realiza controle de estoque em tempo real
- As respostas do modelo dependem da disponibilidade da API da Groq

## Estado do projeto

O projeto está estruturado como uma aplicação interativa de apoio à decisão, com foco em análise de vendas históricas e recomendações de compra orientadas por IA.
```
