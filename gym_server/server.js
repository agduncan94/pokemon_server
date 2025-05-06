const express = require('express');
const { execSync } = require('child_process');
const app = express();
const port = 4000;
const serverErrorStatus = 500;
function getUserNamesFromHome() {
  return ["root", "Misty"]
}
function getTopOutputs(userNames) {
  
  const globalMemoryUsage = 0;
  const globalCpuUsage = 0;
  const userCpuNMemUsage = {}

  const cmd = `ps -eo user,%cpu,rss --no-headers`;
  const output = execSync(cmd, { encoding: 'utf-8' });
  output.trim().split('\n').forEach(line => {
    const [user, cpuStr, memStr] = line.trim().split(/\s+/, 3);
    if (!userNames.find(user_ => user_ === user)) {
      return
    }
    const cpu = parseFloat(cpuStr);
    const mem = parseInt(memStr) * 1024; // rss in KB → bytes

    globalCpuUsage += cpu;
    globalMemoryUsage += mem;

    if (!userCpuNMemUsage[user]) {
      userCpuNMemUsage[user] = { cpuUsage: 0, memUsage: 0 };
    }

    userCpuNMemUsage[user].cpuUsage += cpu;
    userCpuNMemUsage[user].memUsage += mem;
  });
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
    const userNames = getUserNamesFromHome()
    const { globalMemoryUsage, globalCpuUsage, userCpuNMemUsage } = getTopOutputs(userNames)
    const { globalGpuUsage, userGpuUsage } = getNvidiaSmiOutputs()
    const globalNetworkUsage = getNetworkUsage()
    const globalDiskUsage = getDiskUsage()
    // Create users array
    users = userNames.map(name => ({
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
