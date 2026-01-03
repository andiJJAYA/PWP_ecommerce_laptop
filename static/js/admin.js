  function createMiniChart(id, color, dataPoints) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: ["", "", "", "", "", ""],
        datasets: [
          {
            data: dataPoints,
            borderColor: color,
            borderWidth: 2,
            fill: true,
            backgroundColor: color.replace("1)", "0.1)"),
            tension: 0.4,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } },
      },
    });
  }

  window.addEventListener("load", function () {
    createMiniChart(
      "chartProduk",
      "rgba(13, 110, 253, 1)",
      [15, 25, 20, 30, 28, 45]
    );
    createMiniChart(
      "chartPesanan",
      "rgba(25, 135, 84, 1)",
      [5, 10, 8, 15, 12, 20]
    );
    createMiniChart(
      "chartKonsul",
      "rgba(255, 193, 7, 1)",
      [2, 8, 4, 10, 6, 12]
    );
    createMiniChart(
      "chartUser",
      "rgba(13, 202, 240, 1)",
      [50, 80, 70, 120, 110, 156]
    );
  });