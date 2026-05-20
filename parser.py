import requests
import argparse
import re
import json

#Bloque de argumentos argparse
parser = argparse.ArgumentParser(description="Detecta fuerza bruta SSH en logs")
parser.add_argument("--archivo", type=str, required=True, help="Ruta al archivo log")
parser.add_argument("--umbral", type=int, default=3, help="Intentos mínimos para alerta (default: 3) ")
parser.add_argument("--formato", type=str, choices=['txt', 'json', 'csv'], default='txt', help="Formato de salida")

args = parser.parse_args()

#Creamos función para obtener puntuación y país a partir de la IP proporcionada más adelante
def obtener_puntuacion_ip(IP):
    api_key = "" #INTRODUCE TU API KEY AQUÍ

    #Asi es como lo quiere abuseipdb la llamada a la api
    url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={IP}"

    #Creamos los headers para requests
    headers_http = {"Accept": "application/json",
                     "Key": api_key}

    #Introducimos la url y headers a requests.get para que nos cree el objeto
    respuesta = requests.get(url, headers=headers_http)

    #Muestra métodos y atributos del objeto creado
    #print(help(respuesta))
    #print(dir(respuesta))

    datos = respuesta.json()
    scoreAbuse = datos["data"]["abuseConfidenceScore"]
    countryCode = datos["data"]["countryCode"]

    return scoreAbuse, countryCode

#Leemos archivo auth.log o el proporcioado por el arg --archivo
with open(args.archivo) as f:
    contenido = f.read()

# Regex para hacer una lista de IPs
ip = re.findall(r"Failed password.*from (\d+\.\d+\.\d+\.\d+)", contenido)

conteo_ip = {}
for x in ip:
    # Hacemos diccionario a partir de la lista de IP
    conteo_ip[x] = conteo_ip.get(x, 0) + 1 

reporte = []
#lógica simple para iterar basándonos en el umbral junto con la función para obtener su puntuación/localización
for ip, valor in conteo_ip.items():
    if valor > args.umbral:
        scoreAbuse, countryCode = obtener_puntuacion_ip(ip)
        #hago una variable auxiliar para pasarle el valor limpio al json luego
        if scoreAbuse >= 25:
            score = f"{scoreAbuse} (Peligrosa)"
        else:
            score = f"{scoreAbuse} (Probablemente segura / Pocos reportes)"
        print(f"IP: {ip} --- CountryCode: {countryCode}\nIntentos: {valor} --- Puntuación \"AbuseIPDB\": {score}\n")

        #Creo lista a partir de los datos obtenidos
        reporte.append({
            "ip": ip,
            "countryCode": countryCode,
            "intentos": valor,
            "scoreAbuse": scoreAbuse
        })

#Genero archivo json basándome en la lista creada justo antes
with open ("reporte_abuse.json", "w") as f:
    json.dump(reporte, f)

print("[+] Generado reporte llamado \"reporte_abuse.json\"")

