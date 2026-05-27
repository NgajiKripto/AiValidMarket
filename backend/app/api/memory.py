from flask import jsonify, request

from app.api import memory_bp
from app.config import Config
from app.middleware.security import require_api_key
from app.models.memory import MemoryType
from app.services.memory_service import MemoryService
from app.utils.logger import info, error


memory_service = MemoryService()


@memory_bp.route("/sessions", methods=["GET"])
@require_api_key
def list_sessions():
    """List past validation sessions."""
    limit = request.args.get("limit", 10, type=int)
    limit = min(limit, Config.MAX_QUERY_LIMIT)
    offset = request.args.get("offset", 0, type=int)

    try:
        sessions = memory_service.get_session_history(limit=limit, offset=offset)
        session_list = [s.to_dict() for s in sessions]
        return jsonify(session_list)
    except Exception as e:
        error(f"Error listing sessions: {e}")
        return jsonify({"error": str(e)}), 500


@memory_bp.route("/sessions/<session_id>", methods=["GET"])
@require_api_key
def get_session(session_id):
    """Get session detail with associated memories."""
    try:
        session = memory_service._store.get_session(session_id)
        if session is None:
            return jsonify({"error": "Session not found"}), 404
        session_dict = session.to_dict()
        # Include memories associated with this session
        all_memories = memory_service._store.get_memories_for_search()
        session_memories = [
            m.to_dict() for m in all_memories if m.session_id == session_id
        ]
        session_dict["memories"] = session_memories
        return jsonify(session_dict)
    except Exception as e:
        error(f"Error getting session {session_id}: {e}")
        return jsonify({"error": str(e)}), 500


@memory_bp.route("/search", methods=["POST"])
@require_api_key
def search_memories():
    """Search memories by query."""
    data = request.get_json()
    if not data or not data.get("query"):
        return jsonify({"error": "Missing 'query' field"}), 400

    query = data["query"]
    limit = data.get("limit", 5)
    limit = min(limit, Config.MAX_QUERY_LIMIT)
    memory_type = data.get("type")

    type_filter = None
    if memory_type:
        try:
            type_filter = MemoryType(memory_type)
        except ValueError:
            return jsonify({"error": f"Invalid memory type: {memory_type}"}), 400

    try:
        results = memory_service.recall(query, limit=limit, memory_type_filter=type_filter)
        return jsonify([r.to_dict() for r in results])
    except Exception as e:
        error(f"Error searching memories: {e}")
        return jsonify({"error": str(e)}), 500


@memory_bp.route("/<memory_id>", methods=["DELETE"])
@require_api_key
def delete_memory(memory_id):
    """Delete a memory by ID."""
    try:
        deleted = memory_service.forget(memory_id)
        return jsonify({"deleted": deleted})
    except Exception as e:
        error(f"Error deleting memory {memory_id}: {e}")
        return jsonify({"error": str(e)}), 500


@memory_bp.route("/stats", methods=["GET"])
@require_api_key
def get_stats():
    """Get memory system statistics."""
    try:
        stats = memory_service.get_stats()
        return jsonify(stats)
    except Exception as e:
        error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500
