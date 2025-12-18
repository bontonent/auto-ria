import psycopg2
import os
import uuid
from dotenv import load_dotenv

from datetime import datetime
import pytz

load_dotenv()

def connect_to_db():
    return psycopg2.connect(
        dbname=os.getenv('database'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        port=os.getenv('port'),
        host=os.getenv('host')
    )

def write_sql_line(filename, table_name, columns, values):
    formatted_values = []
    for val in values:
        if val is None:
            formatted_values.append("NULL")
        elif isinstance(val, (int, float)):
            formatted_values.append(str(val))
        else:
            safe_val = str(val).replace("'", "''")
            formatted_values.append(f"'{safe_val}'")

    sql_row = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(formatted_values)});\n"
    
    with open(filename, "a", encoding="utf-8") as f:
        f.write(sql_row)

def create_row(data_pull,base_dir):
    today_time = datetime.now(pytz.timezone("Europe/Kyiv")).strftime("%Y-%m-%d")
    conn = connect_to_db()
    cur = conn.cursor()
    
    id_car = str(uuid.uuid4())
    car_vin = data_pull.get('car_vin') or data_pull.get('car_vim')
    
    car_cols = [
        "id", "url", "title", "price_usd", "odometer", 
        "username", "phone_number", "images_count", "car_number", "car_vin"
    ]
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('database'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            port=os.getenv('port'),
            host=os.getenv('host')
        )
        cur = conn.cursor()
        
        today_time = datetime.now().strftime("%Y-%m-%d")
        id_car = str(uuid.uuid4())
        car_vin = data_pull.get('car_vin') or data_pull.get('car_vim')
        
        car_cols = [
            "id", "url", "title", "price_usd", "odometer", 
            "username", "phone_number", "images_count", "car_number", "car_vin"
        ]
        car_vals = (
            id_car,
            data_pull.get('url'),
            data_pull.get('title'),
            float(data_pull.get('price_usd', 0)),
            float(data_pull.get('odometer', 0)),
            data_pull.get('username'),
            data_pull.get('phone_number'),
            data_pull.get('images_count'),
            str(data_pull.get('car_number')),
            car_vin
        )

        # 1. Attempt to insert car
        cur.execute(f"""
            INSERT INTO car ({', '.join(car_cols)})
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (price_usd, url) DO NOTHING
        """, car_vals)

        # Check if the car was actually inserted (not a duplicate)
        if cur.rowcount > 0:
            image_list = data_pull.get('image_url', [])
            img_cols = ["id", "car_id", "image_url"]
            img_inserted_vals = []

            # 2. Insert images only if car is new
            for img_url in image_list:
                id_img = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO car_images (id, car_id, image_url)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (image_url) DO NOTHING
                """, (id_img, id_car, img_url))
                
                if cur.rowcount > 0:
                    img_inserted_vals.append((id_img, id_car, img_url))

            # Commit changes to DB
            conn.commit()

            # 3. Write to SQL script files only after successful commit
            create_sql_car = "/".join([str(base_dir),f"row_table_car_{today_time}.sql"])
            write_sql_line(create_sql_car, "car", car_cols, car_vals)
            
            create_sql_img = "/".join([str(base_dir),f"row_table_images_{today_time}.sql"])
            for img_val in img_inserted_vals:
                write_sql_line(create_sql_img, "car_images", img_cols, img_val)

            print(f"Success: SQL Script and DB updated for {data_pull.get('title')}")
        
        else:
            # Duplicate found, no action taken
            print(f"Skipped: Duplicate detected for URL {data_pull.get('url')} with price {data_pull.get('price_usd')}")
            conn.rollback()

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database Error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

# if __name__ == "__main__":
#     data_pull = {
#         'url': 'https://auto.ria.com/uk/auto_audi_q7_39052482.html', 
#         'title': 'Audi Q7 2018', 
#         'price_usd': '27000', 
#         'odometer': '146000', 
#         'username': 'Павло', 
#         'phone_number': 380981509418, 
#         'image_url': [
#             'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502453fhd.webp', 
#             'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502437fhd.webp'
#         ], 
#         'images_count': 39, 
#         'car_number': 39052482, 
#         'car_vim': 'WA1LAAF73JD046558'
#     }

#     create_row(data_pull)