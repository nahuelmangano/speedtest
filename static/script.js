function runTest() {
    document.getElementById("status").textContent = "Ejecutando test... esto puede tardar unos segundos.";
    document.getElementById("results").style.display = "none";

    fetch("/run-speedtest")
        .then(response => response.json())
        .then(data => {
            document.getElementById("download").textContent = data.download;
            document.getElementById("upload").textContent = data.upload;
            document.getElementById("ping").textContent = data.ping;
            document.getElementById("results").style.display = "block";
            document.getElementById("status").textContent = "Test completado.";
        })
        .catch(error => {
            document.getElementById("status").textContent = "Error al ejecutar el test.";
            console.error(error);
        });
}
