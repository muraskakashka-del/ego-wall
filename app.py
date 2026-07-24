import os
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# База данных в памяти (Имя Короля, Его ссылка, Цена трона)
king_data = {
    "name": "💎 ТВОЙ НИК (АДМИН) 💎",
    "link": "https://telegram.org",
    "price": 100.00  # Цена в сомах (KGS)
}

# ВПИШИ СЮДА СВОЙ НОМЕР ТЕЛЕФОНА О! ДЛЯ ПОПОЛНЕНИЯ БАЛАНСА
MY_PHONE_NUMBER = "0708333334" 

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE EGO WALL | СТЕНА ЭГОИСТА</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            background: radial-gradient(circle at center, #1a0033 0%, #050010 100%); 
            color: #ffffff; 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px;
        }
        .main-card { 
            background: rgba(15, 10, 30, 0.85); border: 2px solid #ff007f; border-radius: 24px; 
            padding: 40px 30px; max-width: 480px; width: 100%; text-align: center; 
            box-shadow: 0 0 40px rgba(255, 0, 127, 0.25); backdrop-filter: blur(10px);
        }
        h1 { 
            font-size: 32px; font-weight: 900; letter-spacing: 2px;
            background: linear-gradient(45deg, #ff007f, #00ffff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-transform: uppercase; margin-bottom: 10px;
        }
        .subtitle { color: #8a85a0; font-size: 14px; margin-bottom: 35px; text-transform: uppercase; }
        .throne-room { 
            background: linear-gradient(145deg, #160d29, #0a0418); border: 1px solid rgba(255, 215, 0, 0.3);
            padding: 25px; border-radius: 18px; margin-bottom: 35px; position: relative;
        }
        .throne-room::after {
            content: '👑 ТЕКУЩИЙ КОРОЛЬ'; position: absolute; top: -11px; left: 50%; transform: translateX(-50%);
            background: #ffd700; color: #000; font-size: 11px; font-weight: bold; padding: 2px 14px; border-radius: 20px;
        }
        .king-link { 
            display: inline-block; font-size: 26px; font-weight: 800; color: #00ffff; 
            text-decoration: none; margin: 15px 0 10px 0; text-shadow: 0 0 12px rgba(0, 255, 255, 0.6);
        }
        .price-tag { font-size: 15px; color: #a5a1b8; }
        .price-amount { color: #ffd700; font-weight: 700; font-size: 18px; }
        input { 
            width: 100%; padding: 15px 20px; margin-bottom: 15px; background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; font-size: 15px; 
        }
        .neon-btn { 
            width: 100%; padding: 18px; background: linear-gradient(90deg, #ff007f, #7928ca);
            color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 800; 
            text-transform: uppercase; cursor: pointer; box-shadow: 0 4px 20px rgba(255, 0, 127, 0.4);
        }
        .instruction-box {
            background: rgba(255, 0, 127, 0.1); border: 1px dashed #ff007f;
            padding: 15px; border-radius: 12px; margin-top: 20px; text-align: left; font-size: 14px;
        }
        .instruction-box b { color: #00ffff; }
    </style>
</head>
<body>

    <div class="main-card">
        <h1>The Ego Wall</h1>
        <div class="subtitle">Стена твоего превосходства</div>
        
        <div class="throne-room">
            <a href="{{ king.link }}" class="king-link" target="_blank">{{ king.name }}</a>
            <div class="price-tag">Место выкуплено за <span class="price-amount">{{ king.price }} KGS</span></div>
        </div>

        <form action="/buy" method="POST">
            <input type="text" name="username" placeholder="Твое имя / Никнейм" required maxlength="30">
            <input type="url" name="userlink" placeholder="Ссылка на твой ТГ (https://...)" required>
            
            <button type="submit" class="neon-btn">
                Занять стену за {{ king.price + 50.0 }} KGS
            </button>
        </form>

        {% if show_instruction %}
        <div class="instruction-box">
            🚀 <b>ШАГ ДО ПОБЕДЫ!</b><br>
            Чтобы твое имя появилось на стене, переведи ровно <b>{{ pending_price }} KGS</b> на мобильный баланс (или кошелек О!Деньги) номера: <b>{{ phone }}</b>.<br><br>
            После подтверждения оплаты администратор обновит твою ссылку!
        </div>
        {% endif %}
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE, king=king_data, show_instruction=False)

@app.route('/buy', methods=['POST'])
def buy():
    global king_data
    new_name = request.form.get('username')
    new_link = request.form.get('userlink')
    
    # Рассчитываем стоимость для нового участника
    next_price = king_data["price"] + 50.00
    
    # Временное обновление данных на экране
    king_data["name"] = new_name
    king_data["link"] = new_link
    king_data["price"] = next_price
    
    # Показываем инструкцию с номером телефона
    return render_template_string(HTML_TEMPLATE, king=king_data, show_instruction=True, pending_price=next_price, phone=MY_PHONE_NUMBER)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
