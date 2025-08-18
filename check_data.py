import pandas as pd

# 데이터 읽기
df = pd.read_excel('data_sample.xlsx', header=None)
print("전체 데이터:")
print(df)
print("\n데이터 형태:", df.shape)

print("\n컬럼별 고유값:")
for i in range(len(df.columns)):
    print(f'컬럼 {i}:', df[i].unique()[:5])

# 실제 데이터 구조 파악
print("\n실제 데이터 구조:")
for idx, row in df.iterrows():
    print(f"행 {idx}:", row.tolist()) 