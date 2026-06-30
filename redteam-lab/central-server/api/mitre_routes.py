from fastapi import APIRouter
import json, yaml
from pathlib import Path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent / "mitre"

@router.get("/mapping")
def get_mapping():
    mapping_file = BASE_DIR / "mapping.yaml"
    if not mapping_file.exists():
        return {"error": "mapping.yaml not found"}
    with open(mapping_file, "r") as f:
        return yaml.safe_load(f)

@router.get("/navigator")
def get_navigator_layer():
    layer_file = BASE_DIR / "techniques.json"
    if not layer_file.exists():
        return {"error": "techniques.json not found. Run sync_mitre.py first."}
    with open(layer_file, "r") as f:
        return json.load(f)

@router.get("/coverage")
def get_coverage_stats():
    layer_file = BASE_DIR / "techniques.json"
    if not layer_file.exists():
        return {"error": "techniques.json not found"}
    with open(layer_file, "r") as f:
        layer = json.load(f)
    techs = layer.get("techniques", [])
    return {
        "total_covered": len(techs),
        "techniques": techs
    }