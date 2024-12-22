import pandas as pd


# 공백 제거 함수
def remove_whitespace_from_columns(df):
    df.columns = df.columns.str.strip()
    return df

# 데이터 기간 변환 함수
def set_period(df, year_start, year_end):
    year_list = list(range(year_start, year_end + 1))
    filtered_df = df[df["year"].isin(year_list)]
    return filtered_df

# 데이터 변환 함수
def transform_dataframe(df):
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    transformed_df = df.rename(columns={
        'sunshine': 'sunhr',
        'tmax': 'Tmax',
        'tmin': 'Tmin',
        'rainfall': 'rain',
        'wind': 'wind',
        'humid': 'RH'
    })[['date', 'sunhr', 'Tmax', 'Tmin', 'rain', 'wind', 'RH']]
    return transformed_df

def main():
    df = pd.read_csv("../file/weather(146)_1994-2024.csv")
    df = remove_whitespace_from_columns(df)
    # print(df.columns)
    df = set_period(df, 2023, 2023) # 2023년도만 모델에 돌려보자
    df = transform_dataframe(df)

    df.to_csv("../file/weather_data.csv", index=False)



if __name__ == "__main__":
    main()
