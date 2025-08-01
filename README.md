# 📰 Feed RSS - Procedimentos DRE

Este projeto extrai automaticamente informações de procedimentos do RSS feed do Diário da República (Série II - Parte L) e gera um feed RSS completo e estruturado, incluindo uma interface web moderna para consulta e gestão de procedimentos ativos.

## 🚀 Funcionalidades

- ✅ **Extração automática** do RSS feed do Diário da República
- ✅ **Detalhes completos** de cada procedimento (entidade, NIPC, preços, prazos, etc.)
- ✅ **Feed RSS válido** compatível com todos os leitores RSS
- ✅ **Atualização automática** via GitHub Actions (diária)
- ✅ **GitHub Pages** com interface web moderna e responsiva
- ✅ **Sistema de Seeds** para filtros personalizados por palavras-chave e distrito
- ✅ **Gestão de procedimentos ativos** com filtros por prazo de validade
- ✅ **Interface de pesquisa avançada** com filtros por seed e texto livre
- ✅ **Informações estruturadas** em formato XML e JSON
- ✅ **Persistência local** de seeds e configurações personalizadas

## 📁 Estrutura do Projeto

```
DRE-RSS/
├── .github/
│   └── update.yml          # Workflow GitHub Actions
├── data/
│   ├── DD-MM-YYYY.json     # Ficheiros JSON diários
│   ├── ativos.json         # Procedimentos ativos (prazos válidos)
│   └── seeds.json          # Seeds personalizadas (opcional)
├── scripts/
│   ├── rss_dre_extractor.py    # Script principal de extração
│   ├── json_to_rss_converter.py # Conversor JSON→RSS
│   ├── gerir_ativos.py         # Gestão de procedimentos ativos
│   └── manage_seeds.py         # Gestão de seeds (local)
├── RSS/
│   ├── procedimentos_basicos.json     # Dados do RSS
│   ├── procedimentos_completos.json   # Dados + detalhes
│   └── feed_rss_procedimentos.xml     # Feed RSS final
├── requirements.txt                    # Dependências Python
├── serve.py                           # Servidor local para desenvolvimento
├── README.md                          # Este arquivo
└── index.html                         # Interface web principal
```

## 🛠️ Instalação

1. Clone o repositório:

```bash
git clone https://github.com/DamiaoCode/DRE-RSS.git
cd DRE-RSS
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Execução Manual

Para executar o processo completo manualmente:

```bash
cd scripts
python rss_dre_extractor.py
```

O script irá:

1. Extrair dados do RSS feed do DRE
2. Acessar cada link e extrair detalhes completos
3. Salvar dados em JSON na pasta `data/` com data (DD-MM-YYYY.json)
4. Gerar automaticamente o feed RSS XML
5. Atualizar o ficheiro `ativos.json` com procedimentos válidos

### Interface Web

Para aceder à interface web:

1. **Desenvolvimento local**:

```bash
python serve.py
```

Aceda a http://localhost:8000

2. **GitHub Pages**:
   Aceda a https://damiaocode.github.io/DRE-RSS/

### Sistema de Seeds

O sistema de seeds permite criar filtros personalizados:

1. **Criar Seed**: Clique em "Criar Seed" na interface
2. **Adicionar palavras-chave**: Separe por vírgulas ou Enter
3. **Selecionar distrito**: Filtro geográfico opcional
4. **Guardar**: Gera um código único para a seed
5. **Usar Seed**: Introduza o código no campo "Pesquisar por Seed"

### Gestão de Seeds (Local)

Para gestão avançada de seeds via linha de comandos:

```bash
cd scripts
python manage_seeds.py
```

Opções disponíveis:

- Adicionar nova seed
- Listar seeds existentes
- Procurar seed por código
- Remover seed

## 📊 Informações Extraídas

O feed RSS contém as seguintes informações para cada procedimento:

### Informações da Entidade

- **Entidade Adjudicante**: Nome da entidade
- **NIPC**: Número de identificação
- **Distrito, Concelho, Freguesia**: Localização
- **Site e E-mail**: Contactos

### Informações do Contrato

- **Designação do contrato**: Título oficial
- **Descrição**: Detalhes do contrato
- **Preço base s/IVA**: Valor do contrato
- **Prazo de execução**: Duração prevista
- **Prazo para apresentação das propostas**: Data e hora limite
- **Tem fundos EU**: Se tem financiamento europeu
- **Plataforma eletrónica**: Plataforma utilizada
- **URL procedimento**: Link para apresentação
- **Autor do anúncio**: Nome e cargo

## 🌐 Interface Web

### Funcionalidades Principais

- **Tabela responsiva** com procedimentos ativos
- **Pesquisa em tempo real** por todos os campos
- **Sistema de seeds** para filtros personalizados
- **Filtros por distrito** para relevância geográfica
- **Expansão de detalhes** ao clicar nas linhas
- **Formatação automática** de datas e preços
- **Interface moderna** e profissional

### Características Técnicas

- **Responsive Design**: Adaptável a todos os dispositivos
- **Local Storage**: Persistência de seeds no navegador
- **CORS Handling**: Servidor local para desenvolvimento
- **Search Optimization**: Pesquisa eficiente em todos os campos
- **Modern UI/UX**: Interface intuitiva e profissional

## 🔧 Configuração

### GitHub Pages

Para ativar o GitHub Pages:

1. Vá para Settings > Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: / (root)

### GitHub Actions

O workflow está configurado em `.github/update.yml`:

- Execução diária automática
- Execução manual disponível
- Commit automático das atualizações
- Geração automática de ficheiros JSON datados

### Desenvolvimento Local

Para desenvolvimento e testes:

```bash
# Servidor local
python serve.py

# Gestão de seeds
cd scripts
python manage_seeds.py
```

## 📈 Gestão de Dados

### Ficheiros JSON

- **DD-MM-YYYY.json**: Dados diários extraídos
- **ativos.json**: Procedimentos com prazos válidos
- **seeds.json**: Seeds personalizadas (opcional)

### Atualização Automática

O sistema mantém automaticamente:

- Procedimentos ativos (prazos não expirados)
- Seeds personalizadas
- Dados históricos organizados por data

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🔗 Links Úteis

- **Interface Web**: https://damiaocode.github.io/DRE-RSS/
- **RSS Feed Original**: https://files.diariodarepublica.pt/rss/serie2&parte=l-html.xml
- **Diário da República**: https://diariodarepublica.pt/
- **Feed RSS Gerado**: https://damiaocode.github.io/DRE-RSS/RSS/feed_rss_procedimentos.xml

## 🆕 Novidades

### Versão 2.0 - Interface Web Completa

- ✅ Interface web moderna e responsiva
- ✅ Sistema de seeds para filtros personalizados
- ✅ Gestão automática de procedimentos ativos
- ✅ Pesquisa avançada por todos os campos
- ✅ Filtros geográficos por distrito
- ✅ Persistência local de configurações
- ✅ Formatação automática de dados
- ✅ Design profissional e intuitivo
