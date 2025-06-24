import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
// File: src/server/mcpServer.ts
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import "reflect-metadata"; // ✅ must be first

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import express from "express";
import { TodoMCPToolRegistry } from "./toolRegistry";

export class MCPServerApp {
    private server: McpServer;
    private expressApp: express.Application;
    private readonly port: number = 9002;

    constructor() {
        this.server = new McpServer({
            name: "Project management MCP server",
            version: "1.0.0"
        });
        new TodoMCPToolRegistry(this.server);
        // new WorkspaceMCPToolRegistry(this.server);
        // new TaskColumnValuesMCPToolRegistry(this.server);
        // new BoardMCPToolRegistry(this.server);
        // new BoardTaskMCPToolRegistry(this.server);
        // new BoardGroupMCPToolRegistry(this.server);
        // new BoardColumnMCPToolRegistry(this.server);

        this.expressApp = express();

        this.setupRoutes();
    }

    private setupRoutes() {
        this.expressApp.use(express.json());
        const transports = {
            streamable: {} as Record<string, StreamableHTTPServerTransport>,
            sse: {} as Record<string, SSEServerTransport>
        };


        this.expressApp.get('/sse', async (req, res) => {
            // Create SSE transport for legacy clients
            console.log("Received SSE message GET");
            console.log(req.headers);
            const transport = new SSEServerTransport('/sse', res);
            transports.sse[transport.sessionId] = transport;

            res.on("close", () => {
                delete transports.sse[transport.sessionId];
            });

            await this.server.connect(transport);
        });
        this.expressApp.post('/sse', async (req, res) => {
            console.log("Received SSE message POST");
            console.log("req.body: ", req.body)
            console.log("")
            const sessionId = req.query.sessionId as string;
            console.log("sessionId: ", sessionId)
            const transport = transports.sse[sessionId];
            // print headers
            // console.log(req.headers);
            if (!transport) {
                res.status(404).send(`No SSE session found for sessionId: ${sessionId}`);
                return;
            }

            try {
                await transport.handleMessage(req.body
                //   ,{
                //     authInfo: {
                //         token: req.headers.authorization || "abcdef",
                //         clientId: "",
                //         scopes: []
                //     }
                // }
              ); // ✅ correct method
                res.sendStatus(200);
            } catch (err) {
                console.error("❌ Error handling client message:", err);
                res.status(500).send("Internal Server Error");
            }
        });

    }



    public start() {
        this.expressApp.listen(this.port, () => {
            console.log(`MCP server running on port ${this.port}`);
        });
    }
}

// Entrypoint
new MCPServerApp().start();
