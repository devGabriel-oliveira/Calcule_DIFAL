from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Dicionário COMPLETO de alíquotas
aliquotas_estaduais = {
    'AC': {'interna': 19, 'interestadual': 12},
    'AL': {'interna': 19, 'interestadual': 12},
    'AP': {'interna': 18, 'interestadual': 12},
    'AM': {'interna': 20, 'interestadual': 12},
    'BA': {'interna': 20.5, 'interestadual': 12},
    'CE': {'interna': 20, 'interestadual': 12},
    'DF': {'interna': 20, 'interestadual': 12},
    'ES': {'interna': 17, 'interestadual': 12},
    'GO': {'interna': 19, 'interestadual': 12},
    'MA': {'interna': 22, 'interestadual': 12},
    'MT': {'interna': 17, 'interestadual': 12},
    'MS': {'interna': 17, 'interestadual': 12},
    'MG': {'interna': 18, 'interestadual': 12},
    'PA': {'interna': 19, 'interestadual': 12},
    'PB': {'interna': 20, 'interestadual': 12},
    'PR': {'interna': 19.5, 'interestadual': 12},
    'PE': {'interna': 20.5, 'interestadual': 12},
    'PI': {'interna': 21, 'interestadual': 12},
    'RJ': {'interna': 22, 'interestadual': 12},
    'RN': {'interna': 18, 'interestadual': 12},
    'RS': {'interna': 17, 'interestadual': 12},
    'RO': {'interna': 19.5, 'interestadual': 12},
    'RR': {'interna': 20, 'interestadual': 12},
    'SC': {'interna': 17, 'interestadual': 12},
    'SP': {'interna': 18, 'interestadual': 12},
    'SE': {'interna': 19, 'interestadual': 12},
    'TO': {'interna': 20, 'interestadual': 12}
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular-difal', methods=['POST'])
def calcular_difal():
    try:
        data = request.get_json()
        
        # Verificação dos dados recebidos
        print("Dados recebidos:", data)  # Para debug
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Nenhum dado recebido'}), 400
            
        # Extração dos valores
        uf_origem = data.get('ufOrigem')
        uf_destino = data.get('ufDestino')
        valor_item = float(data.get('valorItem', 0))
        cst = int(data.get('cst', 0))
        valor_frete = float(data.get('valorFrete', 0))
        valor_ipi = float(data.get('valorIpi', 0))
        
        # Validação das UFs
        if not uf_origem or not uf_destino:
            return jsonify({'status': 'error', 'message': 'Selecione a UF de origem e destino'}), 400
            
        if uf_origem not in aliquotas_estaduais or uf_destino not in aliquotas_estaduais:
            return jsonify({
                'status': 'error', 
                'message': f'UF inválida. Origem: {uf_origem}, Destino: {uf_destino}'
            }), 400
            
            
        if cst not in {0, 1, 2, 3, 4, 5, 6, 7, 8}:
            return jsonify({
                'status': 'error',
                'message': 'CST inválida! Use apenas valores de 0 a 8'
            }), 400

        # Obter alíquotas
        aliquota_interna = aliquotas_estaduais[uf_destino]['interna']
        aliquota_interestadual = aliquotas_estaduais[uf_origem]['interestadual']
        
        # Cálculo do DIFAL
        valor_nf = valor_item + valor_frete + valor_ipi
        
        #if cst in {1, 2, 3, 8}:
            #difal = valor_nf * (aliquota_interna/100 - 0.04)
        #else:
            #difal = valor_nf * (aliquota_interna/100 - aliquota_interestadual/100)
            
            
        # passando as aliquotas para porcentagem:
        
        aliquota_interna_porcentagem = aliquota_interna / 100
        
        if cst in {0, 4, 5, 6, 7}:
            aliquota_interestadual_porcentagem =  aliquota_interestadual / 100
        elif cst in {1, 2, 3, 8}:
            aliquota_interestadual_porcentagem = 0.04
        else:
            return jsonify({'status': 'error', 'message': 'CST inválida! Use apenas valores de 0 a 8'}), 400
        
        
            
        # Realizando o calculo do DIFAL Base Dupla
        icms = valor_nf * aliquota_interestadual_porcentagem
        BaseCalculo1 = valor_nf - icms
        BaseCalculo2 = BaseCalculo1 / (1 - aliquota_interna_porcentagem)
        ICMS_interno = BaseCalculo2 * aliquota_interna_porcentagem
        difal = ICMS_interno - icms
        
     
            
        return jsonify({
            'status': 'success',
            'valorDifal': round(difal, 2),
            'aliquotaInterna': round(aliquota_interna * 100, 2),  # Convertendo de volta para porcentagem
            'aliquotaInterestadual': round(aliquota_interestadual_porcentagem * 100, 2),
            'ufOrigem': uf_origem,
            'ufDestino': uf_destino,
            'cst': cst
        })

    except ValueError as e:
        return jsonify({'status': 'error', 'message': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)