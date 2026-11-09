import { spawn } from "node:child_process";

const args = process.argv.slice(2);
const portIndex = args.indexOf("--port");
const hostIndex = args.indexOf("--host");
const port = portIndex >= 0 ? args[portIndex + 1] : "3000";
const host = hostIndex >= 0 ? args[hostIndex + 1] : "127.0.0.1";
const child = spawn(process.execPath, ["node_modules/next/dist/bin/next", "dev", "-H", host, "-p", port], { stdio: "inherit" });
for (const signal of ["SIGTERM", "SIGINT"]) process.on(signal, () => child.kill(signal));
child.on("exit", code => process.exit(code ?? 0));
