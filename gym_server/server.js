const express = require('express');
const { exec } = require('child_process');
const app = express();
const port = 4000;

app.get('/api/stats', (req, res) => {
  // Create user objects that store the stats
  const user1 = {
    name: "Andrew",
    cpuUsage: 10,
    memoryUsage: 20,
    gpuMemoryUsage: 30
  };

  const user2 = {
    name: "Alex",
    cpuUsage: 15,
    memoryUsage: 25,
    gpuMemoryUsage: 35
  };

  const user3 = {
    name: "Denise",
    cpuUsage: 20,
    memoryUsage: 30,
    gpuMemoryUsage: 40
  };

  // Create users array
  users = [user1, user2, user3];

  // Create global usage object
  globalUsage = {
    cpuUsage: 50,
    memoryUsage: 70,
    diskUsage: 80,
    networkUsage: 60,
    gpuUsage: 80,
    name: 'Valrhona'
  };

  res.json({
    users: users,
    globalUsage: globalUsage
  });
});


app.listen(port, () => {
  console.log(`Pokemon server running at http://localhost:${port}`);
});
