# Gerador de Documentação

Uma ferramenta de desktop para criar documentações com captura de tela, edição de imagens e geração de PDF.

## Funcionalidades

### 1. Captura de Tela
- Captura seletiva de área da tela
- Salva automaticamente as imagens na pasta `images`
- Interface intuitiva com guia visual

### 2. Editor de Imagens
- Ferramentas de desenho:
  - ✏️ Caneta livre
  - 📏 Linha reta
  - ⬜ Retângulo
  - ➡️ Seta
  - 🔤 Texto
- Personalização:
  - 🎨 Seletor de cores
  - Ajuste de espessura das linhas (1-20px)
- Recursos adicionais:
  - Desfazer última ação
  - Limpar todas as edições
  - Histórico de até 20 ações

### 3. Gerenciamento de Etapas
- Adicionar etapas com nome personalizado
- Editar descrições
- Renomear etapas
- Reordenar etapas (arrastar e soltar)
- Deletar etapas

### 4. Gestão de Templates
- Salvar documentação como template
- Carregar templates existentes
- Organização automática de arquivos

### 5. Capa da Documentação
- Título personalizável
- Descrição detalhada
- Edição simplificada via diálogo

### 6. Geração de PDF
- Layout profissional
- Formatação automática
- Organização por etapas
- Capa personalizada
- Suporte a imagens e textos

## Como Usar

1. **Iniciar o Programa**
   - Execute `doc_creator.py`
   - Interface principal será exibida

2. **Criar Nova Documentação**
   - Clique em "Editar Capa" para definir título e descrição
   - Use "Adicionar Etapa" para capturar telas
   - Selecione a área desejada da tela
   - Nomeie cada etapa

3. **Editar Imagens**
   - Selecione uma etapa da lista
   - Clique em "Editar Imagem"
   - Use as ferramentas de desenho
   - Salve as alterações

4. **Adicionar Descrições**
   - Selecione uma etapa
   - Digite a descrição no campo de texto
   - A descrição é salva automaticamente

5. **Gerar PDF**
   - Clique em "Gerar PDF"
   - Escolha o local para salvar
   - O PDF será gerado com todas as etapas

6. **Trabalhar com Templates**
   - Use "Salvar Template" para armazenar o modelo
   - Use "Carregar Template" para reutilizar documentações

## Estrutura de Arquivos

```
Criador de documentação/
│
├── doc_creator.py    # Arquivo principal
├── requirements.txt  # Bibliotecas Utilizadas
├── images/           # Pasta de imagens das etapas
└── templates/        # Pasta de templates salvos
```

## Requisitos

- Python 3.6+
- PyQt5
- Pillow (PIL)
- FPDF

## Instalação

1. **Clone ou baixe o repositório**

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual**
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute o programa**
   ```bash
   python doc_creator.py
   ```

**Nota:** Se encontrar problemas com versões específicas, você pode atualizar para as versões mais recentes usando:
```bash
pip install --upgrade -r requirements.txt
```