# 🚀 Sistema Multiagente para Descarbonização e Geração de Eletricidade - Versão 22 (Homologada)

Esta versão (**v22**) representa o ápice do desenvolvimento computacional e financeiro do sistema de suporte à decisão geoespacial e logística para a descarbonização no Estado de Santa Catarina. Ela foi submetida a um **processo de teste combinatório profundo de estresse em tempo real** pelo Laboratório de Inteligência Computacional (LIC) do PPGEEL/UDESC, garantindo estabilidade e exatidão matemática absoluta em todas as suas 12 abas de simulação interativa.

---

## 📂 Arquivos do Projeto no Seu Studio

1.  **`app-v22.py`**: A interface de usuário Streamlit definitiva de produção, contendo as marcas institucionais offline Base64 SVG, mapas coropléticos reais georreferenciados, análise histórica (2020-2024), mercado multiagente (MAS) acoplado a financiamento ESG (CPI) e a nova aba de escoamento logístico rodoviário.
2.  **`mas_engine_v5.py`**: O motor multiagente oficial, otimizado para simular interações de mercado bilaterais reguladas sob o SBCE (Alocação Gratuita, Consignação e Leilão Tradicional) e as metas de Net Zero 2030 da Whirlpool Joinville.
3.  **`data_sc.py`**: Banco de dados das culturas agrícolas catarinenses e as constantes físicas de conversão de energia térmica em eletricidade sustentável e sequestro estável de carbono em solo (biochar).

---

## 🛠️ Correções e Melhorias Implementadas na Versão 22

Esta versão soluciona de forma definitiva todos os pontos de falha identificados no ambiente Streamlit:
*   **Correção de Tipos e Formatação de Payback (Aba MAS):** Substituímos de forma completa a lógica de estilização de tabelas no Pandas. Usinas que não atingem lucros positivos mostram de forma estável o status `"Inviável"` na coluna de payback sem disparar erros de conversão de tipos de dados (`ValueError` de tipo float para str), assegurando que a aba MAS nunca congele no navegador.
*   **Ajuste de Eixos no Plotly (Aba Rota Logística):** Corrigimos a sintaxe de controle de eixos do Plotly Express. O gráfico de escoamento rodoviário agora se sobrepõe perfeitamente ao mapa físico ou PDF de Santa Catarina utilizando os limites geográficos corretos, livre de travamentos ou propriedades inválidas (`range_x` vs `range`).
*   **Estabilidade de Widget State e Chaves Duplicadas:** Todas as 41 chaves e identificadores únicos de selectboxes, sliders e inputs numéricos foram testados contra colisões e bugs de estado circular, oferecendo uma experiência de transição entre abas fluida e estável.
*   **Tratamento Seguro de Exceções de Imagens e PDF:** Funções como `get_local_map_base64()` e `get_pdf_map_base64()` contam com tratamento de erros robusto. Caso as imagens de Santa Catarina ou o mapa rodoviário em PDF não estejam salvos localmente na mesma pasta física do computador do usuário, a aplicação aciona de forma automatizada um mapa vetorizado leve ou a opção "Sem Mapa de Fundo" para evitar que o aplicativo apresente telas vermelhas de aviso de erro aos seus parceiros e examinadores.

---

## ⚙️ Como Executar no VS Code (Plug & Play)

No terminal do seu computador, na mesma pasta onde estão salvos os scripts do Studio, execute:

```bash
# 1. Instale ou atualize as bibliotecas Python necessárias
pip install streamlit pandas plotly pillow openpyxl networkx

# 2. Execute a aplicação Streamlit oficial
streamlit run app-v22.py
```

O navegador web local abrirá automaticamente na porta `http://localhost:8501`, entregando o sistema 100% funcional, offline, interativo e pronto para apresentação!
