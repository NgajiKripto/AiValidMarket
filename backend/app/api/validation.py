import threading
from concurrent.futures import ThreadPoolExecutor

from flask import jsonify, request

from app import limiter
from app.api import validation_bp
from app.config import Config
from app.middleware.security import require_api_key
from app.models.memory import MemoryType
from app.models.task import TaskManager, TaskStatus
from app.services.idea_analyzer import IdeaAnalyzer
from app.services.memory_service import MemoryService
from app.services.web_researcher import WebResearcher
from app.services.report_generator import ReportGenerator
from app.utils.llm_client import LLMClient
from app.utils.logger import info, error
from app.utils.sanitizer import sanitize_input, sanitize_log_input, validate_chat_history


task_manager = TaskManager()
memory_service = MemoryService()

# Thread pool and concurrency control
executor = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)
_validation_semaphore = threading.Semaphore(Config.MAX_CONCURRENT_VALIDATIONS)


def _run_validation(task_id: str, idea_text: str):
    """Run the full validation pipeline in a background thread."""
    try:
        # Initialize services
        llm_client = LLMClient(
            api_key=Config.LLM_API_KEY,
            base_url=Config.LLM_BASE_URL,
            model=Config.LLM_MODEL_NAME,
        )
        analyzer = IdeaAnalyzer(llm_client)
        researcher = WebResearcher(Config.SERPER_API_KEY)
        report_gen = ReportGenerator(llm_client)

        # Inject memory context from past validations
        memory_context = ""
        try:
            memory_context = memory_service.inject_context(idea_text)
        except Exception as e:
            error(f"Memory context injection failed (non-fatal): {e}")

        # Step 1: Analyze the idea
        task_manager.update_task(
            task_id, status=TaskStatus.PROCESSING, progress=10,
            message="Analyzing your idea..."
        )
        analysis = analyzer.analyze_idea(idea_text)

        # Step 2: Web research
        task_manager.update_task(
            task_id, progress=30, message="Researching the market..."
        )
        research_results = []

        keywords = analysis.get("keywords", [])
        if keywords and Config.SERPER_API_KEY:
            research_results.extend(researcher.search_keywords(keywords[:5]))

            task_manager.update_task(
                task_id, progress=50, message="Gathering additional data..."
            )
            # Get PAA and news
            main_query = keywords[0] if keywords else idea_text[:50]
            research_results.extend(researcher.get_people_also_ask(main_query))
            research_results.extend(researcher.search_news(main_query))
            research_results.extend(researcher.search_social(main_query))

        # Step 3: Generate report
        task_manager.update_task(
            task_id, progress=75, message="Generating validation report..."
        )
        report = report_gen.generate_report(
            idea_text, analysis, research_results, memory_context=memory_context
        )

        # Complete
        final_result = {
            "idea": idea_text,
            "analysis": analysis,
            "research_results_count": len(research_results),
            "report": report,
        }
        task_manager.complete_task(task_id, final_result)
        info(f"Validation task {task_id} completed successfully")

        # Capture validation result as memory
        try:
            session = memory_service.start_session(idea_text)
            tags = analysis.get("keywords", [])[:5] + analysis.get("categories", [])[:3]
            executive_summary = report.get("executive_summary", "") if isinstance(report, dict) else ""
            report_content = f"Validation of: {idea_text}\n{executive_summary}"
            memory_service.remember(
                content=report_content,
                memory_type=MemoryType.SEMANTIC,
                importance=0.7,
                session_id=session.id,
                tags=tags,
                metadata={"task_id": task_id},
            )
            summary = executive_summary or f"Validated idea: {idea_text[:100]}"
            memory_service.end_session(session.id, summary)
            memory_service.consolidate()
        except Exception as e:
            error(f"Memory capture failed (non-fatal): {e}")

    except Exception as e:
        error(f"Validation task {task_id} failed: {e}")
        task_manager.fail_task(task_id, str(e))
    finally:
        _validation_semaphore.release()


@validation_bp.route("/validate", methods=["POST"])
@require_api_key
@limiter.limit(Config.RATE_LIMIT_VALIDATE)
def validate_idea():
    """Start an async idea validation task."""
    data = request.get_json()
    if not data or not data.get("idea"):
        return jsonify({"error": "Missing 'idea' field"}), 400

    idea_text = sanitize_input(data["idea"])

    if len(idea_text) > 5000:
        return jsonify({"error": "Idea text must be 5000 characters or fewer"}), 400

    # Enforce concurrent validation limit
    if not _validation_semaphore.acquire(blocking=False):
        return jsonify({"error": "Too many concurrent validations"}), 429

    task = task_manager.create_task()

    # Run validation in thread pool
    executor.submit(_run_validation, task.id, idea_text)

    sanitized_idea = sanitize_log_input(idea_text, max_length=50)
    info(f"Started validation task {task.id} for idea: {sanitized_idea}")
    return jsonify({"task_id": task.id, "status": task.status.value}), 202


@validation_bp.route("/status/<task_id>", methods=["GET"])
def get_status(task_id):
    """Get the status of a validation task."""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@validation_bp.route("/result/<task_id>", methods=["GET"])
def get_result(task_id):
    """Get the result of a completed validation task."""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    if task.status != TaskStatus.COMPLETED:
        return jsonify({
            "error": "Task not yet completed",
            "status": task.status.value,
            "progress": task.progress,
        }), 202
    return jsonify(task.to_dict())


@validation_bp.route("/chat", methods=["POST"])
@require_api_key
def chat():
    """Handle follow-up chat about a validation result."""
    data = request.get_json()
    if not data or not data.get("task_id") or not data.get("message"):
        return jsonify({"error": "Missing 'task_id' or 'message' field"}), 400

    task_id = data["task_id"]
    message = data["message"]
    chat_history = validate_chat_history(data.get("chat_history", []))

    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task.status != TaskStatus.COMPLETED:
        return jsonify({"error": "Validation not yet completed"}), 400

    try:
        llm_client = LLMClient(
            api_key=Config.LLM_API_KEY,
            base_url=Config.LLM_BASE_URL,
            model=Config.LLM_MODEL_NAME,
        )

        # Build context from the validation result
        result = task.result
        context = f"""You are discussing a market validation report for this idea: {result.get('idea', '')}

Report summary: {result.get('report', {}).get('executive_summary', 'No report available')}
Market viability score: {result.get('report', {}).get('market_viability_score', 'N/A')}/10

Answer the user's follow-up questions about this validation based on the data gathered."""

        # Enrich context with relevant past memories
        try:
            memory_results = memory_service.recall(message, limit=3)
            if memory_results:
                past_insights = "\n".join(
                    f"- {r.entry.summary}" for r in memory_results
                )
                context += f"\n\nPast validation insights:\n{past_insights}"
        except Exception as e:
            error(f"Memory recall in chat failed (non-fatal): {e}")

        messages = [{"role": "system", "content": context}]
        messages.extend(chat_history)

        response = llm_client.chat(messages, temperature=0.7)
        return jsonify({"response": response})

    except Exception as e:
        error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500
