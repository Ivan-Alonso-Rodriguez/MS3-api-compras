import boto3
import json
import os
import decimal
from middleware.validarTokenAcceso import validar_token

# Custom encoder para manejar Decimals
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    # Validar el token
    token_validacion = validar_token(event['headers'])
    if not token_validacion['ok']:
        return token_validacion['respuesta']

    datos_token = token_validacion['datos']

    # Obtener tabla desde variable de entorno
    tabla = boto3.resource('dynamodb').Table(os.environ['COMPRAS_TABLE'])

    # Obtener compras del usuario autenticado
    resultado = tabla.scan(
        FilterExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': datos_token['user_id']}
    )

    return {
        'statusCode': 200,
        'body': json.dumps(resultado.get('Items', []), cls=DecimalEncoder)
    }
