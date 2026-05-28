"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database


class WorkModeRepository:
    """MongoDB persistence adapter for Work Mode Mission Runtime state."""

    def __init__(self, database: Database):
        self.projects: Collection = database["work_projects"]
        self.employees: Collection = database["work_employees"]
        self.project_employees: Collection = database["work_project_employees"]
        self.missions: Collection = database["work_missions"]
        self.runs: Collection = database["work_runs"]
        self.steps: Collection = database["work_steps"]
        self.artifacts: Collection = database["work_artifacts"]
        self.products: Collection = database["work_products"]
        self.work_windows: Collection = database["work_windows"]
        self.events: Collection = database["work_events"]
        self.event_counters: Collection = database["work_event_counters"]

    def ensure_indexes(self) -> None:
        self.projects.create_index([("user_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)])
        self.projects.create_index([("user_id", ASCENDING), ("name", ASCENDING)])
        self.employees.create_index([("user_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)])
        self.employees.create_index([("user_id", ASCENDING), ("name", ASCENDING)])
        self.project_employees.create_index(
            [("user_id", ASCENDING), ("project_id", ASCENDING), ("employee_id", ASCENDING)],
            unique=True,
        )
        self.project_employees.create_index(
            [("user_id", ASCENDING), ("project_id", ASCENDING), ("updated_at", DESCENDING)]
        )
        self.missions.create_index(
            [("user_id", ASCENDING), ("project_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)]
        )
        self.missions.create_index([("user_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)])
        self.missions.create_index([("user_id", ASCENDING), ("lead_employee_id", ASCENDING), ("updated_at", DESCENDING)])
        self.runs.create_index([("user_id", ASCENDING), ("mission_id", ASCENDING), ("started_at", DESCENDING)])
        self.steps.create_index([("user_id", ASCENDING), ("run_id", ASCENDING), ("sequence", ASCENDING)])
        self.steps.create_index([("user_id", ASCENDING), ("mission_id", ASCENDING), ("sequence", ASCENDING)])
        self.artifacts.create_index([("user_id", ASCENDING), ("mission_id", ASCENDING), ("created_at", DESCENDING)])
        self.artifacts.create_index([("user_id", ASCENDING), ("run_id", ASCENDING), ("created_at", DESCENDING)])
        self.products.create_index([("user_id", ASCENDING), ("mission_id", ASCENDING), ("updated_at", DESCENDING)])
        self.work_windows.create_index([("user_id", ASCENDING), ("mission_id", ASCENDING), ("created_at", ASCENDING)])
        self.work_windows.create_index([("user_id", ASCENDING), ("run_id", ASCENDING), ("created_at", ASCENDING)])
        self.events.create_index(
            [("user_id", ASCENDING), ("mission_id", ASCENDING), ("sequence", ASCENDING)],
            unique=True,
        )
        self.events.create_index([("user_id", ASCENDING), ("run_id", ASCENDING), ("sequence", ASCENDING)])
        self.events.create_index([("user_id", ASCENDING), ("mission_id", ASCENDING), ("created_at", DESCENDING)])
        self.event_counters.create_index([("mission_id", ASCENDING)], unique=True)

    def create_project(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.projects.insert_one(document)
        created = self.projects.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_project(self, project_id: str, user_id: str) -> dict[str, Any] | None:
        query_id = _object_id_or_none(project_id)
        if query_id is None:
            return None
        return self.projects.find_one({"_id": query_id, "user_id": user_id})

    def list_projects(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return list(self.projects.find({"user_id": user_id}).sort("updated_at", DESCENDING).limit(limit))

    def create_employee(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.employees.insert_one(document)
        created = self.employees.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_employee(self, employee_id: str, user_id: str) -> dict[str, Any] | None:
        query_id = _object_id_or_none(employee_id)
        if query_id is None:
            return None
        return self.employees.find_one({"_id": query_id, "user_id": user_id})

    def list_employees(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return list(self.employees.find({"user_id": user_id}).sort("updated_at", DESCENDING).limit(limit))

    def add_project_employee(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["project_id"] = _object_id(document["project_id"])
        document["employee_id"] = _object_id(document["employee_id"])
        result = self.project_employees.insert_one(document)
        created = self.project_employees.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_project_employee(self, project_id: str, employee_id: str, user_id: str) -> dict[str, Any] | None:
        project_query_id = _object_id_or_none(project_id)
        employee_query_id = _object_id_or_none(employee_id)
        if project_query_id is None or employee_query_id is None:
            return None
        return self.project_employees.find_one(
            {"project_id": project_query_id, "employee_id": employee_query_id, "user_id": user_id}
        )

    def list_project_employees(self, user_id: str, project_id: str, limit: int) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(project_id)
        if query_id is None:
            return []
        return list(
            self.project_employees.find({"user_id": user_id, "project_id": query_id})
            .sort("updated_at", DESCENDING)
            .limit(limit)
        )

    def create_mission(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["project_id"] = _object_id(document["project_id"])
        result = self.missions.insert_one(document)
        created = self.missions.find_one({"_id": result.inserted_id})
        assert created is not None
        self.event_counters.insert_one({"mission_id": result.inserted_id, "sequence": 0})
        return created

    def find_mission(self, mission_id: str, user_id: str) -> dict[str, Any] | None:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return None
        return self.missions.find_one({"_id": query_id, "user_id": user_id})

    def list_missions(self, user_id: str, project_id: str, limit: int) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(project_id)
        if query_id is None:
            return []
        return list(
            self.missions.find({"user_id": user_id, "project_id": query_id})
            .sort("updated_at", DESCENDING)
            .limit(limit)
        )

    def update_mission(self, mission_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return None
        return self.missions.find_one_and_update(
            {"_id": query_id, "user_id": user_id},
            {"$set": values},
            return_document=ReturnDocument.AFTER,
        )

    def list_missions_by_status(self, statuses: list[str], limit: int) -> list[dict[str, Any]]:
        return list(
            self.missions.find({"status": {"$in": statuses}})
            .sort("updated_at", ASCENDING)
            .limit(limit)
        )

    def create_run(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["mission_id"] = _object_id(document["mission_id"])
        result = self.runs.insert_one(document)
        created = self.runs.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_active_run(self, mission_id: str, user_id: str) -> dict[str, Any] | None:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return None
        return self.runs.find_one(
            {"mission_id": query_id, "user_id": user_id, "status": "running"},
            sort=[("started_at", DESCENDING)],
        )

    def find_latest_run(self, mission_id: str, user_id: str) -> dict[str, Any] | None:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return None
        return self.runs.find_one(
            {"mission_id": query_id, "user_id": user_id},
            sort=[("started_at", DESCENDING)],
        )

    def update_run(self, run_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        query_id = _object_id_or_none(run_id)
        if query_id is None:
            return None
        return self.runs.find_one_and_update(
            {"_id": query_id, "user_id": user_id},
            {"$set": values},
            return_document=ReturnDocument.AFTER,
        )

    def update_running_runs_for_mission(
        self,
        mission_id: str,
        user_id: str,
        values: dict[str, Any],
    ) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return []
        run_ids = [
            row["_id"]
            for row in self.runs.find({"mission_id": query_id, "user_id": user_id, "status": "running"})
        ]
        if not run_ids:
            return []
        self.runs.update_many({"_id": {"$in": run_ids}, "user_id": user_id}, {"$set": dict(values)})
        return list(self.runs.find({"_id": {"$in": run_ids}, "user_id": user_id}))

    def create_step(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["mission_id"] = _object_id(document["mission_id"])
        document["run_id"] = _object_id(document["run_id"])
        result = self.steps.insert_one(document)
        created = self.steps.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def update_step(self, step_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        query_id = _object_id_or_none(step_id)
        if query_id is None:
            return None
        return self.steps.find_one_and_update(
            {"_id": query_id, "user_id": user_id},
            {"$set": values},
            return_document=ReturnDocument.AFTER,
        )

    def create_artifact(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["mission_id"] = _object_id(document["mission_id"])
        document["run_id"] = _object_id(document["run_id"])
        result = self.artifacts.insert_one(document)
        created = self.artifacts.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def update_artifact(self, artifact_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        query_id = _object_id_or_none(artifact_id)
        if query_id is None:
            return None
        return self.artifacts.find_one_and_update(
            {"_id": query_id, "user_id": user_id},
            {"$set": dict(values)},
            return_document=ReturnDocument.AFTER,
        )

    def list_artifacts(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return []
        return list(
            self.artifacts.find({"user_id": user_id, "mission_id": query_id})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

    def create_product(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["mission_id"] = _object_id(document["mission_id"])
        result = self.products.insert_one(document)
        created = self.products.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_product(self, product_id: str, user_id: str) -> dict[str, Any] | None:
        query_id = _object_id_or_none(product_id)
        if query_id is None:
            return None
        return self.products.find_one({"_id": query_id, "user_id": user_id})

    def update_product(self, product_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        query_id = _object_id_or_none(product_id)
        if query_id is None:
            return None
        values = dict(values)
        if values.get("latest_artifact_id") is not None:
            values["latest_artifact_id"] = _object_id(values["latest_artifact_id"])
        if "artifact_ids" in values:
            values["artifact_ids"] = [_object_id(value) for value in values["artifact_ids"]]
        return self.products.find_one_and_update(
            {"_id": query_id, "user_id": user_id},
            {"$set": values},
            return_document=ReturnDocument.AFTER,
        )

    def list_products(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return []
        return list(
            self.products.find({"user_id": user_id, "mission_id": query_id})
            .sort("updated_at", DESCENDING)
            .limit(limit)
        )

    def create_work_window(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["mission_id"] = _object_id(document["mission_id"])
        if document.get("run_id") is not None:
            document["run_id"] = _object_id(document["run_id"])
        result = self.work_windows.insert_one(document)
        created = self.work_windows.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def update_work_window(self, window_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        query_id = _object_id_or_none(window_id)
        if query_id is None:
            return None
        values = dict(values)
        if values.get("result_artifact_id") is not None:
            values["result_artifact_id"] = _object_id(values["result_artifact_id"])
        return self.work_windows.find_one_and_update(
            {"_id": query_id, "user_id": user_id},
            {"$set": values},
            return_document=ReturnDocument.AFTER,
        )

    def update_running_work_windows_for_mission(
        self,
        mission_id: str,
        user_id: str,
        values: dict[str, Any],
    ) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return []
        window_ids = [
            row["_id"]
            for row in self.work_windows.find({"mission_id": query_id, "user_id": user_id, "status": "running"})
        ]
        if not window_ids:
            return []
        self.work_windows.update_many({"_id": {"$in": window_ids}, "user_id": user_id}, {"$set": dict(values)})
        return list(self.work_windows.find({"_id": {"$in": window_ids}, "user_id": user_id}))

    def list_work_windows(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return []
        return list(
            self.work_windows.find({"user_id": user_id, "mission_id": query_id})
            .sort("created_at", ASCENDING)
            .limit(limit)
        )

    def next_event_sequence(self, mission_id: str) -> int:
        query_id = _object_id(mission_id)
        counter = self.event_counters.find_one_and_update(
            {"mission_id": query_id},
            {"$inc": {"sequence": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        assert counter is not None
        return int(counter["sequence"])

    def create_event(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["mission_id"] = _object_id(document["mission_id"])
        if document.get("run_id") is not None:
            document["run_id"] = _object_id(document["run_id"])
        if document.get("step_id") is not None:
            document["step_id"] = _object_id(document["step_id"])
        result = self.events.insert_one(document)
        created = self.events.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def list_events(self, user_id: str, mission_id: str, after_sequence: int | None, limit: int) -> list[dict[str, Any]]:
        query_id = _object_id_or_none(mission_id)
        if query_id is None:
            return []
        query: dict[str, Any] = {"user_id": user_id, "mission_id": query_id}
        if after_sequence is not None:
            query["sequence"] = {"$gt": after_sequence}
        return list(self.events.find(query).sort("sequence", ASCENDING).limit(limit))


def _object_id(value: Any) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    raise ValueError("invalid_object_id")


def _object_id_or_none(value: Any) -> ObjectId | None:
    try:
        return _object_id(value)
    except ValueError:
        return None
