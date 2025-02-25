from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML 模板
CALCULATOR_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>纺织品价格计算器</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .calculator {
            background: #333;
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            width: 900px;
            display: flex;
            gap: 20px;
        }
        .input-section, .result-section {
            background: #fff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }
        .input-section {
            width: 400px;
        }
        .result-section {
            width: 400px;
            background: #e8f4f8;
        }
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        label {
            font-weight: 700;
            color: #2c3e50;
            font-size: 14px;
        }
        input[type="number"] {
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            width: 100%;
            box-sizing: border-box;
            background: #f9f9f9;
            transition: border-color 0.3s;
        }
        input[type="number"]:focus {
            border-color: #3498db;
            outline: none;
        }
        .button-group {
            display: flex;
            justify-content: space-around;
            margin-top: 15px;
        }
        input[type="submit"], #reset-button {
            padding: 12px;
            border: none;
            border-radius: 50%;
            width: 120px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            transition: transform 0.2s, background-color 0.3s;
        }
        input[type="submit"] {
            background-color: #ff6b6b;
            color: white;
        }
        input[type="submit"]:hover {
            background-color: #e65a5a;
            transform: scale(1.1);
        }
        input[type="submit"]:active {
            transform: scale(0.95);
        }
        #reset-button {
            background-color: #2ecc71;
            color: white;
        }
        #reset-button:hover {
            background-color: #27ae60;
            transform: scale(1.1);
        }
        #reset-button:active {
            transform: scale(0.95);
        }
        .result-section h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            text-align: center;
        }
        .result-table {
            width: 100%;
            border-collapse: collapse;
            opacity: 0;
            animation: fadeIn 0.5s forwards;
        }
        .result-table th, .result-table td {
            padding: 8px;
            border-bottom: 1px solid #ddd;
            text-align: left;
            font-size: 14px;
        }
        .result-table th {
            background-color: #3498db;
            color: white;
        }
        .result-table tr:last-child td {
            border-bottom: none;
            font-weight: 700;
            color: #ff6b6b;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @media (max-width: 600px) {
            .calculator {
                flex-direction: column;
                width: 100%;
            }
            .input-section, .result-section {
                width: 100%;
            }
            .button-group {
                flex-direction: column;
                gap: 10px;
            }
            input[type="submit"], #reset-button {
                width: 100%;
                border-radius: 10px;
            }
        }
    </style>
</head>
<body>
    <h1>纺织品价格计算器</h1>
    <div class="calculator">
        <div class="input-section">
            <form id="calcForm" method="post" action="/calculate">
                <label>门幅 (厘米):</label>
                <input type="number" name="width" step="0.1" required value="{{ width or '' }}">
                <label>纬密 (根/梭):</label>
                <input type="number" name="weft_density" step="0.1" required value="{{ weft_density or '' }}">
                <label>头份 (根):</label>
                <input type="number" name="head_count" required value="{{ head_count or '' }}">
                <label>经纱D数 (D):</label>
                <input type="number" name="warp_d" step="0.1" required value="{{ warp_d or '' }}">
                <label>纬纱D数 (D):</label>
                <input type="number" name="weft_d" step="0.1" required value="{{ weft_d or '' }}">
                <label>经纱原料价格 (元/KG):</label>
                <input type="number" name="warp_price" step="0.01" required value="{{ warp_price or '' }}">
                <label>纬纱原料价格 (元/KG):</label>
                <input type="number" name="weft_price" step="0.01" required value="{{ weft_price or '' }}">
                <label>车速 (转/分钟):</label>
                <input type="number" name="machine_speed" step="0.1" required value="{{ machine_speed or '' }}">
                <label>缩率:</label>
                <input type="number" name="shrinkage" step="0.01" required value="{{ shrinkage or '' }}">
                <label>整经费用 (元):</label>
                <input type="number" name="warping_cost" step="0.01" required value="{{ warping_cost or '' }}">
                <label>开票价格 (元/米):</label>
                <input type="number" name="invoice_price" step="0.01" required value="{{ invoice_price or '' }}">
                <div class="button-group">
                    <input type="submit" value="计算">
                    <button type="button" id="reset-button" onclick="resetForm()">清零</button>
                </div>
            </form>
        </div>
        <div class="result-section">
            <h3>计算结果</h3>
            {% if result %}
                <table class="result-table">
                    <tr><th>项目</th><th>值</th></tr>
                    <tr><td>经向克重</td><td>{{ result['warp_weight'] }} 克</td></tr>
                    <tr><td>纬向克重</td><td>{{ result['weft_weight'] }} 克</td></tr>
                    <tr><td>经纱成本</td><td>{{ result['warp_cost'] }} 元</td></tr>
                    <tr><td>纬纱成本</td><td>{{ result['weft_cost'] }} 元</td></tr>
                    <tr><td>成本价</td><td>{{ result['cost_price'] }} 元/米</td></tr>
                    <tr><td>日产量</td><td>{{ result['daily_output'] }} 米</td></tr>
                    <tr><td>日利润</td><td>{{ result['daily_profit'] }} 元</td></tr>
                </table>
            {% else %}
                <p>输入参数后点击“计算”查看结果！</p>
            {% endif %}
        </div>
    </div>
    <script>
        function resetForm() {
            document.getElementById('calcForm').reset();
            window.location.href = '/';
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(CALCULATOR_HTML, result=None)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # 获取输入参数
        width = float(request.form['width'])
        weft_density = float(request.form['weft_density'])
        head_count = float(request.form['head_count'])
        warp_d = float(request.form['warp_d'])
        weft_d = float(request.form['weft_d'])
        warp_price = float(request.form['warp_price'])
        weft_price = float(request.form['weft_price'])
        machine_speed = float(request.form['machine_speed'])
        shrinkage = float(request.form['shrinkage'])
        warping_cost = float(request.form['warping_cost'])
        invoice_price = float(request.form['invoice_price'])

        # 计算中间结果
        warp_weight = head_count * warp_d / 9000
        weft_weight = weft_density * (width + 12) / 9000 * weft_d
        warp_cost = (warp_weight * (warp_price / 1000) + warping_cost) * shrinkage
        weft_cost = weft_weight * (weft_price / 1000)
        cost_price = warp_cost + weft_cost
        daily_output = machine_speed * 24 * 60 * 0.92 / weft_density / 100
        daily_profit = (invoice_price - cost_price) * daily_output

        # 保留两位小数
        result = {
            'warp_weight': round(warp_weight, 2),
            'weft_weight': round(weft_weight, 2),
            'warp_cost': round(warp_cost, 2),
            'weft_cost': round(weft_cost, 2),
            'cost_price': round(cost_price, 2),
            'daily_output': round(daily_output, 2),
            'daily_profit': round(daily_profit, 2)
        }

        # 将输入值传回表单以保持显示
        inputs = {
            'width': width,
            'weft_density': weft_density,
            'head_count': head_count,
            'warp_d': warp_d,
            'weft_d': weft_d,
            'warp_price': warp_price,
            'weft_price': weft_price,
            'machine_speed': machine_speed,
            'shrinkage': shrinkage,
            'warping_cost': warping_cost,
            'invoice_price': invoice_price
        }

        return render_template_string(CALCULATOR_HTML, result=result, **inputs)
    except Exception as e:
        return render_template_string(CALCULATOR_HTML, result=f"计算错误: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)