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

def create_row(data_pull, base_dir):
    today_time = datetime.now(pytz.timezone("Europe/Kyiv")).strftime("%Y-%m-%d")
    conn = None
    
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        id_car = str(uuid.uuid4())
        # Use .get() with a default value to avoid ReferenceErrors
        car_vin = data_pull.get('car_vin') or data_pull.get('car_vim') or None
        
        car_cols = [
            "id", "url", "title", "price_usd", "odometer", 
            "username", "phone_number", "images_count", "car_number", "car_vin"
        ]
        
        car_vals = (
            id_car,
            data_pull.get('url'),
            data_pull.get('title'),
            float(data_pull.get('price_usd', 0)) if data_pull.get('price_usd') else 0.0,
            float(data_pull.get('odometer', 0)) if data_pull.get('odometer') else 0.0,
            data_pull.get('username'),
            data_pull.get('phone_number'),
            data_pull.get('images_count', 0),
            str(data_pull.get('car_number')),
            car_vin
        )

        # 1. Insert car with Conflict handling
        cur.execute(f"""
            INSERT INTO car ({', '.join(car_cols)})
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (price_usd, url) DO NOTHING
        """, car_vals)

        if cur.rowcount > 0:
            image_list = data_pull.get('image_url', [])
            img_inserted_vals = []

            # 2. Insert images only if car is new
            if image_list:
                img_cols = ["id", "car_id", "image_url"]
                for img_url in image_list:
                    id_img = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO car_images (id, car_id, image_url)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (image_url) DO NOTHING
                    """, (id_img, id_car, img_url))
                    
                    if cur.rowcount > 0:
                        img_inserted_vals.append((id_img, id_car, img_url))

            conn.commit()

            # 3. Write SQL Dumps
            car_sql_path = os.path.join(base_dir, f"row_table_car_{today_time}.sql")
            write_sql_line(car_sql_path, "car", car_cols, car_vals)
            
            if img_inserted_vals:
                img_sql_path = os.path.join(base_dir, f"row_table_images_{today_time}.sql")
                for img_val in img_inserted_vals:
                    write_sql_line(img_sql_path, "car_images", ["id", "car_id", "image_url"], img_val)
        else:
            conn.rollback()

    except Exception as e:
        if conn: conn.rollback()
        print(f"Database Error for {data_pull.get('url')}: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
    

if __name__ == "__main__":
    data_pull = {'url': 'https://auto.ria.com/uk/auto_porsche_cayenne_39166041.html', 'title': 'Porsche Cayenne 2012', 'price_usd': '19500', 'odometer': '133000', 'username': 'Елизавета', 'phone_number': 380973755250, 'image_url': ['https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630921fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630922fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630924fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630923fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630927fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630931fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630928fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622631030fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630930fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630926fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630929fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630932fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630933fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630934fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630935fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630936fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630937fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630938fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630940fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630946fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630942fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630944fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630948fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630945fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630951fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630956fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630953fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630952fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630955fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630954fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630957fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630958fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630959fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630960fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630961fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630963fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630962fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630964fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630965fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630967fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630966fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/porsche_cayenne__622630968fhd.webp'], 'images_count': 42, 'car_number': 39166041, 'car_vim': None, 'datetime_found': '2025-12-18|12:10'}
    base_dir="/home/bontonent/Projects/make_money/auto_ria/database"
    create_row(data_pull,base_dir)