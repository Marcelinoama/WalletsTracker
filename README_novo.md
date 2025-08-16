# 🤖 Bot Monitor de Compras do Telegram

Bot para monitorar volumes de compras de contratos em grupos do Telegram e notificar quando uma quantidade específica de compras for detectada. **NOVO**: Sistema de janela temporal e grupos separados para monitoramento e notificação!

## 🚀 Funcionalidades

- **Sistema de Janela Temporal**: Conta todas as compras em períodos configuráveis
- **Notificação Imediata**: Alerta assim que threshold é atingido na janela
- **Grupos Separados**: Monitora em um grupo e notifica em outro
- **Contagem por Contrato**: Conta compras individualmente para cada contrato
- **Reset Automático**: Limpa contadores após tempo configurável (padrão: 1 hora)
- **Serviço Systemd**: Execução como serviço do sistema
- **Multi-Admin**: Suporte a múltiplos administradores
- **Configuração Flexível**: Threshold e janela configuráveis

## 📋 Pré-requisitos

- Python 3.8+
- Token do bot do Telegram (obter do @BotFather)
- IDs dos grupos onde o bot será usado

## 🔧 Instalação

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Configuração do arquivo .env:**
```env
BOT_TOKEN=seu_token_do_botfather
GRUPO_MONITORAMENTO=-1001111111  # Grupo onde o bot escuta compras
GRUPO_NOTIFICACAO=-1001222222    # Grupo onde o bot envia alertas
THRESHOLD_COMPRAS=10
COOLDOWN_COMPRAS=15              # Janela temporal em segundos
ADMIN_IDS=123456789,987654321
```

**📋 Modos de Configuração:**
- **Grupos Separados**: Configure GRUPO_MONITORAMENTO e GRUPO_NOTIFICACAO
- **Mesmo Grupo**: Configure só GRUPO_MONITORAMENTO, deixe GRUPO_NOTIFICACAO vazio
- **Todos os Grupos**: Deixe ambos vazios (monitora todos, notifica no mesmo)

⏱️ **Sistema de Janela Temporal:**
- O bot monitora compras em janelas de tempo configuráveis
- Todas as compras dentro da janela são contadas
- Notifica imediatamente quando threshold é atingido
- Padrão: 15 segundos de janela, 10 compras para notificar

## 🚀 Executando o Bot

### Manual
```bash
python3 bot.py
```

### Como Serviço (Recomendado)
```bash
# Iniciar
sudo systemctl start wallet-monitor-bot

# Parar
sudo systemctl stop wallet-monitor-bot

# Reiniciar
sudo systemctl restart wallet-monitor-bot

# Ver status
sudo systemctl status wallet-monitor-bot

# Ver logs em tempo real
sudo journalctl -u wallet-monitor-bot -f
```

## 📱 Comandos Disponíveis

### Para Todos os Usuários
- `/help` - Mostra ajuda e comandos disponíveis
- `/grupoid` ou `/id` - Mostra ID do grupo atual

### Para Administradores
- `/status` - Mostra status atual e contratos monitorados
- `/setthreshold [número]` - Define quantas compras são necessárias para alertar
- `/setcooldown [segundos]` - Define duração da janela de monitoramento

## 🔍 Como Funciona

1. **Detecção**: O bot monitora mensagens que contêm "🟢 BUY"
2. **Extração**: Extrai o nome do token e endereço do contrato
3. **Janela Temporal**: Inicia janela de X segundos na primeira compra
4. **Contagem**: Conta todas as compras do mesmo contrato na janela
5. **Notificação**: Alerta imediatamente quando atinge threshold
6. **Reset**: Após tempo configurado, zera os contadores

## 📊 Exemplo de Funcionamento

```
Configuração: Janela de 15s | Threshold: 3 compras

🕐 10:00:00 → 🟢 BUY SONA → Inicia janela de 15s (1/3)
🕐 10:00:05 → 🟢 BUY SONA → Dentro da janela (2/3)  
🕐 10:00:08 → 🟢 BUY SONA → 🚨 ALERTA ENVIADO! (3/3)
🕐 10:00:12 → 🟢 BUY SONA → Ignora (já notificou)
🕐 10:00:15 → ⏰ Janela finalizada
```

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

## ⚙️ Configurações Avançadas

### Alterar Janela Temporal
```bash
/setcooldown 10    # Janela de 10 segundos
/setcooldown 30    # Janela de 30 segundos
```

### Alterar Threshold
```bash
/setthreshold 5    # Precisa de 5 compras
/setthreshold 15   # Precisa de 15 compras
```

### Ver Status em Tempo Real
```bash
/status            # Ver configuração atual
/grupoid           # Ver ID do grupo atual
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
- Verifique se o bot tem permissões no grupo de notificação

### Erros de permissão nos comandos
- Confirme que seu ID está em ADMIN_IDS
- Use `/help` para ver comandos disponíveis

### Serviço não inicia
- Verifique logs: `sudo journalctl -u wallet-monitor-bot`
- Confirme configuração: `sudo systemctl status wallet-monitor-bot`
- Reinicie: `sudo systemctl restart wallet-monitor-bot`

## ⚠️ Importantes

- **Notificação Única**: Cada contrato só gera UM alerta por janela temporal
- **Reset Automático**: Contadores são zerados automaticamente após 1 hora
- **Apenas Administradores**: Somente IDs configurados em ADMIN_IDS podem usar comandos de configuração
- **Monitoramento Contínuo**: Bot funciona 24/7 como serviço systemd

## 📝 Log de Mudanças

### v2.0.0
- ✅ Sistema de janela temporal para contagem de compras
- ✅ Notificação imediata quando threshold é atingido
- ✅ Grupos separados para monitoramento e notificação
- ✅ Serviço systemd integrado
- ✅ Código otimizado e limpo
- ✅ Comandos simplificados e essenciais

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
2. Confira os logs do bot: `sudo journalctl -u wallet-monitor-bot`
3. Teste com `/help` e `/status`

---

**🔥 Bot v2.0 - Sistema de janela temporal otimizado para monitoramento eficiente de volumes de trading!**
