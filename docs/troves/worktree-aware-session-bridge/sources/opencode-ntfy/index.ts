import type { Plugin } from "@opencode-ai/plugin";
import {
  createNotificationPlugin,
  getBackendConfig,
  loadConfig,
} from "opencode-notification-sdk";
import { parseNtfyBackendConfig } from "./config.js";
import { createNtfyBackend } from "./backend.js";

const config = loadConfig("ntfy");
const backendRaw = getBackendConfig(config, "ntfy");
const backendConfig = parseNtfyBackendConfig(backendRaw);

const plugin: Plugin = async (input) => {
  const backend = createNtfyBackend(backendConfig, input.$);
  const sdkPlugin = createNotificationPlugin(backend, {
    backendConfigKey: "ntfy",
    config,
  });
  return sdkPlugin(input);
};

export default plugin;
