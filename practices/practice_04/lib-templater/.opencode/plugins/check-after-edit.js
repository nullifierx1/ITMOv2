// OpenCode V2 plugin: verification hook after file-changing tools
// Adds PASS/FAIL for "sh scripts/check.sh" to the tool result content

import { Plugin } from "@opencode/plugin"
import { spawn } from "node:child_process"

export default Plugin.define({
    id: "check-after-edit",
    async setup(ctx) {
        const fileTools = new Set(["write", "edit", "apply_patch"]) // V2 docs: use apply_patch id

        await ctx.tool.hook("execute.after", async (event) => {
            // event.tool: string id of the tool
            if (!fileTools.has(event.tool)) return

            const cwd = ctx.location.directory
            const child = spawn("bash", ["scripts/check.sh"], {
                cwd,
                env: { ...process.env },
                stdio: ["ignore", "pipe", "pipe"],
                shell: false,
            })

            const out = []
            const err = []
            await new Promise((resolve) => {
                child.stdout.on("data", (d) => out.push(d))
                child.stderr.on("data", (d) => err.push(d))
                child.on("close", () => resolve())
            })

            const code = child.exitCode ?? 1
            const stdout = Buffer.concat(out).toString("utf8")
            const stderr = Buffer.concat(err).toString("utf8")

            // Modify event.result content to include verification outcome
            const note = code === 0
                ? "[verification] PASS: scripts/check.sh"
                : "[verification] FAIL: scripts/check.sh\n" +
                  (stdout ? `STDOUT:\n${stdout}\n` : "") +
                  (stderr ? `STDERR:\n${stderr}\n` : "")

            const prev = event.result?.content ?? ""
            const merged = prev ? `${prev}\n${note}` : note
            event.result = { ...(event.result || {}), content: merged }
        })
    },
})
