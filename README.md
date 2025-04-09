Instagram Follower & Engagement Analyzer 📊
Um script Python que coleta seguidores e curtidores de posts de um perfil do Instagram, analisa interações e gera um relatório em CSV.

⚙️ Pré-requisitos
Python 3.8+

Bibliotecas: requests, csv, json, datetime, random, time

Cookies de autenticação do Instagram (veja Configuração).

🔧 Configuração
Instale as dependências:

bash
Copy
pip install requests
Configure os cookies:
Edite o script com seus dados:

python
Copy
COOKIES = {
    "csrftoken": "seu_token_aqui",  # Obrigatório
    "ds_user_id": "seu_user_id",    # Obrigatório
    "sessionid": "sua_sessionid"     # Obrigatório
}
USERNAME = "seu_perfil"             # Perfil alvo
💡 Como obter os cookies?

Acesse o Instagram no navegador.

Use o DevTools (F12) > Aplicativo > Cookies > Copie os valores.

🚀 Como Usar
Execute o script:

bash
Copy
python3 instagram_analyzer.py
Saída Esperada:
Arquivo CSV no formato: seguidores_YYYYMMDD_HHMMSS.csv.

Logs detalhados no terminal durante a execução.

📊 Estrutura do CSV Gerado
Campo	Descrição	Exemplo
username	Nome de usuário	"maria_123"
full_name	Nome completo	"Maria Silva"
is_private	Perfil privado?	True/False
is_verified	Perfil verificado?	True/False
data_coleta	Data da coleta	"2024-04-10 14:30"
curtiu_post	Curtiu algum post?	True/False
interacao_score	Pontuação de interação (0 ou 2)	2
⚠️ Limitações
Autenticação: Requer cookies válidos (sessão ativa).

Rate Limit: Pausas aleatórias evitam bloqueios, mas o Instagram pode limitar requisições excessivas.

API Não Oficial: Mudanças na API do Instagram podem quebrar o script.

📌 Melhorias Futuras
Adicionar autenticação via OAuth 2.0.

Suporte a coleta de comentários.

Integração com banco de dados (PostgreSQL).

📄 Licença
MIT License - Consulte o arquivo LICENSE para detalhes.

Contribuições são bem-vindas!
Se encontrar bugs ou tiver sugestões, abra uma issue ou envie um PR.

🔗 Fluxograma do Processo:
   
   flowchart TD
    A[Start] --> B[Configure credentials]
    B --> C[Set API parameters]
    C --> D[Collect followers via GraphQL]
    D --> E{API success?}
    E -->|Yes| F[Extract follower data]
    E -->|No| G[Log error and exit]
    F --> H[Collect post likers]
    H --> I{Posts found?}
    I -->|Yes| J[Extract likers for each post]
    I -->|No| K[Skip]
    J --> L[Match followers with likers]
    L --> M[Calculate engagement score]
    M --> N[Save to CSV]
    N --> O[End]
