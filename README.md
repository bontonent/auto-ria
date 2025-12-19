## Parsing
**url:** https://auto.ria.com/uk/search/?indexName=auto&page=0

First step make 
Create **.env**
```.env
database=autoria
user=postgres
password=password
port=5432
host=localhost
```

## Prepering for run on Docker
### run docker_compose

run in build environemtn
```bash
docker-compose up --build
```

Make public for use
```bash
docker build -t [user_name]/auto_ria:latest .
docker push [user_name]/auto_ria:latest
```
## Run AWS
Open
![alt text](./image_readme/image_7.png)

Create pipeline
![alt text](./image_readme/image_8.png)

Step 1 (main setting)
- create name
- choose schedule
Step 2(Create recipe)
1. Choose AMI
2. Recipe detail
3. Choose ubuntu LTS
4. Setting components
	- Amazon managed
		- choose docker-ce-ubunutu
	- Owned by me
		- Create run your image
			(click create component)
			- Add compatible OS Ubuntu 24.04
			- Add Definition document
```docker

name: PullMyScraper
schemaVersion: 1.0
phases:
  - name: build
    steps:
      - name: PullImage
        action: ExecuteBash
        inputs:
          commands:
            - docker pull [name docker file]/auto_ria:latest
```

				Add him
Step 3
- default
Step 4
- Add name
- IAM role
- instance type: add t.3micro
Step 5
- Add KMS key

Review and Create.
### Test pipeline
![alt text](./image_readme/image_10.png)

**Must be**
![alt text](./image_readme/image_9.png)

## Prepering for run on Python

### first step

Don't forgot create and connect Environment
```
python -m venv .venv
source .../activate
```

**Install library**
```requirements.txt
pip install -r requirements.txt
```

### Database
#### run in pgsql

Connect to database
```
psql -h localhost -p 5432 -U [user name] [database]
```

Create database+table
```
CREATE DATABASE autoria;
\c autoria
\i [round to database/create_table.sql]
ALTER USER [user name] WITH PASSWORD 'password';
```

#### run in pgadmin4
```sql
CREATE DATABASE autoria
CREATE TABLE IF NOT EXISTS car (
    id UUID PRIMARY KEY,
    url TEXT,
    title TEXT,
    price_usd FLOAT,
    odometer FLOAT,
    username TEXT,
    phone_number BIGINT, 
    images_count INTEGER,
    car_number VARCHAR(40),
    car_vin VARCHAR(40),
    datetime_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
    UNIQUE(price_usd, url)
);

CREATE TABLE IF NOT EXISTS car_images (
    id UUID PRIMARY KEY,
    car_id UUID REFERENCES car(id),
    image_url TEXT UNIQUE,
    CONSTRAINT fk_car FOREIGN KEY(car_id) REFERENCES car(id) ON DELETE CASCADE
);
```

### Setting .py for parsing

#### For parsing catalog
![alt text](./image_readme/image_5.png)

#### For parsing product page
![alt text](./image_readme/image_4.png)

### My result 100 pages
![alt text](./image_readme/image_6.png)
- 1973/2000 (douplicate del)
- 1.195757576 it/s
- all time: 27m