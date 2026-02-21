import os

import mercadopago


sdk = mercadopago.SDK(os.getenv('mercado_pago_teste'))

def gerar_link_pagamento(preference_data):
    import mercadopago
    sdk = mercadopago.SDK(os.getenv('mercado_pago_teste'))
    result = sdk.preference().create(preference_data)
    import json
    print(json.dumps(preference_data, indent=2))  # Verifique se 'success' aparece com http://...
    print(result["response"])
    return result["response"]["sandbox_init_point"] # ou sandbox_init_point