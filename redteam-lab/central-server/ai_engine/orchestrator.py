import logging
import asyncio
import json
from sqlalchemy.orm import Session
from database.db import Campaign, CampaignMemory, AIDecisionLog, Task, SessionLocal
from ai_engine.planner import determine_next_phase
from ai_engine.task_selector import select_next_task
from ai_engine.tool_selector import select_tool_for_action
from api.websocket.manager import manager
from config import settings

logger = logging.getLogger("ai_engine.orchestrator")

async def run_campaign_loop(campaign_id: str):
    """The main autonomous loop for a given campaign.
    Observe -> Reason -> Act loop.
    In a real system, this would be managed by Celery/Redis tasks to avoid blocking.
    """
    db = SessionLocal()
    
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign or campaign.status != "running":
            logger.info(f"Campaign {campaign_id} not running, exiting loop.")
            return

        memory = db.query(CampaignMemory).filter(CampaignMemory.campaign_id == campaign_id).first()
        if not memory:
            memory = CampaignMemory(campaign_id=campaign_id)
            db.add(memory)
            db.commit()

        step_count = 0
        while step_count < settings.AI_MAX_STEPS:
            # 1. PLAN: Check overall phase
            phase_decision = await determine_next_phase(db, campaign_id)
            if phase_decision.get("is_complete"):
                logger.info(f"Campaign {campaign_id} deemed complete by Planner.")
                campaign.status = "completed"
                db.commit()
                break

            # 2. SELECT TASK: What exactly to do next?
            task_decision = await select_next_task(db, campaign_id)
            
            # Log AI Decision
            log_entry = AIDecisionLog(
                campaign_id=campaign_id,
                step=step_count,
                state_summary=f"Phase: {memory.phase}",
                reasoning=task_decision.get("reasoning", ""),
                action=task_decision.get("action", "unknown")
            )
            db.add(log_entry)
            db.commit()
            if task_decision.get("action") == "wait" or not task_decision.get("action"):
                logger.info(f"AI decided to wait or failed. Stopping loop.")
                break

            # 3. SELECT TOOL: Map action to concrete tool
            tool_decision = await select_tool_for_action(task_decision)
            tool_name = tool_decision.get("tool_name")
            tool_params = tool_decision.get("params", {})
            
            if not tool_name:
                logger.info(f"No suitable tool found for action {task_decision.get('action')}. Stopping.")
                break
                
            log_entry.tool_name = tool_name
            log_entry.tool_params = tool_params
            db.commit()

            await manager.broadcast_to_campaign(campaign_id, {
                "type": "ai.thought",
                "campaign_id": campaign_id,
                "step": step_count,
                "observation": f"Phase: {memory.phase}",
                "reasoning": task_decision.get("reasoning", ""),
                "action": task_decision.get("action", "unknown"),
                "tool": tool_name
            })


            # 4. EXECUTE: Create Task for Agent
            new_task = Task(
                campaign_id=campaign_id,
                module=tool_name,
                params=tool_params
            )
            db.add(new_task)
            db.commit()
            
            logger.info(f"Created task {new_task.id} ({tool_name}) for campaign {campaign_id}. Waiting for agent...")
            
            # In a real async system, we would sleep and wait for a webhook/event from the agent.
            # Here we simulate waiting for task completion.
            max_wait = settings.TOOL_EXECUTION_TIMEOUT
            waited = 0
            while waited < max_wait:
                db.refresh(new_task)
                if new_task.status in ["completed", "failed"]:
                    break
                await asyncio.sleep(5)
                waited += 5
                
            if new_task.status not in ["completed", "failed"]:
                logger.warning(f"Task {new_task.id} timed out. Marking failed.")
                new_task.status = "failed"
                new_task.result = {"error": "timeout"}
                db.commit()
            elif new_task.status == "completed":
                # 5. ANALYZE: Use LLM to extract findings and update memory
                target_ip = tool_params.get("target") or tool_params.get("domain")
                raw_out = json.dumps(new_task.result) if isinstance(new_task.result, dict) else str(new_task.result)
                
                # Validate output first to prevent analyzer processing error strings
                from ai_engine.validator import validate_tool_output
                is_valid = await validate_tool_output(tool_name, raw_out)
                if not is_valid:
                    logger.warning(f"Task {new_task.id} output failed validation. Marking as failed to prevent planner loops.")
                    new_task.status = "failed"
                    db.commit()
                else:
                    logger.info(f"Task {new_task.id} completed. Running Analyzer...")
                    try:
                        from ai_engine.analyzer import analyze_tool_output
                        await analyze_tool_output(db, campaign_id, new_task.id, tool_name, raw_out, target_ip)
                    except Exception as e:
                        logger.error(f"Analyzer failed for task {new_task.id}: {e}")

            step_count += 1
            
        if step_count >= settings.AI_MAX_STEPS:
            logger.warning(f"Campaign {campaign_id} reached max steps ({settings.AI_MAX_STEPS}). Stopping.")
            campaign.status = "paused"
            db.commit()
            
    except Exception as e:
        logger.error(f"Error in orchestrator loop for campaign {campaign_id}: {e}")
    finally:
        db.close()
