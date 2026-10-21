import psycopg2

try:
    psycopg2.connect(host="localhost", port=5432,
                     user="library", password="library", dbname="library")
    print("Connexion OK")
except UnicodeDecodeError as e:
    print("Vrai message :", e.object.decode("cp1252"))