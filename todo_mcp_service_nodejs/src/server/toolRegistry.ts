import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";



const FASTAPI_APP_URL = "http://0.0.0.0:9001";
import { z } from "zod";



export const CreateTodoInputZodTypeSchema = z
  .object({
    title: z.string(),
    description: z.string(),
    completed: z.boolean().optional(),
  })
  .strict();
export const DeleteTodoInputZodTypeSchema = z
  .object({ id: z.number() })
  .strict();


export class TodoMCPToolRegistry {
  constructor(private server: McpServer) {
    this.registerTools();
  }

  private registerTools() {

    this.server.tool(
      "get_all_todos", "Get all todos",
      {}, // No input schema for this tool
      async () => {
        const res = await fetch(`${FASTAPI_APP_URL}/todos`);
        const data = await res.json();
        return {
          content: [{ type: "text", text: JSON.stringify(data) }]
        };
      }
    );

    this.server.tool(
      "create_todo", "Create a Todo",
      CreateTodoInputZodTypeSchema.shape,
      async (input) => {
        const res = await fetch(`${FASTAPI_APP_URL}/todos`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(input)
        });
        const data = await res.json();
        return {
          content: [{ type: "text", text: JSON.stringify(data) }]
        };
      }
    );

    this.server.tool(
      "delete_todo", "Delete a todo by its ID",
      DeleteTodoInputZodTypeSchema.shape,
      async ({ id }) => {
        const res = await fetch(`${FASTAPI_APP_URL}/todos/${id}`, {
          method: "DELETE"
        });
        const data = await res.json();
        return {
          content: [
            {
              type: "text", // ✅ Only these are valid: "text", "image", "audio", "resource"
              text: JSON.stringify(data)
            }
          ]
        };
      }
    );

  }
}
