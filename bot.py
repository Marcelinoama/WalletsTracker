#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Set
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
import config

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

class ContractMonitor:
    def __init__(self):
        self.contract_counts: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0, 
            'last_seen': datetime.now(), 
            'window_start': None,
            'window_active': False,
            'window_count': 0,
            'buyers': []  # Lista de nomes dos compradores
        })
        self.notified_contracts: Set[str] = set()
        self.group_settings: Dict[int, Dict] = defaultdict(lambda: {'threshold': config.THRESHOLD_COMPRAS, 'enabled': True})
    
    def extract_contract_info(self, text: str) -> tuple:
        # Palavras/tokens que devem ser ignorados - mensagens que contêm estes termos não serão processadas
        ignore_patterns = [
            r'TROLL',
            r'HEAVEN',
            r'🔹🆕🟢',
            r'TEST',
            r'TESTE'
        ]
        
        # Verifica se a mensagem contém padrões que devem ser ignorados
        for ignore_pattern in ignore_patterns:
            if re.search(ignore_pattern, text, re.IGNORECASE):
                return None, None, None
        
        buy_pattern = r'🟢\s*BUY\s+([A-Za-z0-9\.\_\-]+)\s+on\s+([A-Za-z0-9\.\_\-]+)'
        contract_pattern = r'([A-Za-z0-9]{32,})'
        # Padrões para extrair nome do comprador
        buyer_patterns = [
            r'Nome:\s*([^\n\r]+)',  # Formato: Nome: oryx
            r'Buyer:\s*([^\n\r]+)', # Formato: Buyer: oryx 
            r'User:\s*([^\n\r]+)',  # Formato: User: oryx
            r'👤\s*([^\n\r]+)',     # Formato: 👤 oryx
            r'Comprador:\s*([^\n\r]+)', # Formato: Comprador: oryx
        ]
        
        buy_match = re.search(buy_pattern, text, re.IGNORECASE)
        if not buy_match:
            return None, None, None
            
        token_name = buy_match.group(1)
        platform = buy_match.group(2)
        
        contract_matches = re.findall(contract_pattern, text)
        contract_address = contract_matches[0] if contract_matches else f"{token_name}_on_{platform}"
        
        # Extrai nome do comprador - primeiro verifica padrões específicos
        buyer_name = None
        for pattern in buyer_patterns:
            buyer_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if buyer_match:
                buyer_name = buyer_match.group(1).strip()
                break
        
        # Se não encontrou padrão específico, procura na linha seguinte ao BUY
        if not buyer_name:
            lines = text.split('\n')
            buy_line_found = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Se encontrou a linha do BUY, marca para pegar a próxima linha válida
                if re.search(buy_pattern, line, re.IGNORECASE):
                    buy_line_found = True
                    continue
                
                # Se já passou pela linha do BUY, pega a primeira linha válida como nome do comprador
                if buy_line_found and line_stripped:
                    # Verifica se a linha parece ser um nome (não é URL, contrato, etc.)
                    if (not line_stripped.startswith('http') 
                        and not re.match(r'^[A-Za-z0-9]{32,}$', line_stripped)  # Não é endereço de contrato
                        and len(line_stripped) < 50 
                        and not line_stripped.startswith('🟢')
                        and not any(char in line_stripped for char in ['$', '%', 'SOL', 'USD'])):  # Não é valor monetário
                        buyer_name = line_stripped
                        break
        
        # Se ainda não encontrou, usa "Usuário" como padrão
        if not buyer_name:
            buyer_name = "Usuário"
        
        return token_name, contract_address, buyer_name
    
    def reset_old_counts(self):
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=config.TEMPO_RESET)
        
        # Finaliza janelas expiradas
        for contract, data in self.contract_counts.items():
            if data['window_active'] and data['window_start']:
                time_in_window = (current_time - data['window_start']).total_seconds()
                
                if time_in_window > config.COOLDOWN_COMPRAS:
                    final_count = data['count'] + data['window_count']
                    data['count'] = final_count
                    data['last_seen'] = current_time
                    data['window_active'] = False
                    data['window_start'] = None
                    data['window_count'] = 0
                    # Não limpa a lista de compradores aqui, apenas quando o contrato é removido
        
        # Remove contagens antigas
        contracts_to_remove = []
        for contract, data in self.contract_counts.items():
            if data['last_seen'] < cutoff_time:
                contracts_to_remove.append(contract)
        
        for contract in contracts_to_remove:
            del self.contract_counts[contract]
            self.notified_contracts.discard(contract)
    
    def add_purchase(self, contract: str, group_id: int, buyer_name: str = None) -> tuple:
        if not self.group_settings[group_id]['enabled']:
            return False, 0, 0, "disabled"
            
        self.reset_old_counts()
        
        current_time = datetime.now()
        data = self.contract_counts[contract]
        threshold = self.group_settings[group_id]['threshold']
        
        # Adiciona comprador à lista se fornecido (normalizado para evitar duplicatas)
        if buyer_name:
            # Normaliza o nome: minúsculas e remove espaços extras
            normalized_buyer = buyer_name.strip().lower()
            # Verifica se já existe (comparação case-insensitive)
            existing_buyers_normalized = [b.strip().lower() for b in data['buyers']]
            if normalized_buyer not in existing_buyers_normalized:
                data['buyers'].append(buyer_name.strip())  # Armazena com formatação original mas sem espaços extras
        
        # Verifica janela ativa
        if data['window_active'] and data['window_start']:
            time_in_window = (current_time - data['window_start']).total_seconds()
            
            if time_in_window <= config.COOLDOWN_COMPRAS:
                data['window_count'] += 1
                data['last_seen'] = current_time
                
                # Verifica threshold baseado no número de compradores únicos
                unique_buyers_count = len(data['buyers'])
                total_compras = data['count'] + data['window_count']
                if unique_buyers_count >= threshold and contract not in self.notified_contracts:
                    self.notified_contracts.add(contract)
                    return True, total_compras, threshold, "threshold_reached"
                
                return False, total_compras, threshold, "window_active"
            
            else:
                # Janela expirou
                final_count = data['count'] + data['window_count']
                data['count'] = final_count
                data['last_seen'] = current_time
                
                # Verifica threshold baseado no número de compradores únicos
                unique_buyers_count = len(data['buyers'])
                should_notify = (unique_buyers_count >= threshold and contract not in self.notified_contracts)
                if should_notify:
                    self.notified_contracts.add(contract)
                
                # Reset da janela
                data['window_active'] = False
                data['window_start'] = None
                data['window_count'] = 0
                
                # Inicia nova janela
                data['window_active'] = True
                data['window_start'] = current_time
                data['window_count'] = 1
                
                return should_notify, final_count, threshold, "window_completed"
        
        else:
            # Primeira compra - inicia janela
            data['window_active'] = True
            data['window_start'] = current_time
            data['window_count'] = 1
            data['last_seen'] = current_time
            
            # Verifica threshold baseado no número de compradores únicos
            unique_buyers_count = len(data['buyers'])
            total_compras = data['count'] + data['window_count']
            if unique_buyers_count >= threshold and contract not in self.notified_contracts:
                self.notified_contracts.add(contract)
                return True, total_compras, threshold, "threshold_reached"
            
            return False, total_compras, threshold, "window_started"

# Instância global do monitor
monitor = ContractMonitor()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    # Verifica grupo de monitoramento
    if config.GRUPO_MONITORAMENTO and str(update.effective_chat.id) != config.GRUPO_MONITORAMENTO:
        return
    
    text = update.message.text
    group_id = update.effective_chat.id
    
    # Extrai informações do contrato
    token_name, contract_address, buyer_name = monitor.extract_contract_info(text)
    
    if not token_name or not contract_address:
        return
    
    # Adiciona compra e verifica notificação
    should_notify, count, threshold, window_status = monitor.add_purchase(contract_address, group_id, buyer_name)
    
    # Se não deve notificar, retorna
    if not should_notify:
        return
    
    if should_notify:
        # Determina onde enviar
        notification_chat_id = config.GRUPO_NOTIFICACAO if config.GRUPO_NOTIFICACAO else group_id
        
        # Busca a lista de compradores do contrato
        buyers_list = monitor.contract_counts[contract_address]['buyers']
        buyers_text = ""
        if buyers_list:
            buyers_text = "\n" + "\n".join([f"🔹{buyer}" for buyer in buyers_list]) + "\n"
        
        notification_text = (
            f"🚨 **ALERTA DE VOLUME DE COMPRAS** 🚨{buyers_text}"
            f"**Token:** {token_name}\n"
            f"**Compras detectadas:** {count}\n"
            f"**Threshold atingido:** {threshold}\n"
            f"`{contract_address}`"
        )
        
        try:
            await context.bot.send_message(
                chat_id=notification_chat_id,
                text=notification_text,
                parse_mode='Markdown'
            )
            logger.info(f"Alerta enviado: {token_name} - {count} compras")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            await update.message.reply_text(notification_text, parse_mode='Markdown')

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    group_id = update.effective_chat.id
    settings = monitor.group_settings[group_id]
    monitor.reset_old_counts()
    
    grupo_monitor = config.GRUPO_MONITORAMENTO if config.GRUPO_MONITORAMENTO else "Todos os grupos"
    grupo_notif = config.GRUPO_NOTIFICACAO if config.GRUPO_NOTIFICACAO else "Mesmo grupo"
    
    status_text = f"""
📊 **STATUS DO MONITOR**

🔍 **Grupos:**
• Monitoramento: `{grupo_monitor}`
• Notificações: `{grupo_notif}`

⚙️ **Configurações:**
• Threshold: {settings['threshold']} compradores únicos
• Status: {'✅ Ativo' if settings['enabled'] else '❌ Inativo'}
• Janela: {config.COOLDOWN_COMPRAS} segundos

📈 **Contratos Ativos:**
"""
    
    if not monitor.contract_counts:
        status_text += "• Nenhum contrato monitorado"
    else:
        for contract, data in monitor.contract_counts.items():
            if data['window_active']:
                time_left = config.COOLDOWN_COMPRAS - (datetime.now() - data['window_start']).total_seconds()
                status_text += f"• `{contract[:15]}...`: {data['count']} total | Janela: {data['window_count']} ({time_left:.0f}s)\n"
            else:
                status_text += f"• `{contract[:15]}...`: {data['count']} compras\n"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def cmd_grupoid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title or "Chat Privado"
    
    info_text = f"""
🆔 **ID DO GRUPO**

📱 **ID:** `{group_id}`
📋 **Tipo:** {chat_type}
🏷️ **Nome:** {chat_title}

💡 **Configuração:**
• Monitoramento: `GRUPO_MONITORAMENTO={group_id}`
• Notificação: `GRUPO_NOTIFICACAO={group_id}`
"""
    
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def cmd_setthreshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(f"Uso: `/setthreshold [número]`\nAtual: {config.THRESHOLD_COMPRAS} compradores únicos", parse_mode='Markdown')
        return
    
    try:
        new_threshold = int(context.args[0])
        if new_threshold <= 0:
            raise ValueError()
        
        group_id = update.effective_chat.id
        monitor.group_settings[group_id]['threshold'] = new_threshold
        
        await update.message.reply_text(f"✅ Threshold: **{new_threshold}** compradores únicos", parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Número inválido.")

async def cmd_setcooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMIN_IDS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(f"Uso: `/setcooldown [segundos]`\nAtual: {config.COOLDOWN_COMPRAS}s", parse_mode='Markdown')
        return
    
    try:
        new_cooldown = int(context.args[0])
        if new_cooldown < 0:
            raise ValueError()
        
        config.COOLDOWN_COMPRAS = new_cooldown
        await update.message.reply_text(f"✅ Janela: **{new_cooldown}** segundos", parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text("❌ Número inválido.")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 **BOT MONITOR DE COMPRAS**

**Comandos:**
• `/help` - Esta ajuda
• `/grupoid` - ID do grupo atual

**Administradores:**
• `/status` - Status do monitor
• `/setthreshold [número]` - Define threshold
• `/setcooldown [segundos]` - Define janela temporal

**Funcionamento:**
• Monitora mensagens "🟢 BUY"
• Conta compradores únicos por contrato
• Notifica quando atinge threshold de compradores únicos
• Reset automático após 1 hora
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Erro: {context.error}")

def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN não configurado!")
        return
    
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("setthreshold", cmd_setthreshold))
    app.add_handler(CommandHandler("setcooldown", cmd_setcooldown))
    app.add_handler(CommandHandler("grupoid", cmd_grupoid))
    app.add_handler(CommandHandler("id", cmd_grupoid))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("Bot iniciado - Monitorando compras...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()