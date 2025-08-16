# 🤖 Bot Monitor de Compras do Telegram

Bot para monitorar volumes de compras de contratos em grupos do Telegram e notificar quando uma quantidade específica de compras for detectada. **NOVO**: Suporte a grupos separados para monitoramento e notificação!

## 🚀 Funcionalidades

- **Monitoramento Automático**: Detecta mensagens com "🟢 BUY" automaticamente
- **Grupos Separados**: Monitora em um grupo e notifica em outro
- **Contagem por Contrato**: Conta compras individualmente para cada contrato
- **Notificações Inteligentes**: Alerta apenas uma vez quando threshold é atingido
- **Reset Automático**: Limpa contadores após tempo configurável (padrão: 1 hora)
- **Multi-Admin**: Suporte a múltiplos administradores
- **Configuração Flexível**: Threshold configurável por grupo

## 📋 Pré-requisitos

- Python 3.8+
- Token do bot do Telegram (obter do @BotFather)
- ID do grupo onde o bot será usado

## 🔧 Instalação

1. **Clone ou baixe os arquivos**

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Configuração do arquivo .env:**
```env
BOT_TOKEN=seu_token_do_botfather
GRUPO_MONITORAMENTO=-1001111111  # Grupo onde o bot escuta compras
GRUPO_NOTIFICACAO=-1001222222    # Grupo onde o bot envia alertas
THRESHOLD_COMPRAS=10
TEMPO_RESET=3600
ADMIN_IDS=123456789,987654321
LOG_LEVEL=INFO
```

**📋 Modos de Configuração:**
- **Grupos Separados**: Configure GRUPO_MONITORAMENTO e GRUPO_NOTIFICACAO
- **Mesmo Grupo**: Configure só GRUPO_MONITORAMENTO, deixe GRUPO_NOTIFICACAO vazio
- **Todos os Grupos**: Deixe ambos vazios (monitora todos, notifica no mesmo)

## 🎯 Como Obter Configurações Necessárias

### Token do Bot
1. Converse com [@BotFather](https://t.me/botfather) no Telegram
2. Use `/newbot` para criar um novo bot
3. Copie o token fornecido

### IDs dos Grupos
1. Adicione o bot aos grupos (monitoramento e notificação)
2. Use `/grupoid` em cada grupo para ver o ID
3. Ou acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Procure por `"chat":{"id":-123456789` (número negativo)

### Seu ID de Usuário
1. Converse com [@userinfobot](https://t.me/userinfobot)
2. Copie o ID fornecido

## 🏃‍♂️ Executando o Bot

```bash
python bot.py
```

## 📱 Comandos Disponíveis

### Para Todos os Usuários
- `/help` - Mostra ajuda e comandos disponíveis

### Para Administradores
- `/status` - Mostra status atual e contratos monitorados
- `/config` - Menu interativo de configurações
- `/setthreshold [número]` - Define quantas compras são necessárias para alertar

## 🔍 Como Funciona

1. **Detecção**: O bot monitora mensagens que contêm "🟢 BUY"
2. **Extração**: Extrai o nome do token e endereço do contrato
3. **Contagem**: Incrementa contador para aquele contrato específico
4. **Notificação**: Quando atinge o threshold, envia alerta UMA ÚNICA VEZ
5. **Reset**: Após o tempo configurado, zera os contadores

## 📊 Exemplo de Funcionamento

```
Configuração: Threshold = 5

Mensagem 1: "🟢 BUY Pnut on BLOOM" → Contador Pnut = 1
Mensagem 2: "🟢 BUY Pnut on BLOOM" → Contador Pnut = 2
Mensagem 3: "🟢 BUY Pnut on BLOOM" → Contador Pnut = 3
Mensagem 4: "🟢 BUY Pnut on BLOOM" → Contador Pnut = 4
Mensagem 5: "🟢 BUY Pnut on BLOOM" → Contador Pnut = 5 ✅ ALERTA ENVIADO!
Mensagem 6: "🟢 BUY Pnut on BLOOM" → Contador Pnut = 6 (sem alerta)
```

## ⚠️ Importantes

- **Uma Notificação por Contrato**: Cada contrato só gera UM alerta por ciclo
- **Reset Automático**: Contadores são zerados automaticamente após 1 hora (configurável)
- **Apenas Administradores**: Somente IDs configurados em ADMIN_IDS podem usar comandos de configuração
- **Monitoramento Contínuo**: Bot funciona 24/7 uma vez iniciado

## 🛠️ Configurações Avançadas

### Alterar Tempo de Reset
```env
TEMPO_RESET=7200  # 2 horas em segundos
```

### Múltiplos Administradores
```env
ADMIN_IDS=123456789,987654321,111222333
```

### Configuração de Grupos
```env
# Monitorar grupo A e notificar no grupo B
GRUPO_MONITORAMENTO=-1001234567890
GRUPO_NOTIFICACAO=-1001987654321

# Ou monitorar e notificar no mesmo grupo
GRUPO_MONITORAMENTO=-1001234567890
GRUPO_NOTIFICACAO=

# Ou monitorar todos os grupos
GRUPO_MONITORAMENTO=
GRUPO_NOTIFICACAO=
```

## 🔧 Solução de Problemas

### Bot não responde
- Verifique se o token está correto
- Confirme que o bot foi adicionado ao grupo
- Verifique se o bot tem permissões de enviar mensagens

### Notificações não aparecem
- Confirme que threshold está configurado corretamente
- Use `/status` para verificar se compras estão sendo detectadas
- Verifique se o bot tem permissões no grupo

### Erros de permissão nos comandos
- Confirme que seu ID está em ADMIN_IDS
- Use `/help` para ver comandos disponíveis

## 📝 Log de Mudanças

### v1.0.0
- ✅ Monitoramento automático de compras
- ✅ Sistema de contagem por contrato  
- ✅ Notificações inteligentes
- ✅ Comandos administrativos
- ✅ Reset automático de contadores
- ✅ Configuração flexível via .env

## 📄 Licença

Este projeto é de uso livre para fins educacionais e pessoais.

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Confira os logs do bot
3. Teste com `/help` e `/status`

---

**🔥 Bot desenvolvido para monitoramento eficiente de volumes de trading!**
# WalletsTracker
