# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
from src.graph import build_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """Enable debug level logging for more detailed execution information."""
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()


async def run_agent_workflow_async(
    user_input: str,
    mcp_server_json: str,
    debug: bool = False,
    max_plan_iterations: int = 1,
    max_step_num: int = 3,
    enable_background_investigation: bool = True,
):
    """Run the agent workflow asynchronously with the given user input.

    Args:
        user_input: The user's query or request
        debug: If True, enables debug level logging
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
        enable_background_investigation: If True, performs web search before planning to enhance context

    Returns:
        The final state after the workflow completes
    """
    if not user_input:
        raise ValueError("Input could not be empty")

    if debug:
        enable_debug_logging()

    logger.info(f"Starting async workflow with user input: {user_input}")

    yield f"Starting async workflow with user input: {user_input}"

    initial_state = {
        # Runtime Variables
        "messages": [{"role": "user", "content": user_input}],
        "auto_accepted_plan": True,
        "enable_background_investigation": enable_background_investigation,
    }
    config = {
        "configurable": {
            "thread_id": "default",
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "mcp_settings": {
                "servers": {
                    "mcp-github-trending": {
                        "transport": "stdio",
                        "command": "uvx",
                        "args": ["mcp-github-trending"],
                        "enabled_tools": ["get_github_trending_repositories"],
                        "add_to_agents": ["researcher"],
                    },
                }
            },
        },
        "recursion_limit": 100,
    }
    
    mcp_server_config = json.loads(mcp_server_json)
    for server_name, server_config in mcp_server_config.items():
        config["configurable"]["mcp_settings"]["servers"][server_name] = server_config
        config["configurable"]["mcp_settings"]["servers"][server_name]["add_to_agents"] = ["researcher"]

    # import code; code.interact(local=dict(globals(), **locals()))
    
    last_message_cnt = 0
    async for event in graph.astream_events(
        input=initial_state, config=config, stream_mode="custom"
    ):
        if event["name"] == "deep_research_log_info":
            yield f"event: {event["name"]}\n"
            yield f"data: {json.dumps(event['data'])}\n\n"
        # try:
        #     if isinstance(s, dict) and "messages" in s:
        #         if len(s["messages"]) <= last_message_cnt:
        #             continue
        #         last_message_cnt = len(s["messages"])
        #         message = s["messages"][-1]
        #         if isinstance(message, tuple):
        #             yield (message)
        #         else:
        #             yield (message.pretty_print())
        #     else:
        #         # For any other output format
        #         yield (f"Output: {s}")

        # except Exception as e:
        #     logger.error(f"Error processing stream output: {e}")
        #     print(f"Error processing output: {str(e)}")


    logger.info("Async workflow completed successfully")
    yield "event: final_report\n"
    try:
        yield f"data: {json.dumps({'message': event['data']['output']['final_report']})}\n\n"
    except Exception as e:
        import code; code.interact(local=dict(globals(), **locals()))
        logger.error(f"Error processing output: {event['data']["output"]}")


if __name__ == "__main__":
    print(graph.get_graph(xray=True).draw_mermaid())
