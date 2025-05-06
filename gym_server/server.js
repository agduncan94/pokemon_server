const express = require('express');
const { exec } = require('child_process');
const app = express();
const port = 4000;

app.get('/api/stats', (req, res) => {


  // Execute the 'top' command to get server stats
  exec('top -b -n 1 | grep "MiB Mem :"', (err, stdout, stderr) => {
    if (err) {
      console.error(`Error executing top command: ${stderr}`);
      return res.status(500).json({ error: 'Failed to retrieve server stats' });
    }

    // Parse memory usage from the 'top' command output
    const memoryStats = stdout.match(/([\d.]+)\s+total,\s+([\d.]+)\s+free,\s+([\d.]+)\s+used,\s+([\d.]+)\s+buff\/cache/);
    console.log(stdout);
    const totalMemory = parseInt(memoryStats[1], 10);
    const usedMemory = parseInt(memoryStats[2], 10);
    const freeMemory = parseInt(memoryStats[3], 10);

    // Create user objects that store the stats
    const user1 = {
      name: "Ash",
      cpuUsage: 10,
      memoryUsage: 20,
      gpuMemoryUsage: 30
    };

    const user2 = {
      name: "Misty",
      cpuUsage: 15,
      memoryUsage: 25,
      gpuMemoryUsage: 35
    };

    const user3 = {
      name: "Brock",
      cpuUsage: 20,
      memoryUsage: 30,
      gpuMemoryUsage: 40
    };

    // Create users array
    users = [user1, user2, user3];

    // Create global usage object
    globalUsage = {
      cpuUsage: 50,
      memoryUsage: usedMemory,
      freeMemory: freeMemory,
      totalMemory: totalMemory,
      diskUsage: 80,
      networkUsage: 60,
      gpuUsage: 80
    };

    res.json({
      users: users,
      globalUsage: globalUsage
    });
  });
});


app.listen(port, () => {
  console.log(`Pokemon server running at http://localhost:${port}`);
});
