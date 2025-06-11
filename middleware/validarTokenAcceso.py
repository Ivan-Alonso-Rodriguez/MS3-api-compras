import boto3
from datetime import datetime

def validar_token(headers):
    token = headers.get('x-auth-token')
    if not token:
        return {
            'ok': False,
            'respuesta': {
                'statusCode': 401,
                'body': '{"mensaje": "Token no proporcionado"}'
            }
        }

    tabla = boto3.resource('dynamodb').Table(headers.get('TOKENS_TABLE') or 'dev-t_MS1_tokens_acceso')
    respuesta = tabla.get_item(Key={'token': token})

    if 'Item' not in respuesta:
        return {
            'ok': False,
            'respuesta': {
                'statusCode': 403,
                'body': '{"mensaje": "Token no existe"}'
            }
        }

    datos = respuesta['Item']
    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if ahora > datos['expires']:
        return {
            'ok': False,
            'respuesta': {
                'statusCode': 403,
                'body': '{"mensaje": "Token expirado"}'
            }
        }

    return {'ok': True, 'datos': datos}
