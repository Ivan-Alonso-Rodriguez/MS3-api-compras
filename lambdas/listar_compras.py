import boto3, json
from middleware.validarTokenAcceso import validar_token

def lambda_handler(event, context):
    token_validacion = validar_token(event['headers'])
    if not token_validacion['ok']:
        return token_validacion['respuesta']

    datos_token = token_validacion['datos']
    tabla = boto3.resource('dynamodb').Table('dev-t_MS3_compras')

    resultado = tabla.scan(
        FilterExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': datos_token['user_id']}
    )

    return {
        'statusCode': 200,
        'body': json.dumps(resultado['Items'])
    }
