import psycopg2
import os

from dotenv import load_dotenv
load_dotenv()

def connect_to_db():
    # Connect DB
    conn = psycopg2.connect(
        dbname = os.getenv('database'),
        user = os.getenv('user'),
        password = os.getenv('password'),
        port = os.getenv('port'),
        host = os.getenv('host')
    )
    cur = conn.cursor()

    # Return instrument DB
    return conn, cur

def create_row(data_pull):
    conn, cur = connect_to_db()

    
    if (data_pull['image_url'] != []) & (data_pull['image_url'] != None):
        images = " & ".join(data_pull['image_url'])
    elif  len(data_pull['image_url']) == 1:
        images = data_pull['image_url']
        

    sql = """
        INSERT INTO car (
            url, title, price_usd, odometer, username, 
            phone_number, image_url, images_count, 
            car_number, car_vin
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        data_pull.get('url'),
        data_pull.get('title'),
        data_pull.get('price_usd'),
        int(data_pull.get('odometer', 0)),
        data_pull.get('username'),
        data_pull.get('phone_number'),
        images,
        data_pull.get('images_count'),
        str(data_pull.get('car_number')),
        data_pull.get('car_vim')
    )

    cur.execute(sql, values)
    conn.commit()
    
    cur.close()
    conn.close()
    print(f"Complete: {data_pull.get('title')}")

if __name__ == "__main__":
    data_pull = {'url': 'https://auto.ria.com/uk/auto_audi_q7_39052482.html', 'title': 'Audi Q7 2018', 'price_usd': '27000', 'odometer': '146000', 'username': 'Павло', 'phone_number': 380981509418, 'image_url': ['https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502453fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502437fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502406fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502426fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502491fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/audi_q7__619502399fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502352fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502366fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502351fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502335fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502435fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502375fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502371fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502377fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502448fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/audi_q7__619500254fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502381fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502383fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/audi_q7__619502409fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502410fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502412fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502413fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502415fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502427fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/audi_q7__619502479fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502483fhd.webp', 'https://cdn1.riastatic.com/photosnew/auto/photo/audi_q7__619502481fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/audi_q7__619502464fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502470fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502423fhd.webp', 'https://cdn4.riastatic.com/photosnew/auto/photo/audi_q7__619502469fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502468fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502490fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502510fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502477fhd.webp', 'https://cdn2.riastatic.com/photosnew/auto/photo/audi_q7__619502502fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502445fhd.webp', 'https://cdn3.riastatic.com/photosnew/auto/photo/audi_q7__619502433fhd.webp', 'https://cdn0.riastatic.com/photosnew/auto/photo/audi_q7__619502430fhd.webp'], 'images_count': 39, 'car_number': 39052482, 'car_vim': 'WA1LAAF73JD046558', 'datetime_found': '2025-12-18|04:33'}

    create_row(data_pull)



