from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str
    mcp_server_json: str
    debug: bool = False
    max_plan_iterations: int = 1
    max_step_num: int = 3
    enable_background_investigation: bool = True