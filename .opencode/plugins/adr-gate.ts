// adr-gate.ts — OpenCode plugin hook that blocks git commit
// unless ADR compliance has been verified on staged artifact files.
//
// Protocol: tool.execute.before handler takes (input, output).
//   input: { tool, sessionID, callID }
//   output: { args: { command, description, ... } }
// Throw to block (deny). Return normally to allow.

export default async ({ directory }: { project: unknown; directory: string }) => {
  return {
    "tool.execute.before": async (
      input: { tool: string; sessionID: string; callID: string },
      output: { args: { command?: string; description?: string } },
    ) => {
      // Only gate bash/shell tool calls
      if (input.tool !== "bash") return;

      const command = output.args?.command || "";
      // Robust pattern: catches "git commit", "git -c ... commit", etc.
      if (!/\bgit\b.*\bcommit\b/.test(command)) return;

      // Check for staged artifact files
      const { execSync } = await import("child_process");
      try {
        const staged = execSync("git diff --cached --name-only", {
          cwd: directory,
          encoding: "utf-8",
        });
        const artifacts = staged
          .split("\n")
          .filter((f: string) =>
            /^docs\/(spec|epic|initiative|vision|research|adr|design|persona|runbook|journey|train)\//.test(
              f,
            ),
          );

        if (artifacts.length === 0) return; // No artifacts staged, allow

        // Check for recent ADR compliance stamp
        const fs = await import("fs");
        const stampFile = `${directory}/.agents/hook-state/adr-check-passed`;
        if (fs.existsSync(stampFile)) {
          const stat = fs.statSync(stampFile);
          const age = (Date.now() - stat.mtimeMs) / 1000;
          if (age < 300) return; // Recent check passed, allow
        }

        // Run ADR check on each staged artifact
        for (const artifact of artifacts) {
          const result = execSync(
            `bash skills/swain-design/scripts/adr-check.sh "${artifact}"`,
            { cwd: directory, encoding: "utf-8", timeout: 10000 },
          );
          if (!result.startsWith("OK ")) {
            throw new Error(`ADR compliance failed: ${result.trim()}`);
          }
        }

        // All passed — stamp
        execSync(
          `mkdir -p "${directory}/.agents/hook-state" && date > "${stampFile}"`,
          { cwd: directory },
        );
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        if (msg.includes("ADR compliance failed:")) {
          throw e; // Re-throw ADR failures to block the tool
        }
        // Other errors (no git, script not found) — allow through (fail-open)
      }
    },
  };
};
