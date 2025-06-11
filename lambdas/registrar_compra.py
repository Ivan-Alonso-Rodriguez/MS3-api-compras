import boto3, json, uuid
from datetime import datetime
from middleware.validarTokenAcceso import validar_token

def lambda_handler(event, context):
    token_validacion = validar_token(event['headers'])
    if not token_validacion['ok']:
        return token_validacion['respuesta']

    datos_token = token_validacion['datos']
    body = json.loads(event['body'])
    productos = body.get('productos', [])

    if not productos:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Debes incluir productos en la compra'})
        }

    compra = {
        'compra_id': str(uuid.uuid4()),
        'user_id': datos_token['user_id'],
        'tenant_id': datos_token['tenant_id'],
        'productos': productos,
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    tabla = boto3.resource('dynamodb').Table('dev-t_MS3_compras')
    tabla.put_item(Item=compra)

    return {
        'statusCode': 200,
        'body': json.dumps({'mensaje': 'Compra registrada', 'compra_id': compra['compra_id']})
    }
