import psycopg2
import psycopg2.extras
from config import config

def copy_from_csv(conn, cursor, table_name, csv_file_path):
    #Open the csv file
    with open(r'C:\investigation_project_v2-master\homicide_news_data.csv', 'r', encoding='ISO-8859-1') as file:
        #copy data from the csv file to the table
        cursor.execute('SET datestyle = "ISO, DMY";')
        cursor.copy_expert("""COPY homicide_news (news_report_url,
                            news_report_headline,
                            news_report_platform,
                            date_of_publication ,
                            author,
                            wire_service ,
                            no_of_subs,
                            victim_name ,
                            date_of_death,
                            race_of_victim,
                            age_of_victim ,
                            place_of_death_province ,
                            place_of_death_town,
                            type_of_location ,
                            sexual_assault ,
                            mode_of_death_specific ,
                            robbery_y_n_u,
                            perpetrator_name ,
                            perpetrator_relationship_to_victim ,
                            suspect_arrested ,
                            suspect_convicted,
                            multiple_murder,
                            intimate_femicide_y_n_u ,
                            extreme_violence_y_n_m_u ,
                            notes)
        FROM STDIN WITH CSV HEADER DELIMITER ';'
        """, file)
        print(f"Data copied successfully to homicide_news_data.")

def connect():
    connection = None
    csr = None
    try:
        params = config()
        print('Connecting to the PostgreSQL database ...')
        connection = psycopg2.connect(**params)
        csr = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        csr.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        # Drop the table if it already exists
        
        csr.execute("DROP TABLE IF EXISTS homicide_news CASCADE")
        
        create_script_homicide = '''CREATE TABLE homicide_news (
                            article_id SERIAL PRIMARY KEY,
                            news_report_id UUID DEFAULT uuid_generate_v4(), 
                            news_report_url VARCHAR(255) UNIQUE,
                            news_report_headline VARCHAR(255),
                            news_report_platform VARCHAR(255),
                            date_of_publication DATE,
                            author VARCHAR(255),
                            wire_service VARCHAR(255),
                            no_of_subs INT,
                            victim_name VARCHAR(255),
                            date_of_death DATE,
                            race_of_victim VARCHAR(255),
                            age_of_victim INT,
                            place_of_death_province VARCHAR(100),
                            place_of_death_town VARCHAR(255),
                            type_of_location VARCHAR(255),
                            sexual_assault VARCHAR(255),
                            mode_of_death_specific VARCHAR(100),
                            robbery_y_n_u VARCHAR(10),
                            perpetrator_name VARCHAR(255),
                            perpetrator_relationship_to_victim VARCHAR(255),
                            suspect_arrested VARCHAR(255),
                            suspect_convicted VARCHAR(255),
                            multiple_murder BOOLEAN,
                            intimate_femicide_y_n_u VARCHAR(10),
                            extreme_violence_y_n_m_u VARCHAR(10),
                            notes VARCHAR(1000)
                            )'''                   
        csr.execute(create_script_homicide)
        print("homicide_news Table created successfully in public")
        copy_from_csv(connection, csr, 'homicide_news_data', r'C:\investigation_project_v2\homicide_news_data.csv')
        
        
        connection.commit()

        
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if csr is not None:
            csr.close()
        if connection is not None:
            connection.close()
            print('Database connection terminated.')
            
if __name__ == "__main__":
    connect()
