from flask import Flask, render_template_string

app = Flask(__name__)

# Single file layout containing HTML, CSS styling, and JavaScript game logic
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Snake Game Haider</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e2e;
            color: #cdd6f4;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        h1 { color: #a6e3a1; margin-bottom: 5px; }
        .score-board {
            font-size: 20px;
            margin-bottom: 15px;
        }
        canvas {
            background: #313244;
            border: 4px solid #45475a;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        .instructions {
            margin-top: 15px;
            color: #a6adc8;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <h1>Flask Snake Game</h1>
    <div class="score-board">Score: <span id="score">0</span></div>
    
    <canvas id="gameCanvas" width="400" height="400"></canvas>
    
    <div class="instructions">Use <b>Arrow Keys</b> or <b>WASD</b> to move. Press <b>Spacebar</b> to restart if you crash.</div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const scoreElement = document.getElementById("score");

        const gridSize = 20;
        const tileCount = canvas.width / gridSize;

        // Game Variables
        let snake = [{x: 10, y: 10}];
        let food = {x: 5, y: 5};
        let dx = 1;
        let dy = 0;
        let score = 0;
        let gameInterval;
        let gameOver = false;

        function startGame() {
            snake = [{x: 10, y: 10}];
            generateFood();
            dx = 1;
            dy = 0;
            score = 0;
            scoreElement.innerText = score;
            gameOver = false;
            if (gameInterval) clearInterval(gameInterval);
            gameInterval = setInterval(updateGame, 100); // Game tick every 100ms
        }

        function updateGame() {
            if (gameOver) return;

            // Move Snake Head
            const head = {x: snake[0].x + dx, y: snake[0].y + dy};

            // Collision Detection (Wall crash)
            if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
                endGame();
                return;
            }

            // Collision Detection (Self crash)
            for (let i = 0; i < snake.length; i++) {
                if (head.x === snake[i].x && head.y === snake[i].y) {
                    endGame();
                    return;
                }
            }

            // Add new head
            snake.unshift(head);

            // Check if eating food
            if (head.x === food.x && head.y === food.y) {
                score += 10;
                scoreElement.innerText = score;
                generateFood();
            } else {
                // Remove tail if didn't eat food
                snake.pop();
            }

            draw();
        }

        function draw() {
            // Clear Canvas
            ctx.fillStyle = "#313244";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw Snake
            ctx.fillStyle = "#a6e3a1"; // Green snake
            snake.forEach((part, index) => {
                // Make the head a slightly different shade
                ctx.fillStyle = index === 0 ? "#94e2d5" : "#a6e3a1";
                ctx.fillRect(part.x * gridSize, part.y * gridSize, gridSize - 2, gridSize - 2);
            });

            // Draw Food
            ctx.fillStyle = "#f38ba8"; // Red food
            ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize - 2, gridSize - 2);

            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#f38ba8";
                ctx.font = "30px Arial";
                ctx.textAlign = "center";
                ctx.fillText("Game Over", canvas.width / 2, canvas.height / 2 - 10);
                ctx.fillStyle = "#cdd6f4";
                ctx.font = "16px Arial";
                ctx.fillText("Press Space to Restart", canvas.width / 2, canvas.height / 2 + 20);
            }
        }

        function generateFood() {
            food.x = Math.floor(Math.random() * tileCount);
            food.y = Math.floor(Math.random() * tileCount);
            
            // Ensure food doesn't spawn on top of snake
            snake.forEach(part => {
                if (part.x === food.x && part.y === food.y) {
                    generateFood();
                }
            });
        }

        function endGame() {
            gameOver = true;
            draw();
            clearInterval(gameInterval);
        }

        // Handle Keyboard Controls
        window.addEventListener("keydown", e => {
            switch(e.key) {
                // Arrow keys & WASD keys
                case "ArrowUp":
                case "w":
                case "W":
                    if (dy !== 1) { dx = 0; dy = -1; }
                    break;
                case "ArrowDown":
                case "s":
                case "S":
                    if (dy !== -1) { dx = 0; dy = 1; }
                    break;
                case "ArrowLeft":
                case "a":
                case "A":
                    if (dx !== 1) { dx = -1; dy = 0; }
                    break;
                case "ArrowRight":
                case "d":
                case "D":
                    if (dx !== -1) { dx = 1; dy = 0; }
                    break;
                case " ": // Spacebar to restart
                    if (gameOver) startGame();
                    break;
            }
        });

        // Initialize on load
        startGame();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("=" * 50)
    print("  Car Racing Game")
    print("  Developer: Muhammad Haider Anees")
    print("  Open: http://127.0.0.1:5075")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5075)
