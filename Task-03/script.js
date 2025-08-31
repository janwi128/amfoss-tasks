const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreDisplay = document.getElementById('score');
const bestScoreDisplay = document.getElementById('best-score');
const resetButton = document.getElementById('reset-button');
const drawingSound = new Audio('drawing-sound.mp3');

let isDrawing = false;
let drawnPoints = [];
const centerPoint = { x: canvas.width / 2, y: canvas.height / 2 };
let bestSessionScore = parseFloat(sessionStorage.getItem('bestScore')) || 0;

// Set up the canvas and event listeners
function init() {
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    resetButton.addEventListener('click', resetGame);
    bestScoreDisplay.textContent = `${Math.round(bestSessionScore)}%`;
    drawRedDot();
}

function drawRedDot() {
    ctx.beginPath();
    ctx.arc(centerPoint.x, centerPoint.y, 5, 0, 2 * Math.PI);
    ctx.fillStyle = 'red';
    ctx.fill();
}

function startDrawing(event) {
    isDrawing = true;
    drawnPoints = [];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawRedDot();
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    drawnPoints.push({ x, y });
    drawingSound.currentTime = 0;
    drawingSound.play();
}

function draw(event) {
    if (!isDrawing) {
        return;
    }

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    drawnPoints.push({ x, y });

    ctx.beginPath();
    ctx.moveTo(drawnPoints[drawnPoints.length - 2].x, drawnPoints[drawnPoints.length - 2].y);
    ctx.lineTo(x, y);
    ctx.stroke();
}

function stopDrawing() {
    if (!isDrawing) {
        return;
    }

    isDrawing = false;
    drawingSound.pause();
    drawingSound.currentTime = 0;

    if (drawnPoints.length > 2) {
        if (isPointInPolygon(centerPoint, drawnPoints)) {
            calculateScore();
        } else {
            scoreDisplay.textContent = '0%';
            bestScoreDisplay.textContent = `${Math.round(bestSessionScore)}%`;
            alert('The red dot is not inside your circle!');
        }
    }
}

function resetGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    scoreDisplay.textContent = '0%';
    drawRedDot();
    drawnPoints = [];
}

function calculateScore() {
    // 1. Find the center and radius of the drawn shape
    const centerX = drawnPoints.reduce((sum, p) => sum + p.x, 0) / drawnPoints.length;
    const centerY = drawnPoints.reduce((sum, p) => sum + p.y, 0) / drawnPoints.length;
    const distances = drawnPoints.map(p => Math.sqrt(Math.pow(p.x - centerX, 2) + Math.pow(p.y - centerY, 2)));
    const avgRadius = distances.reduce((sum, d) => sum + d, 0) / distances.length;

    // 2. Compare the drawn shape to a perfect circle
    const variance = distances.map(d => Math.pow(d - avgRadius, 2));
    const totalVariance = variance.reduce((sum, v) => sum + v, 0);
    const score = Math.max(0, 100 - (totalVariance / (drawnPoints.length * Math.pow(avgRadius, 2))) * 2500);

    // 3. Display the score and the perfect circle overlay
    scoreDisplay.textContent = `${Math.round(score)}%`;
    drawPerfectCircle(centerX, centerY, avgRadius);

    // Update best score for the session
    if (score > bestSessionScore) {
        bestSessionScore = score;
        sessionStorage.setItem('bestScore', bestSessionScore);
        bestScoreDisplay.textContent = `${Math.round(bestSessionScore)}%`;
    }
}

function drawPerfectCircle(x, y, radius) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(76, 175, 80, 0.7)';
    ctx.lineWidth = 2;
    ctx.stroke();
}

// Ray-casting algorithm to check if a point is inside a polygon
function isPointInPolygon(point, polygon) {
    let isInside = false;
    const x = point.x;
    const y = point.y;
    let i, j;
    for (i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        const xi = polygon[i].x, yi = polygon[i].y;
        const xj = polygon[j].x, yj = polygon[j].y;
        
        const intersect = ((yi > y) != (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) {
            isInside = !isInside;
        }
    }
    return isInside;
}

// Initialize the game
init();
