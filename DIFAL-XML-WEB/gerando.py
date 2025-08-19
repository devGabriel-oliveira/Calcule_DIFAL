from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
from aliquotas import aliquotas_estaduais

ALLOWED_EXTENSIONS = {'xml'}

# Função para verificar se o arquivo tem uma extensão permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Criação do objeto Flask
app = Flask(__name__)
CORS(app)  # Configurar CORS

# Rota para renderizar o template de index
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o XML
@app.route('/process_xml', methods=['POST'])
def process_xml():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        try:
            tree = ET.parse(file)
            root = tree.getroot()

            namespaces = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}  # Defina o namespace aqui

            valores_itens = {}
            for idx, item in enumerate(root.findall('.//nfe:det', namespaces), start=1):
                try:
                    valor_item_text = item.find('.//nfe:vProd', namespaces)
                    valor_item = float(valor_item_text.text) if valor_item_text is not None and valor_item_text.text else 0.0

                    frete_text = item.find('.//nfe:vFrete', namespaces)
                    frete = float(frete_text.text) if frete_text is not None and frete_text.text else 0.0

                    ipi_text = item.find('.//nfe:vIPI', namespaces)
                    ipi = float(ipi_text.text) if ipi_text is not None and ipi_text.text else 0.0

                    cst_text = item.find('.//nfe:CST', namespaces)
                    cst = int(cst_text.text) if cst_text is not None and cst_text.text and cst_text.text.isdigit() else None

                    valor_nf = valor_item + frete + ipi

                    # Substitua com a lógica adequada para obter as alíquotas
                    aliquota_interestadual = aliquotas_estaduais.get('ICMS_INTERESTADUAL', 0.04)
                    aliquota_interna = aliquotas_estaduais.get('ICMS_INTERNO', 0.12)

                    if cst in [1, 2, 3, 8]:
                        icms_interestadual = valor_nf * aliquota_interestadual
                    else:
                        icms_interestadual = valor_nf * aliquota_interestadual

                    base_calculo_1 = valor_nf - icms_interestadual
                    base_calculo_2 = base_calculo_1 / (1 - aliquota_interna)
                    icms_interno = base_calculo_2 * aliquota_interna
                    difal = icms_interno - icms_interestadual

                    valores_itens[f'valor_item_{idx}'] = {
                        'valor_total_item': valor_nf,
                        'icms': icms_interestadual,
                        'difal': round(difal, 2),
                        'cst': cst
                    }
                except AttributeError as e:
                    return jsonify({'error': f'Error processing item {idx}: {e}'})

            return jsonify(valores_itens)

        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    return "Invalid file format", 400

if __name__ == '__main__':
    app.run(debug=True)
