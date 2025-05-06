const express = require('express');
const { execSync } = require('child_process');
const app = express();
const port = 4000;
const serverErrorStatus = 500;
function getUserNamesFromHome() {
  return ["Ash", "Misty"]
}
function getTopOutputs() {
  const globalMemoryUsage = 0;
  const globalCpuUsage = 0;
  const userCpuNMemUsage = {}
  for ({userName, cpuUsage, memUsage} of [{
    userName: "Ash",
    cpuUsage: 0,
    memUsage: 0,
  },
  {
    userName: "Misty",
    cpuUsage: 0,
    memUsage: 0,
  }]) {
    userCpuNMemUsage[userName] = {cpuUsage: cpuUsage, memUsage: memUsage}
  }
  return { globalMemoryUsage, globalCpuUsage, userCpuNMemUsage }
}
function getNvidiaSmiOutputs() {
  const globalGpuUsage = 0;
  const userGpuUsage = {}
  for ({userName, gpuUsage} of [{
    userName: "Ash",
    gpuUsage: 0,
  },
  {
    userName: "Misty",
    gpuUsage: 0,
  }]) {
    userGpuUsage[userName] = gpuUsage
  }
  return { globalGpuUsage, userGpuUsage }
}
function getDiskUsage() {
  return 0
}
function getNetworkUsage() {
  return 0
}
app.get('/api/stats', (req, res) => {
  try {
    const userNamesFromHome = getUserNamesFromHome()
    const { globalMemoryUsage, globalCpuUsage, userCpuNMemUsage } = getTopOutputs()
    const { globalGpuUsage, userGpuUsage } = getNvidiaSmiOutputs()
    const globalNetworkUsage = getNetworkUsage()
    const globalDiskUsage = getDiskUsage()
    // Create users array
    users = userNamesFromHome.map(name => ({
      name: name,
      cpuUsage: userCpuNMemUsage[name].cpuUsage,
      memUsage: userCpuNMemUsage[name].memUsage,
      gpuUsage: userGpuUsage[name].gpuUsage
    }))

    // Create global usage object
    const globalUsage = {
      cpuUsage: globalCpuUsage,
      memoryUsage: globalMemoryUsage,
      diskUsage: globalDiskUsage,
      networkUsage: globalNetworkUsage,
      gpuUsage: globalGpuUsage 
    };

    res.json({
      users: users,
      globalUsage: globalUsage
    });
  } catch (err) {
    console.error(err);
    return res.status(serverErrorStatus).json({ error: 'Failed to retrieve server stats' });
  }
});


app.listen(port, () => {
  console.log(`Pokemon server running at http://localhost:${port}`);
});
