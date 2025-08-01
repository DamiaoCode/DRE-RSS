# 📰 Feed RSS - Procedimentos DRE

Este projeto extrai automaticamente informações de procedimentos do RSS feed do Diário da República (Série II - Parte L) e gera um feed RSS completo e estruturado.

## 🚀 Funcionalidades

- ✅ **Extração automática** do RSS feed do Diário da República
- ✅ **Detalhes completos** de cada procedimento (entidade, NIPC, preços, etc.)
- ✅ **Feed RSS válido** compatível com todos os leitores RSS
- ✅ **Atualização automática** via GitHub Actions (diária)
- ✅ **GitHub Pages** com página web para visualização
- ✅ **Informações estruturadas** em formato XML e JSON

## 📁 Estrutura do Projeto

```
RSS - DRE/
├── .github/
│   └── update.yml          # Workflow GitHub Actions
├── RSS/
│   ├── procedimentos_basicos.json     # Dados do RSS
│   ├── procedimentos_completos.json   # Dados + detalhes
│   └── feed_rss_procedimentos.xml     # Feed RSS final
├── scripts/
│   ├── rss_dre_extractor.py           # Script principal
│   └── json_to_rss_converter.py       # Conversor JSON→RSS
├── requirements.txt                    # Dependências Python
├── README.md                          # Este arquivo
└── index.html                         # Página GitHub Pages
```

## 🛠️ Instalação

1. Clone o repositório:

```bash
git clone https://github.com/joaodamiao/RSS-DRE.git
cd RSS-DRE
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
3. Salvar dados em JSON na pasta `RSS/`
4. Gerar automaticamente o feed RSS XML

### Execução Automática

O projeto está configurado para atualizar automaticamente via GitHub Actions:

- **Agendamento**: Diariamente às 8:00 UTC
- **Execução manual**: Disponível na aba Actions do GitHub
- **Deploy automático**: Feed RSS disponível em GitHub Pages

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
- **Tem fundos EU**: Se tem financiamento europeu
- **Plataforma eletrónica**: Plataforma utilizada
- **URL procedimento**: Link para apresentação
- **Autor do anúncio**: Nome e cargo

## 🌐 Acesso ao Feed

### GitHub Pages

- **URL**: https://damiaocode.github.io/RSS-DRE
- **Feed RSS**: https://damiaocode.github.io/DRE-RSS/RSS/feed_rss_procedimentos.xml

### Leitores RSS Compatíveis

- Feedly
- Inoreader
- NetNewsWire
- RSS Reader
- Qualquer leitor RSS padrão

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

## 📈 Estatísticas

O feed inclui estatísticas em tempo real:

- Total de procedimentos
- Data da última atualização
- Informações sobre fundos EU
- Distribuição por entidades

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🔗 Links Úteis

- **RSS Feed Original**: https://files.diariodarepublica.pt/rss/serie2&parte=l-html.xml
- **Diário da República**: https://diariodarepublica.pt/
- **GitHub Pages**: https://joaodamiao.github.io/RSS-DRE/
