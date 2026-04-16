
const canvas = document.getElementById('sentiment-chart');


if (canvas) {
    const scores = JSON.parse(canvas.getAttribute('data-scores'));
    const pivotIndex = parseInt(canvas.getAttribute('data-pivot'));
    
    const labels = scores.map((_, index) => index); 

    const ctx = canvas.getContext('2d');

    new Chart(ctx, {
        type: 'line', 
        data: {
            labels: labels, 
            datasets: [{
                label: 'Sentiment Flow',
                data: scores, 
                segment: {
                    borderColor: ctx => {
                        const p0 = ctx.p0.parsed.y; 
                        const p1 = ctx.p1.parsed.y; 
                        return p1 < p0 ?  '#88ab75': '#d18a7a'; 
                    }
                },
                tension: 0.4,
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true, 
                    ticks: {
                        callback: function(value, index) {
                            // Only show these three specific labels
                            if (index === 0) return 'Start';
                            if (index === scores.length - 1) return 'End';
                            if (index === pivotIndex) return 'Turning Point';
                            return null;
                        }
                    },
                    grid: { display: false } 
                },
                y: {
                    min: -1,
                    max: 1,
                    ticks: { display: false }, 
                    grid: { color: 'rgba(0,0,0,0.05)' } 
                }
            },
            plugins: {
                legend: { display: false } 
            }
        }
    });
}
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

const context1 = document.getElementById('dayChart').getContext('2d');
const label = dayData.labels
const data = dayData.weekly_scores
new Chart (context1, {
    type: 'bar',
    data: {
        labels: label,
        datasets: [{
            label: 'Your Weekly Mood Trend',
            data: data,
            backgroundColor: 
                function(context) {
                    const value = context.dataset.data[context.dataIndex];
                    return value > 0 ? '#88ab75': '#d18a7a'; 
                },
            borderColor: function(context) {
                    const value = context.dataset.data[context.dataIndex];
                    return value > 0 ? '#88ab75': '#d18a7a'; 
                },
            borderWidth: function(context) {
                    const value = context.dataset.data[context.dataIndex];
                    return value === 0 ? 3 : 1; 
                },
            borderDash: function(context) {
                   const value = context.dataset.data[context.dataIndex];
                   return value === 0 ? [5, 5] : []; 
                },
            borderRadius: 10
        }],
    },
    options: {
            responsive: true,
            scales: {
            x: {
            grid: {
                lineWidth: 2,        
                color: '#4a4a4a'     
            },
            border: {
                width: 3            
            }
        },
            y: {
                grid: {
                   color: function(context) {
                if (context.tick.value === 0) {
                   return '#000000'; 
                }
               return 'rgba(0, 0, 0, 0.1)'; 
            },
    lineWidth: function(context) {
        return context.tick.value === 0 ? 3 : 1; 
    }
            },
             beginAtZero: false,
                min: -1,
                max: 1
            }
    }
    },
})
