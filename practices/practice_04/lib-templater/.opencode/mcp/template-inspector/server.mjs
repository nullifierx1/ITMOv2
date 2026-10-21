import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import { z } from "zod";

const PROJECT_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_-]*$/;
const TEMPLATE_HEADER = "include/__PROJECT_NAME__/foo.h";
const LEGACY_FLAT_HEADER = "include/foo.h";

const server = new McpServer({
  name: "template-inspector",
  version: "1.0.0",
});

server.registerTool(
  "template_inspect",
  {
    description:
      "Inspect the public include layout expected from the C++ library template.",
    inputSchema: {
      projectName: z.string(),
    },
  },
  async ({ projectName }) => {
    if (!PROJECT_NAME_PATTERN.test(projectName)) {
      return {
        content: [
          {
            type: "text",
            text: "Invalid projectName: expected a simple project identifier",
          },
        ],
        isError: true,
      };
    }

    const expectedGeneratedHeader = `include/${projectName}/foo.h`;
    const templateHeaderExists = existsSync(resolve(process.cwd(), TEMPLATE_HEADER));
    const legacyFlatHeaderExists = existsSync(
      resolve(process.cwd(), LEGACY_FLAT_HEADER),
    );
    const result = {
      project_name: projectName,
      template_header: TEMPLATE_HEADER,
      expected_generated_header: expectedGeneratedHeader,
      template_header_exists: templateHeaderExists,
      legacy_flat_header_exists: legacyFlatHeaderExists,
      template_ready: templateHeaderExists && !legacyFlatHeaderExists,
    };

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result),
        },
      ],
    };
  },
);

const transport = new StdioServerTransport();

server.connect(transport).catch((error) => {
  console.error("Failed to start template-inspector MCP server:", error);
  process.exitCode = 1;
});
