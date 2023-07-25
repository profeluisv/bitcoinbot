# Importaciones estándar
import datetime
import json
import os
import threading

# Importaciones de terceros
import asyncio
import cryptocompare
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import pandas as pd
import plotly.graph_objects as go
import pytz
from pytz import timezone
from PIL import Image
import qrcode
import re
import requests
import telebot
from telebot import types
from tabulate import tabulate

# Otras importaciones
from datetime import datetime
import html
import io
import markdown
import tempfile
from io import BytesIO
from prettytable import PrettyTable
import time
import schedule

# Configurar el bot de Telegram (JarvisBTC)
bot_token = os.getenv('BOT_TOKEN')

# Crear instancia del bot
bot = telebot.TeleBot(bot_token)

# Variables globales
crypto_data = []  # Almacenar los datos de las criptomonedas
current_page = 1  # Página actual de la tabla

# Bloques del código para comenzar y enviar mensaje de Bienvenida

# Función que maneja el comando /start
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    # Mensaje de bienvenida mejorado usando copywriting
    welcome_message = f'Hola {user.first_name} 👋 ¡Soy BitcoinBot y te doy la bienvenida! 🤖🚀\n\n'
    welcome_message += 'Descubre el potencial de Bitcoin y el mercado de criptomonedas con 1 MES GRATIS de todas las funciones sin publicidad. ¡Genial! 🌟 ¡Únete ahora! 💰\n\n'
    welcome_message += 'Ejecuta los siguientes comandos para comenzar:\n\n'

    # Menú principal
    welcome_message += '📋 <b>Inicio:</b>\n\n'
    welcome_message += '/menu - Accede al menú principal.\n'
    welcome_message += '/pro - Todas las funciones sin publicidad.\n\n'

    # Indicadores financieros
    welcome_message += '💹 <b>Indicadores financieros:</b>\n\n'
    welcome_message += '/p - Precio por criptomoneda.\n'
    welcome_message += '/top10 - Precio del top 10 criptomonedas.\n\n'

    # Estadísticas de la blockchain de Bitcoin
    welcome_message += '🔗 <b>Estadísticas de Bitcoin:</b>\n\n'
    welcome_message += '/oa - Análisis on-chain de la red.\n\n'

    # Gráficos e indicadores de análisis técnico
    welcome_message += '📈 <b>Gráficos e indicadores:</b>\n\n'
    welcome_message += '/g - Gráfico de precio.\n'
    welcome_message += '/vol - Gráfico de volumen.\n'
    welcome_message += '/sma - Gráfico Medias Móviles Simples.\n'
    welcome_message += '/bb - Indicador Bollinger Bands.\n'
    welcome_message += '/rsi - Indicador RSI.\n'
    welcome_message += '/macd - Indicador MACD.\n\n'

    # Actualidad y noticias
    welcome_message += '📰 <b>Actualidad:</b>\n\n'
    welcome_message += '/n - Noticias de último minuto.\n\n'

    # Tienda y recursos adicionales
    welcome_message += '🛍️ <b>Tienda:</b>\n\n'
    welcome_message += '/shop - Descuentos, ofertas, recursos, consultas.\n\n'

    # Cierre del mensaje
    welcome_message += '¡Explora todas las opciones y disfruta de Bitcoin y el mundo de las criptomonedas ! Si necesitas ayuda, no dudes en contactarnos @profeluisv. ¡Éxito en tus inversiones! 🚀💰'

    bot.reply_to(message, welcome_message, parse_mode='HTML')

    # Agregar chat_id a la lista de usuarios que han iniciado el comando /start
    add_user_with_start_command(message.chat.id)

    # Agregar chat_id a la "versión pro" durante 1 minuto
    add_to_active_pro_users(message.chat.id, duration)

# Función que maneja el comando /menu
@bot.message_handler(commands=['menu'])
def menu(message):
    # Simplemente llamamos a la función start() que ya contiene el mensaje que queremos enviar.
    start(message)

# Función que maneja el comando /shop
@bot.message_handler(commands=['shop'])
def shop(message):
    chat_id = message.chat.id  # Obtener el ID del chat

    # Mensaje con el enlace al sitio web
    shop_message = '🛍️ ¡Bienvenido a nuestra tienda online!\n\n'
    shop_message += 'Encontrarás todo lo necesario para comenzar a participar en Bitcoin, DeFi, NFT y cyberseguridad.\n'
    shop_message += 'Visítanos [Aquí](https://beacons.ai/bitcoinbot)'

    bot.send_message(chat_id, shop_message, parse_mode='Markdown', disable_web_page_preview=True)

# Bloques del código para enviar mensaje de PRECIOS DEL TOP 10 CRIPTOMONEDAS

# URL de la API CoinGecko para obtener los datos de las criptomonedas
API_URL = 'https://api.coingecko.com/api/v3/coins/markets'

# Parámetros de la API
PARAMS = {
    'vs_currency': 'usd',
    'per_page': 10,  # Mostrar 10 criptomonedas por página
}

# Función que maneja el comando /top10
@bot.message_handler(commands=['top10'])
def handle_pm_command(message):
    chat_id = message.chat.id

    # Obtener los datos de las criptomonedas y enviar la tabla
    get_crypto_data(page=current_page)
    table = generate_table(crypto_data)
    send_table_message(chat_id, table)

    # Enviar el enlace en otro mensaje
    send_link_message(chat_id)

def get_crypto_data(page):
    # Actualizar los parámetros de la API con la página actual
    PARAMS['page'] = page

    # Realizar la solicitud GET a la API CoinGecko
    response = requests.get(API_URL, params=PARAMS)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtener los datos de las criptomonedas desde la respuesta JSON
        global crypto_data
        crypto_data = []
        for i, crypto in enumerate(response.json()):
            rank = i + 1
            symbol = crypto['symbol'].upper()
            price = crypto['current_price']
            percent_change = crypto['price_change_percentage_24h']
            crypto_data.append({'#': rank, 'Cripto': symbol, 'Precio': price, '24h%': percent_change})

def generate_table(crypto_data):
    headers = ['#', 'Cripto', 'Precio', '24h%']
    rows = []

    for crypto in crypto_data:
        rank = str(crypto['#'])
        symbol = crypto['Cripto']
        price_str = '${:,.2f}'.format(crypto['Precio'])
        percent_change = '{:.2f}%'.format(crypto['24h%'])
        row = [rank, symbol, price_str, percent_change]
        rows.append(row)

    # Ajustar los espacios entre las columnas
    table = tabulate(rows, headers, tablefmt='plain', numalign='left')

    return table

def update_table(chat_id):
    if crypto_data:
        table = generate_table(crypto_data)
        send_message(chat_id, table)
    else:
        error_message = "Lo siento, no pude obtener los datos de mercado. Por favor, intenta nuevamente más tarde."
        bot.send_message(chat_id=chat_id, text=error_message)

# Bloques del código para enviar mensaje de ONCHIAN ANALYSIS

# Función que maneja el comando /oa
@bot.message_handler(commands=['oa'])
def onchain_analysis(message):
    chat_id = message.chat.id  # Obtener el ID del chat
    indicators = get_onchain_data()  # Obtener los indicadores on-chain de la blockchain de Bitcoin
    if indicators:
        message = create_message(indicators)  # Crear el mensaje con los indicadores en formato Markdown
        send_table_message(chat_id, message)  # Enviar el mensaje al chat_id con la tabla formateada en Markdown
        send_link_message(chat_id)  # Enviar el link después de la tabla
    else:
        error_message = "No se pudieron obtener los indicadores on-chain."
        bot.send_message(chat_id=chat_id, text=error_message)

# Función para obtener los datos de la blockchain de Bitcoin
def get_onchain_data():
    url = "https://api.blockchain.info/stats"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        indicators = {
            'Precio de Mercado (USD)': data['market_price_usd'],
            'Tasa de Hash': data['hash_rate'],
            'Total de Comisiones (BTC)': data['total_fees_btc'],
            'Total de Bitcoins Minados': data['n_btc_mined'],
            'Número de Transacciones': data['n_tx'],
            'Número de Bloques Minados': data['n_blocks_mined'],
            'Minutos entre Bloques': data['minutes_between_blocks'],
            'Total de Bitcoins en Circulación': data['totalbc'],
            'Número Total de Bloques': data['n_blocks_total'],
            'Volumen de Transacciones Estimado (USD)': data['estimated_transaction_volume_usd'],
            'Tamaño de los Bloques (KBytes)': data['blocks_size'],
            'Ingresos de los Mineros (USD)': data['miners_revenue_usd'],
            'Próximo Ajuste de Dificultad': data['nextretarget'],
            'Dificultad Actual': data['difficulty'],
            'Bitcoin Enviados Estimados (BTC)': data['estimated_btc_sent'],
            'Ingresos de los Mineros (BTC)': data['miners_revenue_btc'],
            'Total de Bitcoins Enviados': data['total_btc_sent'],
            'Vol. de Transacciones (BTC)': data['trade_volume_btc'],
            'Vol. de Transacciones (USD)': data['trade_volume_usd'],
        }
        return indicators
    else:
        return None

# Función para crear el mensaje con los indicadores en formato Markdown
def create_message(indicators):
    message = ""

    # Agregar las estadísticas de mercado
    message += "Estadísticas de mercado\n\n"
    message += f"Precio de Bitcoin: {'$' + str(indicators['Precio de Mercado (USD)']):>14}\n"
    capitalizacion = indicators['Precio de Mercado (USD)'] * indicators['Total de Bitcoins en Circulación'] / 1000000000
    message += f"Cap. de mercado (B): {'$' + str(round(capitalizacion / 100000000, 2)):>12}\n"
    message += f"Volumen (BTC): {str(indicators['Vol. de Transacciones (BTC)']):>18}\n\n"

    # Agregar las estadísticas de la blockchain
    message += "Estadísticas de la blockchain\n\n"
    message += f"Número total de bloques: {str(indicators['Número Total de Bloques']):>8}\n"
    message += f"Minutos entre bloques: {str(round(indicators['Minutos entre Bloques'], 2)):>10}\n"
    message += f"Total Bitcoin: {str(round(indicators['Total de Bitcoins en Circulación'] / 100000000, 2)):>18}\n\n"

    # Agregar las estadísticas de minado y ajuste de dificultad
    message += "Estadísticas de minado y ajuste de dificultad\n\n"
    message += f"Tasa de Hash (Ehash/s): {str(round(indicators['Tasa de Hash'] / 1000000000, 2)):>9}\n"
    message += f"Dificultad actual (T): {str(round(indicators['Dificultad Actual'] / 1000000000000, 2)):>10}\n"

    return message

# Bloques del código para enviar las TABLAS DE DATOS

# Define una función para enviar la tabla al chat_id especificado sin enlaces publicitarios para usuarios de la "versión pro"
def send_table_message(chat_id, table):
    if not has_paid_pro_version(chat_id):
        # Si el usuario no ha pagado, enviar la tabla con el enlace publicitario
        formatted_table = f'```\n{table}\n```'
        bot.send_message(chat_id=chat_id, text=formatted_table, parse_mode='Markdown')
    else:
        # Si el usuario ha pagado, enviar la tabla sin el enlace publicitario
        formatted_table = f'```\n{table}\n```'
        bot.send_message(chat_id=chat_id, text=formatted_table, parse_mode='Markdown')
        send_link_message(chat_id)

# Define una función para enviar el enlace sin enlaces publicitarios para usuarios de la "versión pro"
def send_link_message(chat_id):
    if not has_paid_pro_version(chat_id):
        link = 'Más herramientas: [Aquí](https://beacons.ai/bitcoinbot) 🔥'
        bot.send_message(chat_id=chat_id, text=link, parse_mode='Markdown', disable_web_page_preview=True)

# Define una función para enviar la imagen del código QR de la dirección de pago de Bitcoin
def send_qr_code(chat_id):
    if not has_paid_pro_version(chat_id):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(PRO_VERSION_ADDRESS)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Enviar la imagen del código QR con la dirección de Bitcoin
        bot.send_photo(chat_id, photo=img_buffer)

        # Enviar los mensajes de instrucciones
        bot.send_message(chat_id, "Para disfrutar por un año de todas las funciones de BitcoinBot, sin anuncios publicitarios, por favor realiza un pago de 0.0004 BTC a la dirección:")
        bot.send_message(chat_id, "12 meses = 0.0004 BTC")
        bot.send_message(chat_id, PRO_VERSION_ADDRESS)
        bot.send_message(chat_id, "Una vez que hayas realizado el pago, espera un momento para que se verifique y puedas disfrutar de la versión pro.\n\nVendrán más funciones, si tienes una idea para una que necesites o algún requerimiento envíanos un mensaje directo @profeluisv")

# Función que maneja el comando /pro
@bot.message_handler(commands=['pro'])
def handle_pro_command(message):
    chat_id = message.chat.id
    if not has_paid_pro_version(chat_id):
        # Si el usuario no ha pagado, enviar la imagen del código QR primero
        send_qr_code(chat_id)
    else:
        # Si el usuario ha pagado, enviar el mensaje de acceso a la versión pro
        bot.send_message(chat_id, "¡Bienvenido a la versión pro! Ahora tienes acceso completo a todas las funciones.")
        send_link_message(chat_id)

# Bloques del código para enviar los GRAFICOS

# Función que maneja el comando /'g', 'vol', 'sma', 'bb', 'rsi', 'macd'
@bot.message_handler(commands=['g', 'vol', 'sma', 'bb', 'rsi', 'macd'])
def handle_commands(message):
    chat_id = message.chat.id
    command = message.text.split(' ')
    valid_commands = ['/g', '/vol', '/sma', '/bb', '/rsi', '/macd']

    # Verificar si se proporcionó el símbolo de la criptomoneda después del comando
    if len(command) == 2 and command[0] in valid_commands:
        symbol = command[1].upper()

        # Verificar si es un comando restringido
        if command[0] in ['/vol', '/bb', '/rsi', '/macd']:
            if not has_paid_pro_version(chat_id):
                # Si el usuario no ha pagado, enviar el mensaje para realizar el pago
                bot.send_message(chat_id, "Necesitas la cuenta /pro para tener acceso a esa función.")
                return

        try:
            graph_info = get_price_chart(symbol, command[0][1:], chat_id)
            if graph_info.get('image_bytes'):
                img_buffer = io.BytesIO(graph_info['image_bytes'])
                bot.send_photo(chat_id, img_buffer, caption=graph_info.get('link', None))
            elif graph_info.get('link'):
                bot.send_message(chat_id, graph_info['link'])
        except Exception as e:
            error_message = f"No se pudo obtener el gráfico de precios para {symbol}. Por favor, verifica el código e intenta nuevamente."
            bot.send_message(chat_id, error_message)
    else:
        # Si no se proporcionó el símbolo o el comando es inválido, mostrar un mensaje de ayuda específico
        if len(command) == 1 and command[0] in valid_commands:
            help_message = f"Por favor, ingresa el código de la criptomoneda después del comando. Por ejemplo, {command[0]} btc"
        else:
            help_message = "Comando inválido. Por favor, utiliza uno de los siguientes comandos:\n" + "\n".join(valid_commands)
        bot.send_message(chat_id, help_message)

# Función para obtener los datos de precios y generar el gráfico
def get_price_chart(symbol, indicator, chat_id):
    data = cryptocompare.get_historical_price_minute(symbol, currency='USD', limit=4 * 24 * 12)
    if data:
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        df.set_index('time', inplace=True)

        plt.style.use('dark_background')

        if indicator == 'g':
            plt.plot(df.index, df['close'], color='orange', label='Precio de cierre')
            plt.xlabel('Hora', color='white')
            plt.ylabel('Precio', color='white')
            plt.title(f'Gráfico del precio de {symbol} (Diario)', color='white')
            plt.legend()
        elif indicator == 'vol':
            df['volume'] = df['volumeto'] - df['volumefrom']
            plt.plot(df.index, df['volume'], color='cyan', label='Volumen')
            plt.xlabel('Hora', color='white')
            plt.ylabel('Volumen', color='white')
            plt.title(f'Gráfico de volumen de {symbol} (Diario)', color='white')
            plt.legend(loc='upper left')
        elif indicator == 'sma':
            df['sma_100'] = df['close'].rolling(window=100).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            plt.plot(df.index, df['close'], color='orange', label='Precio de cierre')
            plt.plot(df.index, df['sma_100'], color='cyan', label='SMA 100')
            plt.plot(df.index, df['sma_200'], color='magenta', label='SMA 200')
            plt.xlabel('Hora', color='white')
            plt.ylabel('Precio', color='white')
            plt.title(f'Gráfico del precio y medias móviles de {symbol} (Diario)', color='white')
            plt.legend()
        elif indicator == 'bb':
            window = 100
            df['sma'] = df['close'].rolling(window=window).mean()
            df['std'] = df['close'].rolling(window=window).std()
            df['upper_band'] = df['sma'] + 3 * df['std']
            df['lower_band'] = df['sma'] - 3 * df['std']
            plt.plot(df.index, df['close'], color='orange', label='Precio de cierre')
            plt.plot(df.index, df['sma'], color='cyan', label='SMA')
            plt.plot(df.index, df['upper_band'], color='magenta', label='Banda superior')
            plt.plot(df.index, df['lower_band'], color='lime', label='Banda inferior')
            plt.fill_between(df.index, df['upper_band'], df['lower_band'], color='gray', alpha=0.3)
            plt.xlabel('Hora', color='white')
            plt.ylabel('Precio', color='white')
            plt.title(f'Gráfico del precio y Bollinger Bands de {symbol} (Diario)', color='white')
            plt.legend()
        elif indicator == 'rsi':
            df['delta'] = df['close'].diff()
            df['gain'] = df['delta'].apply(lambda x: x if x > 0 else 0)
            df['loss'] = df['delta'].apply(lambda x: abs(x) if x < 0 else 0)
            df['avg_gain'] = df['gain'].rolling(window=30).mean()
            df['avg_loss'] = df['loss'].rolling(window=30).mean()
            df['rs'] = df['avg_gain'] / df['avg_loss']
            df['rsi'] = 100 - (100 / (1 + df['rs']))
            fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            ax1.plot(df.index, df['close'], color='orange', label='Precio de cierre')
            ax1.set_ylabel('Precio', color='white')
            ax1.tick_params(axis='y', colors='white')
            ax1.spines['bottom'].set_visible(False)
            ax1.spines['left'].set_color('white')
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.legend()
            ax2.plot(df.index, df['rsi'], color='cyan', label='RSI')
            ax2.axhline(70, color='magenta', linestyle='--', alpha=0.5)
            ax2.axhline(30, color='magenta', linestyle='--', alpha=0.5)
            ax2.set_xlabel('Hora', color='white')
            ax2.set_ylabel('RSI', color='white')
            ax2.tick_params(axis='x', colors='white')
            ax2.tick_params(axis='y', colors='white')
            ax2.spines['bottom'].set_color('white')
            ax2.spines['left'].set_color('white')
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.legend(loc='upper left')
            plt.suptitle(f'Gráfico del precio y RSI de {symbol} (Diario)', color='white')
        elif indicator == 'macd':
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            ax1.plot(df.index, df['close'], color='orange', label='Precio de cierre')
            ax1.set_ylabel('Precio', color='white')
            ax1.tick_params(axis='y', colors='white')
            ax1.spines['bottom'].set_visible(False)
            ax1.spines['left'].set_color('white')
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.legend()
            ax2.plot(df.index, df['macd'], color='cyan', label='MACD')
            ax2.plot(df.index, df['signal'], color='magenta', label='Señal')
            ax2.axhline(0, color='orange', linestyle='-', alpha=0.5)
            ax2.set_xlabel('Hora', color='white')
            ax2.set_ylabel('MACD', color='white')
            ax2.tick_params(axis='x', colors='white')
            ax2.tick_params(axis='y', colors='white')
            ax2.spines['bottom'].set_color('white')
            ax2.spines['left'].set_color('white')
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.legend(loc='upper left')
            plt.suptitle(f'Gráfico del precio y MACD de {symbol} (Diario)', color='white')

        # Desactivar notación científica en el eje y del gráfico de volumen
        plt.ticklabel_format(style='plain', axis='y')

        # Código para personalizar las etiquetas del eje x para mostrar solo las fechas correspondientes al cambio de un día
        locator = mdates.AutoDateLocator(maxticks=8)  # Configurar el número máximo de etiquetas en el eje x
        formatter = mdates.ConciseDateFormatter(locator)  # Utilizar el formateador ConciseDateFormatter
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.tight_layout()

        # Crear un objeto BytesIO para almacenar temporalmente el gráfico
        image_bytes_io = io.BytesIO()

        # Guardar el gráfico en el objeto BytesIO
        plt.savefig(image_bytes_io, format='png')
        plt.close()

        # Obtener el contenido en bytes del objeto BytesIO
        image_bytes = image_bytes_io.getvalue()

        # Si el usuario no ha pagado, crear y enviar el archivo de enlace
        if not has_paid_pro_version(chat_id):
            link = 'Más información aquí: https://beacons.ai/bitcoinbot'
            return {"image_bytes": image_bytes, "link": link}
        else:
            # Devolver solo el contenido en bytes del gráfico para usuarios pro
            return {"image_bytes": image_bytes}

    else:
        raise Exception("No se encontraron datos de precios para la criptomoneda")

# Bloques del código para enviar mensaje de NOTICIAS

# Fuente de noticias para el bot de Telegram
def get_bitcoin_news():
    url = 'https://min-api.cryptocompare.com/data/v2/news/?lang=ES&categories=BTC'
    response = requests.get(url)
    news_data = response.json()
    if 'Data' in news_data:
        return news_data['Data']
    else:
        return []

# Función que maneja el comando /n
@bot.message_handler(commands=['n'])
def send_news(message):
    chat_id = message.chat.id  # Obtener el ID del chat

    news_data = get_bitcoin_news()

    if news_data:

        # Tomar la última noticia del día
        latest_news = news_data[:3]

        for news in latest_news:
            title = news['title']
            url = news['url']
            if not has_paid_pro_version(chat_id):
                link = 'Más herramientas: [Aquí](https://beacons.ai/bitcoinbot) 🔥'
                message = f'{title}\n{url}\n\n{link}'
            else:
                message = f'{title}\n{url}'
            bot.send_message(chat_id, message, parse_mode='Markdown', disable_web_page_preview=False)
    else:
        bot.send_message(chat_id, 'No hay noticias disponibles')

# Bloques del código de pago en Bitcoin para la "VERSION PRO"

# Dirección Bitcoin fija para recibir pagos de la "versión pro"
PRO_VERSION_ADDRESS = "bc1qng7ja8xvmrta54307adut0a5gtegjfxy8fa5vc"

# Monto requerido para la "versión pro" (en BTC, por ejemplo, 0.0004 BTC)
REQUIRED_AMOUNT_BTC = 0.0004

# Duración de la "versión pro" en segundos (365 días en este ejemplo)
PRO_VERSION_DURATION = 365 * 24 * 60 * 60

# Duración del tiempo en segundos para nuevos usuarios (por defecto, 1 mes = 2592000)
duration = 2592000

# Estructura para mantener un registro de usuarios activos en la "versión pro"
# Cada elemento es un diccionario con el chat_id del usuario y su fecha de activación (timestamp)
active_pro_users = []

# Lista de chat_id de usuarios que han iniciado el comando /start
users_with_start_command = []

# Lista de chat_id de usuarios a agregar manualmente a la "versión pro" (Mi ID 5488206180)
users_to_add = [5488206180, 987654321, 555555555, 123456789]

# Función para agregar chat_id a la lista de usuarios que han iniciado el comando /start
def add_user_with_start_command(chat_id):
    if chat_id not in users_with_start_command:
        users_with_start_command.append(chat_id)

# Función para agregar chat_id a la lista de usuarios activos en la "versión pro" durante la duración especificada
def add_to_active_pro_users(chat_id, duration):
    if chat_id not in [user["chat_id"] for user in active_pro_users]:
        manually_enable_pro_version(chat_id)
        threading.Timer(duration, remove_from_active_pro_users, args=[chat_id]).start()

# Función para eliminar chat_id de la lista de usuarios activos en la "versión pro"
def remove_from_active_pro_users(chat_id):
    global active_pro_users
    active_pro_users = [user for user in active_pro_users if user["chat_id"] != chat_id]

# Función para enviar un mensaje personalizado al usuario una vez que su pago ha sido verificado
def send_payment_confirmation_message(chat_id):
    confirmation_message = "¡Gracias por tu pago! Ahora tienes acceso a la versión pro de BitcoinBot y todas sus funciones. ¡Disfrútalo!"
    bot.send_message(chat_id, confirmation_message)

# Función para verificar si un usuario ha realizado el pago y tiene acceso a la "versión pro"
def has_paid_pro_version(chat_id):
    # Verificar si el usuario está en la lista de usuarios activos
    for user in active_pro_users:
        if user["chat_id"] == chat_id:
            # Si el usuario está en la lista, siempre considerarlo como usuario de la "versión pro"
            return True

    # Si el usuario no está en la lista de usuarios activos, verificar el pago normalmente
    url = f"https://blockchain.info/rawaddr/{PRO_VERSION_ADDRESS}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for tx in data["txs"]:
            for output in tx["out"]:
                if output["addr"] == PRO_VERSION_ADDRESS and output["value"] >= REQUIRED_AMOUNT_BTC * 1e8:
                    # Si el pago es válido, agregar al usuario a la lista de usuarios activos y establecer la fecha de activación
                    user_data = {
                        "chat_id": chat_id,
                        "activation_date": time.time()
                    }
                    active_pro_users.append(user_data)
                    # Enviar mensaje de confirmación al usuario una vez que el pago ha sido verificado
                    send_payment_confirmation_message(chat_id)
                    return True

    return False

# Función para agregar manualmente a un usuario a la "versión pro"
def manually_enable_pro_version(chat_id):
    user_data = {
        "chat_id": chat_id,
        "activation_date": time.time()
    }
    active_pro_users.append(user_data)

# Iterar sobre la lista de usuarios y agregarlos manualmente a la "versión pro"
for chat_id in users_to_add:
    manually_enable_pro_version(chat_id)

# Bloques del código para enviar mensaje de PRECIOS POR CRIPTOMONEDAS

# Función que maneja el comando /p
@bot.message_handler(commands=['p'])
def handle_precio_command(message):
    chat_id = message.chat.id
    command = message.text.split(' ')
    if len(command) > 1:
        symbol = command[1].upper()
        try:
            data_table = get_daily_price(symbol)
            send_table_message(chat_id, data_table)

            # Enviar el enlace después de la tabla
            send_link_message(chat_id)
        except Exception as e:
            error_message = f"Lo siento, no pude obtener el precio de {symbol}. Por favor, verifica el código e intenta nuevamente."
            send_message(chat_id, error_message)
    else:
        message = "Por favor, ingresa el código de la criptomoneda después del comando /p. Por ejemplo, /p btc"
        send_message(chat_id, message)

def format_number(number):
    return '{:,.2f}'.format(number)

def format_volume(volume):
    # Formatear el volumen usando el prefijo adecuado (K, M, B, etc.)
    prefixes = ['', 'K', 'M', 'B', 'T']
    prefix_index = 0

    while volume >= 1000 and prefix_index < len(prefixes) - 1:
        volume /= 1000
        prefix_index += 1

    return f'{volume:.2f} {prefixes[prefix_index]}'

def send_message(chat_id, message):
    bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def get_daily_price(symbol):
    # Obtener los datos históricos de los últimos 365 días para el símbolo especificado
    ohlcv = cryptocompare.get_historical_price_day(symbol, currency='USDT', limit=730)

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(ohlcv)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    # Obtener los datos del último día
    today = df.iloc[-1]
    yesterday = df.iloc[-2]
    last_7_days = df.iloc[-7:]
    last_30_days = df.iloc[-30:]
    last_365_days = df.iloc[-365:]

    # Calcular la variación en valor y porcentaje
    price_change_24h = today['close'] - yesterday['close']
    price_change_7d = today['close'] - last_7_days.iloc[0]['close']
    price_change_1M = today['close'] - last_30_days.iloc[0]['close']
    price_change_1a = today['close'] - last_365_days.iloc[0]['close']

    percent_change_24h = (price_change_24h / yesterday['close']) * 100
    percent_change_7d = (price_change_7d / last_7_days.iloc[0]['close']) * 100
    percent_change_1M = (price_change_1M / last_30_days.iloc[0]['close']) * 100
    percent_change_1a = (price_change_1a / last_365_days.iloc[0]['close']) * 100

    # Formatear los valores
    price = format_number(today['close'])
    high = format_number(today['high'])
    low = format_number(today['low'])
    volume = today['volumefrom'] * today['close']  # Multiplicar por el precio de cierre

    # Formatear el volumen usando la nueva función
    formatted_volume = format_volume(volume)

    # Obtener el emoji correspondiente a la variación porcentual
    if percent_change_24h > 5:
        emoji_24h = "😀"
    elif percent_change_24h > 1:
        emoji_24h = "😊"
    else:
        emoji_24h = "😕"

    if percent_change_7d > 5:
        emoji_7d = "😀"
    elif percent_change_7d > 1:
        emoji_7d = "😊"
    else:
        emoji_7d = "😕"

    if percent_change_1M > 5:
        emoji_1M = "😀"
    elif percent_change_1M > 1:
        emoji_1M = "😊"
    else:
        emoji_1M = "😕"

    if percent_change_1a > 5:
        emoji_1a = "😀"
    elif percent_change_1a > 1:
        emoji_1a = "😊"
    else:
        emoji_1a = "😕"

    # Crear el mensaje con los datos del último día
    message = f'{symbol} ${price}\n'
    message += f'H|L: ${high}|${low}\n'
    message += f'24h    {percent_change_24h:.2f}%   {emoji_24h}\n'
    message += f'7d     {percent_change_7d:.2f}%   {emoji_7d}\n'
    message += f'1m     {percent_change_1M:.2f}%   {emoji_1M}\n'
    message += f'1a     {percent_change_1a:.2f}%   {emoji_1a}\n'
    message += f'Vol: ${formatted_volume}\n'  # Utilizar el volumen formateado

    # Escapar caracteres especiales de Markdown
    message = message.replace('*', '\\*').replace('_', '\\_').replace('<', '\\<').replace('>', '\\>').replace('`', '\\`')

    return message

# Iniciar el bot de Telegram con polling infinito
bot.infinity_polling()
