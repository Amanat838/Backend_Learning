const os = require("node:os");

function convertBytesToGB(bytes) {
  return bytes / (1024 * 1024 * 1024);
}

const name = process.argv[2] ?? "Stranger"
console.log(`Helloo ${name}`);
console.log("Node version: ",process.version);
console.log("Platform: ",process.platform);
console.log("CPU cores: ",os.cpus().length);
console.log(`${convertBytesToGB(os.freemem()).toFixed(1)} GB free of ${convertBytesToGB(os.totalmem()).toFixed(1)} GB`);
console.log(`Uptime of this process: ${process.uptime().toFixed(2)} s`)
console.log('DATE', new Date())
