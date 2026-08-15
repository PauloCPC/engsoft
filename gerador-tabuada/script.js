

const numero = document.getElementById("numero");
const botao = document.getElementById("gerar");
const resultado = document.getElementById("resultado");

botao.addEventListener("click", function() {

    const valor = Number(numero.value);

    if (valor < 1 || valor > 100) {
        resultado.innerHTML = "Digite um número entre 1 e 100.";
        return;
    }

    resultado.innerHTML = `<h2>Tabuada do ${valor}</h2>`;

    for (let i = 1; i <= 12; i++) {

        const multiplicacao = valor * i;

        resultado.innerHTML += `${valor} x ${i} = ${multiplicacao}<br>`;
    }
});