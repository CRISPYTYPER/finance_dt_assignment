from datetime import datetime

def parse_float(value):
    return float(value.replace(',', '.'))

def get_tax_rate(age):
    if 55 <= age < 70:
        return 0.055  # 5.5%
    elif 70 <= age < 80:
        return 0.044  # 4.4%
    elif 80 <= age:
        return 0.033  # 3.3%
    return -1 # 55세 미만은 다루지 않음.

def calculate_required_return_rate(dob, retirement_age, life_expectancy, current_assets, monthly_investment,
                                   required_pension, salary_growth_rate, continue_investment):
    # 현재 나이 계산
    birth_year = int(dob.split('-')[0])
    current_year = datetime.now().year
    age = current_year - birth_year

    # 인출 시작 나이 설정
    withdrawal_start_age = max(retirement_age, 55)

    # 총 계산할 개월 수 계산
    total_months = (life_expectancy - age + 1) * 12

    # 월간 임금 상승률 계산 (루프 외부에서 계산 가능)
    monthly_salary_growth = (1 + salary_growth_rate / 100) ** (1/12) - 1

    # 이진 탐색을 통한 필요한 월 수익률 계산
    low, high = 0, 0.05  # 월 수익률 0% ~ 5%
    tolerance = 1e-7  # 허용 오차를 작게 설정하여 정확도 향상

    while high - low > tolerance:
        rate = (high + low) / 2
        temp_assets = current_assets
        temp_monthly_investment = monthly_investment
        success = True

        for month in range(total_months):
            temp_age = age + month // 12

            # 은퇴 전/후 구분
            if temp_age < retirement_age:
                investment = temp_monthly_investment
            else:
                investment = temp_monthly_investment if continue_investment else 0

            # 인출 여부 결정
            if temp_age >= withdrawal_start_age:
                tax_rate = get_tax_rate(temp_age)
                gross_withdrawal = required_pension / (1 - tax_rate)
                withdrawal = gross_withdrawal
            else:
                withdrawal = 0

            # 투자 금액 추가 (기간 초)
            temp_assets += investment

            # 자산 증가 (투자 수익률 적용)
            temp_assets = temp_assets * (1 + rate)

            # 인출 금액 차감 (기간 말)
            temp_assets -= withdrawal

            if temp_assets < 0:
                success = False
                break

            # 월 투자 금액 증가 (매월 적용)
            temp_monthly_investment *= (1 + monthly_salary_growth)

        if success:
            high = rate
        else:
            low = rate

    # 월간 수익률을 연간 수익률로 변환
    required_return_rate = (1 + high) ** 12 - 1
    return round(required_return_rate * 100, 2)  # 백분율로 변환



def calculate_yearly_data(dob, retirement_age, life_expectancy, current_assets, monthly_investment,
                          required_pension, salary_growth_rate, continue_investment, required_return_rate):
    # 현재 나이 계산
    birth_year = int(dob.split('-')[0])
    base_year = datetime.now().year
    age = base_year - birth_year

    # 인출 시작 나이 설정
    withdrawal_start_age = max(retirement_age, 55)

    # 총 계산할 개월 수 계산
    total_months = (life_expectancy - age + 1) * 12

    # 매월 데이터 계산
    data = []
    temp_assets = current_assets
    temp_monthly_investment = monthly_investment
    rate = (1 + required_return_rate / 100) ** (1/12) - 1  # 월간 수익률 계산

    # 월간 임금 상승률 계산 (루프 외부에서 계산 가능)
    monthly_salary_growth = (1 + salary_growth_rate / 100) ** (1/12) - 1

    for month in range(total_months):
        current_year = base_year + month // 12
        current_month = month % 12 + 1
        temp_age = age + month // 12

        # 연간 누적 변수 초기화
        if current_month == 1:
            annual_investment = 0
            annual_profit = 0
            annual_withdrawal = 0
            annual_tax = 0

        # 은퇴 전/후 구분
        if temp_age < retirement_age:
            investment = temp_monthly_investment
        else:
            investment = temp_monthly_investment if continue_investment else 0

        # 인출 여부 결정
        if temp_age >= withdrawal_start_age:
            tax_rate = get_tax_rate(temp_age)
            gross_withdrawal = required_pension / (1 - tax_rate)
            withdrawal = gross_withdrawal
            tax = gross_withdrawal * tax_rate
            after_tax_withdrawal = required_pension  # 세후 인출 금액은 필요한 연금액과 동일
        else:
            withdrawal = 0
            tax = 0
            after_tax_withdrawal = 0

        # 이전 자산 저장
        previous_assets = temp_assets

        # 투자 금액 추가 (기간 초)
        temp_assets += investment

        # 자산 증가 (투자 수익률 적용)
        temp_assets = temp_assets * (1 + rate)

        # 수익 계산
        profit = (previous_assets + investment) * rate

        # 인출 금액 차감 (기간 말)
        temp_assets -= withdrawal

        # 월별 누적
        annual_investment += investment
        annual_profit += profit
        annual_withdrawal += withdrawal
        annual_tax += tax

        # 월 투자 금액 증가 (매월 적용)
        temp_monthly_investment *= (1 + monthly_salary_growth)

        # 매년 12월 또는 마지막 달에 데이터 저장
        if current_month == 12 or month == total_months - 1:
            data.append({
                'age': temp_age,
                'year': current_year,
                'assets': int(round(previous_assets)),
                'investment': int(round(annual_investment)),
                'profit': int(round(annual_profit)),
                'withdrawal': int(round(annual_withdrawal)),
                'tax': int(round(annual_tax)),
                'after_tax_withdrawal': int(round(annual_withdrawal - annual_tax)),
                'end_assets': int(round(temp_assets))
            })

        if temp_assets < 0:
            break

    return data

