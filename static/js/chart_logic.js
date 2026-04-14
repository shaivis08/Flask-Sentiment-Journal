

const ctx = document.getElementById('myChart').getContext('2d');
const labels = chartData.labels
const scores = chartData.sentiment

new Chart(ctx, {
    type: 'line', 
    data: {
        labels: labels, 
        datasets: [{
            label: 'Your Weekly Mood Chart',
            data: scores, 
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
            fill: false
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: false,
                min: -1,
                max: 1
            }
        }
    }
});



