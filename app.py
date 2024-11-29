from flask import Flask, render_template, request
from datetime import datetime
from calculations import parse_float, calculate_required_return_rate, calculate_yearly_data

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 사용자 입력 받기
        dob = request.form['dob']
        retirement_age = int(request.form['retirement_age'])
        life_expectancy = int(request.form['life_expectancy'])
        current_assets = parse_float(request.form['current_assets'])
        current_salary = parse_float(request.form['current_salary'])
        monthly_investment = parse_float(request.form['monthly_investment'])
        required_pension = parse_float(request.form['required_pension'])
        salary_growth_rate = parse_float(request.form['salary_growth_rate'])
        continue_investment = request.form.get('continue_investment') == 'on'

        # 필요한 연간 수익률 계산
        required_return_rate = calculate_required_return_rate(
            dob, retirement_age, life_expectancy, current_assets,
            monthly_investment, required_pension, salary_growth_rate,
            continue_investment
        )

        if required_return_rate is None:
            required_return_rate = '목표를 달성할 수 있는 수익률을 찾지 못했습니다.'
            data = []
        else:
            # 매년 데이터 계산
            data = calculate_yearly_data(
                dob, retirement_age, life_expectancy, current_assets,
                monthly_investment, required_pension, salary_growth_rate,
                continue_investment, required_return_rate
            )

        return render_template('result.html', data=data, required_return_rate=required_return_rate)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
