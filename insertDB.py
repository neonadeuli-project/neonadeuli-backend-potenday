import pymysql
import pandas as pd

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    database='neonadeuli',
    port=3306
)

try:
    csv_file_path = './heritage_table_v2.csv'
    data = pd.read_csv(csv_file_path)

    cursor = connection.cursor()

    insert_query = """
                INSERT INTO heritages (
                    heritage_type_id, 
                    name, 
                    name_hanja, 
                    description, 
                    location, 
                    latitude, 
                    longitude, 
                    category, 
                    sub_category1, 
                    sub_category2, 
                    sub_category3, 
                    era, 
                    area_code, 
                    image_url, 
                    created_at,
                    updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

    # 각 행을 테이블에 삽입
    for index, row in data.iterrows():
        cursor.execute(insert_query, (
        int(row['heritage_type_id']),
        str(row['name']),
        str(row['name_hanja']),
        str(row['description']),
        str(row['location']),
        float(row['latitude']),
        float(row['longitude']),
        str(row['category']),
        str(row['sub_category1']),
        str(row['sub_category2']),
        str(row['sub_category3']),
        str(row['era']),
        float(row['area_code']),
        str(row['image_url']),
        str(row['created_at']),
        str(row['updated_at'])
    ))

    # 변경사항 저장
    connection.commit()

finally:
    # 연결 종료
    connection.close()