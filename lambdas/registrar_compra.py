import boto3, json, uuid
from datetime import datetime
from middleware.validarTokenAcceso import validar_token
import os

dynamodb = boto3.resource('dynamodb')
productos_table = dynamodb.Table(os.environ['PRODUCTOS_TABLE'])
compras_table = dynamodb.Table(os.environ['COMPRAS_TABLE'])

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

    productos_confirmados = []

    for p in productos:
        codigo = p.get('codigo')
        cantidad = p.get('cantidad', 1)

        if not codigo or cantidad <= 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Producto inválido: {p}'})
            }

        resultado = productos_table.get_item(Key={'codigo': codigo})
        item = resultado.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Producto {codigo} no encontrado'})
            }

        if item.get('cantidad', 0) < cantidad:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Stock insuficiente para {codigo}'})
            }

        # Descontar stock
        productos_table.update_item(
            Key={'codigo': codigo},
            UpdateExpression='SET cantidad = cantidad - :c',
            ConditionExpression='cantidad >= :c',
            ExpressionAttributeValues={':c': cantidad}
        )

        productos_confirmados.append({
            'codigo': codigo,
            'nombre': item['nombre'],
            'precio_unitario': item['precio'],
            'cantidad': cantidad
        })

    compra = {
        'compra_id': str(uuid.uuid4()),
        'user_id': datos_token['user_id'],
        'tenant_id': datos_token['tenant_id'],
        'productos': productos_confirmados,
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    compras_table.put_item(Item=compra)

    return {
        'statusCode': 200,
        'body': json.dumps({'mensaje': 'Compra registrada', 'compra_id': compra['compra_id']})
    }
