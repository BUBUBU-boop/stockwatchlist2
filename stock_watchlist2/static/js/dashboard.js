let chartInstance = null;

async function loadChart(ticker, period) {
    const response = await fetch(`/chart/${ticker}/${period}`);
    const data = await response.json();

    const canvas = document.getElementById("chart");

    if (!canvas) {
        return;
    }

    const ctx = canvas.getContext("2d");

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [
                {
                    data: data.prices
                }
            ]
        },
        options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        }
    }
}
    });
}

function initAvatarColors() {
    const avatars = document.querySelectorAll(".avatar-circle");

    avatars.forEach((avatar) => {
        const name = avatar.dataset.name || "";

        let hash = 0;

        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }

        const hue = Math.abs(hash % 360);

        avatar.style.backgroundColor = `hsl(${hue}, 60%, 50%)`;
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    initAvatarColors();

    const chartElement = document.getElementById("chart");

    if (chartElement && chartElement.dataset.ticker) {
        await loadChart(
            chartElement.dataset.ticker,
            "3m"
        );
    }

    const buttons = document.querySelectorAll(".period-btn");

    buttons.forEach((button) => {
        button.addEventListener("click", async () => {
            const ticker = button.dataset.ticker;
            const period = button.dataset.period;

            await loadChart(
                ticker,
                period
            );
        });
    });
});
