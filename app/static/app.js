document.addEventListener("DOMContentLoaded", () => {
    const userSelect = document.getElementById("user-select");
    const modelSelect = document.getElementById("model-select");
    const simulateBtn = document.getElementById("simulate-btn");

    const historySection = document.getElementById("history-section");
    const recommendationSection = document.getElementById("recommendation-section");
    const historyGrid = document.getElementById("history-grid");
    const recommendationGrid = document.getElementById("recommendation-grid");
    const loading = document.getElementById("loading");
    const currentModelDisplay = document.getElementById("current-model-display");

    // Fetch initial data (users and models)
    async function init() {
        try {
            const [usersRes, modelsRes] = await Promise.all([
                fetch("/api/users"),
                fetch("/api/models")
            ]);

            const usersData = await usersRes.json();
            const modelsData = await modelsRes.json();

            usersData.users.forEach(userId => {
                const option = document.createElement("option");
                option.value = userId;
                option.textContent = `User ${userId}`;
                userSelect.appendChild(option);
            });

            modelsData.models.forEach(modelId => {
                const option = document.createElement("option");
                option.value = modelId;
                option.textContent = modelId.replace("_", " ").toUpperCase();
                modelSelect.appendChild(option);
            });

        } catch (error) {
            console.error("Failed to initialize:", error);
            alert("Error connecting to backend API");
        }
    }

    function createMovieCard(movie, isHistory = false) {
        const card = document.createElement("div");
        card.className = "movie-card";

        const title = document.createElement("div");
        title.className = "movie-title";
        title.textContent = movie.title;

        const meta = document.createElement("div");
        meta.className = "movie-meta";
        if (isHistory) {
            meta.textContent = `User Rating: ${movie.rating}/5`;
        } else {
            meta.textContent = `Match Score: ${(movie.score * 100).toFixed(1)}%`;
        }

        card.appendChild(title);
        card.appendChild(meta);
        return card;
    }

    simulateBtn.addEventListener("click", async () => {
        const userId = userSelect.value;
        const modelId = modelSelect.value;

        if (!userId || !modelId) {
            alert("Please select both a user and a model");
            return;
        }

        // Reset UI
        historySection.classList.add("hidden");
        recommendationSection.classList.add("hidden");
        loading.classList.remove("hidden");
        historyGrid.innerHTML = "";
        recommendationGrid.innerHTML = "";

        currentModelDisplay.textContent = modelSelect.options[modelSelect.selectedIndex].text;

        try {
            // Fetch history and recommendations
            const [historyRes, recsRes] = await Promise.all([
                fetch(`/api/user/${userId}/history`),
                fetch(`/api/recommend/${userId}?model=${modelId}&n=6`)
            ]);

            const historyData = await historyRes.json();
            const recsData = await recsRes.json();

            // Populate history
            historyData.history.forEach(movie => {
                historyGrid.appendChild(createMovieCard(movie, true));
            });

            // Populate recommendations
            recsData.recommendations.forEach(movie => {
                recommendationGrid.appendChild(createMovieCard(movie, false));
            });

            // Show UI
            loading.classList.add("hidden");
            historySection.classList.remove("hidden");
            recommendationSection.classList.remove("hidden");

        } catch (error) {
            console.error("Simulation error:", error);
            alert("An error occurred during simulation.");
            loading.classList.add("hidden");
        }
    });

    init();
});
