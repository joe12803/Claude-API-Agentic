import os
import asyncio
import json
import logging
import re
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from claude_webapi import ClaudeClient
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude-bridge")
load_dotenv()

app = FastAPI(title="Hermes Agentic Bridge v4.0")
security = HTTPBearer()
ACCOUNTS_FILE = "/home/joe1280/Claude-API/accounts.json"
AUTH_TOKEN="sk-123456"

class ChatCompletionRequest(BaseModel):
    model: str = "claude-sonnet-4-6"
    messages: List[dict]
    stream: bool = False

def format_openai_sse(content: str, model: str, finish_reason: Optional[str] = None):
    data = {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion.chunk",
        "created": 1714723200,
        "model": model,
        "choices": [{"index": 0, "delta": {"content": content} if content else {}, "finish_reason": finish_reason}]
    }
    return f"data: {json.dumps(data)}\n\n"

async def execute_bash(command: str) -> str:
    logger.info(f"Executing: {command}")
    try:
        proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return (stdout.decode() + stderr.decode()).strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, token: str = Depends(security)):
    if token.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    with open(ACCOUNTS_FILE, "r") as f:
        acc = json.load(f)[0]
    
    user_query = request.messages[-1].get("content", "")

    async def agent_generator():
        async with ClaudeClient(acc["session_key"], acc.get("org_id")) as client:
            # --- 阶段 1: 提取指令 ---
            planner_prompt = f"User wants: {user_query}. If this requires system access, reply ONLY with a bash code block. If not, reply with 'NONE'."
            logger.info("Phase 1: Planning...")
            
            plan_resp = await client.generate_content(planner_prompt, model=request.model)
            plan_text = plan_resp.text
            
            execution_context = ""
            match = re.search(r"```bash\n(.*?)\n```", plan_text, re.DOTALL)
            if match:
                command = match.group(1).strip()
                yield format_openai_sse(f"🔍 [Executing]: `{command}`...\n", request.model)
                result = await execute_bash(command)
                execution_context = f"\nSystem execution result for `{command}`:\n{result}\n"
                yield format_openai_sse(f"✅ [Result Received]\n", request.model)
            
            # --- 阶段 2: 最终回复 ---
            final_prompt = f"Context: {execution_context}\nUser asked: {user_query}\nTask: Provide the final answer based on the context. Be concise and direct."
            logger.info("Phase 2: Answering...")
            
            async for chunk in client.generate_content_stream(final_prompt, model=request.model):
                yield format_openai_sse(chunk.text_delta, request.model)
            
            if execution_context:
                yield format_openai_sse(f"\n\n```text\n{execution_context}\n```", request.model)
        
        yield "data: [DONE]\n\n"

    # 非流式处理逻辑修复
    if not request.stream:
        full_text = ""
        async with ClaudeClient(acc["session_key"], acc.get("org_id")) as client:
            # 重复一遍 Agent 逻辑，但收集为完整文本
            planner_prompt = f"User wants: {user_query}. If this requires system access, reply ONLY with a bash code block. If not, reply with 'NONE'."
            plan_resp = await client.generate_content(planner_prompt, model=request.model)
            plan_text = plan_resp.text
            
            execution_context = ""
            match = re.search(r"```bash\n(.*?)\n```", plan_text, re.DOTALL)
            if match:
                command = match.group(1).strip()
                full_text += f"🔍 [Executing]: `{command}`...\n"
                result = await execute_bash(command)
                execution_context = f"\nSystem execution result for `{command}`:\n{result}\n"
                full_text += f"✅ [Result Received]\n"
            
            final_prompt = f"Context: {execution_context}\nUser asked: {user_query}\nTask: Provide the final answer based on the context."
            final_resp = await client.generate_content(final_prompt, model=request.model)
            full_text += final_resp.text
            
            if execution_context:
                full_text += f"\n\n```text\n{execution_context}\n```"
                
        return JSONResponse({
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "choices": [{"message": {"role": "assistant", "content": full_text.strip()}}]
        })

    return StreamingResponse(agent_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
