import mcp
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from agents import FunctionTool
import json

def clean_schema(schema):
    """Clean up schema to ensure it's valid for OpenAI."""
    if not isinstance(schema, dict):
        return schema
        
    # Remove invalid properties from the schema
    invalid_props = ['default', 'examples', 'enum']
    cleaned_schema = {}
    
    for key, value in schema.items():
        if key == 'properties' and isinstance(value, dict):
            # Clean properties recursively
            cleaned_props = {}
            for prop_name, prop_schema in value.items():
                cleaned_props[prop_name] = clean_schema(prop_schema)
            cleaned_schema[key] = cleaned_props
            # Ensure all properties are required
            cleaned_schema['required'] = list(cleaned_props.keys())
        elif key == 'required' and isinstance(value, list):
            # Skip the original required array as we're requiring all properties
            continue
        elif key not in invalid_props:
            # Recursively clean other objects
            cleaned_schema[key] = clean_schema(value) if isinstance(value, dict) else value
    
    return cleaned_schema

async def list_tools_stdio(params):
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return tools_result.tools

async def call_mcp_tool_stdio(params, tool_name, tool_args):
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result

async def list_tools_sse(url):
    async with sse_client(url) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return tools_result.tools

async def call_mcp_tool_sse(url, tool_name, tool_args):
    async with sse_client(url) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result

async def get_tools_openai_stdio(params):
    openai_tools = []
    for tool in await list_tools_stdio(params):
        # Clean and prepare the schema
        schema = clean_schema(tool.inputSchema)
        schema['additionalProperties'] = False
        
        openai_tool = FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_mcp_tool_stdio(params, toolname, json.loads(args))
        )
        openai_tools.append(openai_tool)
    return openai_tools

async def get_tools_openai_sse(url):
    openai_tools = []
    for tool in await list_tools_sse(url):
        # Clean and prepare the schema
        schema = clean_schema(tool.inputSchema)
        schema['additionalProperties'] = False
        
        openai_tool = FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_mcp_tool_sse(url, toolname, json.loads(args))
        )
        openai_tools.append(openai_tool)
    return openai_tools 