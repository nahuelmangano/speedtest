function runTest() {
    const resultsBox = document.getElementById("results");
    const statusText = document.getElementById("status");
    const loader = document.getElementById("loader");

    resultsBox.style.display = "none";
    loader.style.display = "block";
    statusText.innerText = "Realizando test de velocidad, por favor espere...";

    fetch("/run-speedtest")
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al realizar el test");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById("download").innerText = data.download;
            document.getElementById("upload").innerText = data.upload;
            document.getElementById("ping").innerText = data.ping;
            resultsBox.style.display = "block";
            statusText.innerText = "";
        })
        .catch(error => {
            statusText.innerText = "Ocurrió un error: " + error.message;
        })
        .finally(() => {
            loader.style.display = "none";
        });
}
