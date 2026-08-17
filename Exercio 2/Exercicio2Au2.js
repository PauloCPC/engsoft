// iniciando o canvas
var canvas = document.getElementById('progress');
var ctx = canvas.getContext('2d');

// configurações
var x = 0;
var y = 0;
var altura = 10;
var largura = 0;
var fator = 60;
var resolucao = 1280;

// cor da barra
ctx.fillStyle = "#4169E1";

// Função que anima a barra de progresso
function animacao() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    largura += fator;

    if (largura > resolucao) {
        largura = resolucao;
    }

    ctx.fillRect(x, y, largura, altura);

    // interrompe a função setInterval()
    // para evitar carregamento excessivo
    if (largura >= resolucao) {
        clearInterval(atualiza);
    }
}

// Atualiza a barra
var atualiza = setInterval(animacao, 100);