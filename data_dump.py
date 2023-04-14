import data_extract_transform as data
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import time

print('Script execution start.\n')
start = time.perf_counter()

DB_HOST = 'localhost:5432'
DB_NAME = 'pokemon'
DB_USER = 'postgres'
DB_PASS = 'admin'

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}', echo=False)

with engine.connect() as conn:
    print('Re-initializing tables...')
    conn.execute(text("CALL initialize_tables()"))
    conn.commit()
    print('Success!\n')

    print(f'Inserting {len(data.type_df.index)} rows to public.pokemon_types on {DB_NAME}...')
    data.type_df.to_sql('pokemon_types', engine, if_exists='append', index=False, schema='public', chunksize=10000)
    print(f'Successfully inserted {len(data.type_df.index)} rows.\n')

    print(f'Inserting {len(data.poke_df.index)} rows to public.pokemon on {DB_NAME}...')
    data.poke_df.to_sql('pokemon', engine, if_exists='append', index=False, schema='public', chunksize=10000)
    print(f'Successfully inserted {len(data.poke_df.index)} rows.\n')

    print(f'Inserting {len(data.evo_df.index)} rows to public.evolutions on {DB_NAME}...')
    data.evo_df.to_sql('evolutions', engine, if_exists='append', index=False, schema='public', chunksize=10000)
    print(f'Successfully inserted {len(data.evo_df.index)} rows.\n')