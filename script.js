function calcularDIFAL() {
    const ufOrigem = document.getElementById('ufOrigem').value;
    const ufDestino = document.getElementById('ufDestino').value;
    const numItem = document.getElementById('item').value;
    const numCST = document.getElementById('cst').value;
    const numFrete = document.getElementById('frete').value;
    const numIPI = document.getElementById('ipi').value;

    // Validação básica
    if (!ufOrigem || !ufDestino || ufOrigem === "" || ufDestino === "") {
        alert('Selecione a UF de origem e destino!');
        return;
    }

    if (!numItem || !numCST || !numFrete || !numIPI) {
        alert('Preencha todos os campos!');
        return;
    }

    // Preparar dados para envio
    const data = {
        ufOrigem: ufOrigem,
        ufDestino: ufDestino,
        valorItem: parseFloat(numItem),
        cst: parseInt(numCST),
        valorFrete: parseFloat(numFrete),
        valorIpi: parseFloat(numIPI)
    };

    console.log("Enviando dados:", data); // Para debug

    fetch('/calcular-difal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro na resposta do servidor');
        }
        return response.json();
    })
    .then(data => {
        console.log("Resposta recebida:", data); // Para debug
        if(data.status === 'success') {
            document.getElementById('valordifal').textContent = 
                data.valorDifal.toLocaleString('pt-BR', { 
                    style: 'currency', 
                    currency: 'BRL' 
                });
        } else {
            alert('Erro: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor: ' + error.message);
    });
}

function limparFormulario() {
    // Limpa os selects
    document.getElementById('ufOrigem').selectedIndex = 0;
    document.getElementById('ufDestino').selectedIndex = 0;
    
    // Limpa os inputs
    document.getElementById('item').value = '';
    document.getElementById('cst').value = '';
    document.getElementById('frete').value = '';
    document.getElementById('ipi').value = '';
    
    // Reseta o resultado
    document.getElementById('valordifal').textContent = '00';
    
    // Foca no primeiro campo
    document.getElementById('ufOrigem').focus();
}

// Esperando o documento carregar completamente
document.addEventListener('DOMContentLoaded', function() {
    
    // Listando de IDs dos campos que devem responder ao Enter...
    const campos = ['item', 'cst', 'frete', 'ipi'];
    
    // Para cada ID na lista
    campos.forEach(function(id) {
        // Pega o elemento pelo ID
        const campo = document.getElementById(id);
        
        // Adicionando um listener para o evento keypress
        campo.addEventListener('keypress', function(evento) {
            // Verifica se a tecla pressionada foi Enter
            if (evento.key === 'Enter') {
                // Impede o comportamento padrão (como submit)
                evento.preventDefault();
                
                // Chama a função de cálculo
                calcularDIFAL();
            }
        });
    });
});