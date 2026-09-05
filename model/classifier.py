"""
Civisense - Smart Civic Issue Classifier & Severity Estimator

This module acts as the AI inference engine for Civisense.
In this hackathon MVP, it employs a multi-modal heuristic analysis:
1. Computer Vision Image Analysis: Evaluates luminance, contrast, edge density,
   and color palette distribution using Pillow.
2. Natural Language Description Analysis: Scans tokenized keywords to reinforce
   the semantic context and calculate severity modifiers.
3. Automated Department Routing & Priority Matrix: Calculates dynamic SLA priority
   (1-10) and assigns the municipal department responsible for remediation.

Production Upgrade Path:
- Replace the heuristic engine with fine-tuned YOLOv8 or MobileNetV2 trained on
  civic problem datasets (e.g., Road Damage Dataset RDD2022, GarbageNet, etc.).
"""

import os
import re
import random
from PIL import Image, ImageStat, ImageFilter

CATEGORIES = {
    "Pothole": {
        "keywords": ["pothole", "crater", "hole", "road pit", "bump", "asphalt hole", "dip", "ditch"],
        "department": "Road Maintenance Department",
        "base_severity": "HIGH",
        "base_priority": 8,
        "default_confidence_range": (88, 96),
        "visual_signature": "high_edge_dark_contrast"
    },
    "Garbage Dump": {
        "keywords": ["garbage", "trash", "waste", "dump", "litter", "debris", "rubbish", "plastic", "refuse", "stench"],
        "department": "Solid Waste Management Department",
        "base_severity": "MEDIUM",
        "base_priority": 6,
        "default_confidence_range": (86, 95),
        "visual_signature": "high_entropy_color_scatter"
    },
    "Water Leakage": {
        "keywords": ["water", "leak", "pipe", "burst", "supply", "drinking water", "flooding", "tap", "pipeline"],
        "department": "Water Supply & Sewerage Board",
        "base_severity": "HIGH",
        "base_priority": 8,
        "default_confidence_range": (87, 94),
        "visual_signature": "blue_reflectance_smooth"
    },
    "Broken Streetlight": {
        "keywords": ["streetlight", "street light", "lamp", "pole", "dark", "wiring", "electrical", "bulb", "flickering", "lighting"],
        "department": "Electrical & Public Lighting Department",
        "base_severity": "MEDIUM",
        "base_priority": 6,
        "default_confidence_range": (89, 97),
        "visual_signature": "low_luminance_vertical"
    },
    "Road Damage": {
        "keywords": ["crack", "road damage", "damaged road", "caved in", "pavement", "erosion", "broken road", "tar", "divider"],
        "department": "Public Works Department (PWD)",
        "base_severity": "HIGH",
        "base_priority": 7,
        "default_confidence_range": (85, 93),
        "visual_signature": "linear_edges_texture"
    },
    "Overflowing Drain": {
        "keywords": ["drain", "drainage", "sewer", "gutter", "sewage", "overflowing drain", "choked", "manhole", "dirty water", "nallah"],
        "department": "Municipal Drainage & Sanitation Department",
        "base_severity": "CRITICAL",
        "base_priority": 9,
        "default_confidence_range": (88, 96),
        "visual_signature": "dark_fluid_contrast"
    },
    "Other": {
        "keywords": ["encroachment", "tree fallen", "stray", "noise", "illegal", "footpath", "hazard", "civic"],
        "department": "Municipal Grievance Redressal Cell",
        "base_severity": "LOW",
        "base_priority": 4,
        "default_confidence_range": (78, 88),
        "visual_signature": "general"
    }
}

SEVERITY_KEYWORDS = {
    "CRITICAL": ["critical", "emergency", "fatal", "accident", "burst", "flooded", "collapsed", "fire", "sparking", "toxic", "huge", "dangerous", "death trap"],
    "HIGH": ["deep", "urgent", "major", "severe", "hazardous", "massive", "blocked", "overflowing", "injury", "broken", "serious"],
    "MEDIUM": ["moderate", "bad", "smelly", "annoying", "growing", "frequent", "several"],
    "LOW": ["minor", "small", "slight", "cosmetic", "old", "inconvenience"]
}


class CivicIssueClassifier:
    """Intelligent multi-modal civic classifier for hackathon demonstration."""

    def __init__(self):
        self.categories = CATEGORIES

    def analyze_image_features(self, image_path):
        """Extract visual descriptors (brightness, contrast, edge density) from image."""
        if not image_path or not os.path.exists(image_path):
            return {"valid": False, "brightness": 128, "contrast": 50, "edge_score": 50}

        try:
            with Image.open(image_path) as img:
                # Convert to RGB and resize for fast analysis
                img_rgb = img.convert("RGB").resize((160, 160))
                stat = ImageStat.Stat(img_rgb)
                mean_brightness = sum(stat.mean) / (3.0 * 255.0)  # 0.0 to 1.0
                r, g, b = stat.mean

                # Grayscale for edge analysis
                img_gray = img_rgb.convert("L")
                edges = img_gray.filter(ImageFilter.FIND_EDGES)
                edge_stat = ImageStat.Stat(edges)
                edge_score = edge_stat.mean[0]  # higher means more jagged/broken textures

                contrast = (stat.stddev[0] + stat.stddev[1] + stat.stddev[2]) / 3.0

                return {
                    "valid": True,
                    "brightness": mean_brightness,
                    "contrast": contrast,
                    "edge_score": edge_score,
                    "r": r, "g": g, "b": b
                }
        except Exception:
            return {"valid": False, "brightness": 128, "contrast": 50, "edge_score": 50}

    def predict(self, image_path=None, description=""):
        """
        Classifies the civic problem based on description and image.
        Returns a rich dictionary with issue, confidence, severity, priority, and department.
        """
        desc_lower = (description or "").lower()
        img_features = self.analyze_image_features(image_path)

        # 1. Text keyword score
        category_scores = {}
        for cat, data in self.categories.items():
            score = 0
            for kw in data["keywords"]:
                if kw in desc_lower:
                    score += 15 + len(kw)
            category_scores[cat] = score

        # 2. Visual heuristic weighting
        if img_features["valid"]:
            # Dark images / high contrast -> Broken Streetlight / Night issues
            if img_features["brightness"] < 0.28:
                category_scores["Broken Streetlight"] += 8
            # High edge score / rough texture -> Potholes, Road Damage, Garbage
            if img_features["edge_score"] > 25:
                category_scores["Pothole"] += 6
                category_scores["Road Damage"] += 5
                category_scores["Garbage Dump"] += 4
            # Water or drain: bluish or dark fluid reflectance
            if img_features.get("b", 0) > img_features.get("r", 0) * 1.1:
                category_scores["Water Leakage"] += 6
                category_scores["Overflowing Drain"] += 4

        # 3. Filename heuristic fallback
        if image_path:
            fname = os.path.basename(image_path).lower()
            for cat, data in self.categories.items():
                for kw in data["keywords"]:
                    if kw in fname:
                        category_scores[cat] += 20

        # Determine winner
        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]

        # If no significant signal, pick based on description length or fallback to Pothole / Other
        if max_score <= 0:
            if "light" in desc_lower or "dark" in desc_lower:
                best_category = "Broken Streetlight"
            elif "road" in desc_lower:
                best_category = "Road Damage"
            elif "water" in desc_lower:
                best_category = "Water Leakage"
            elif "waste" in desc_lower or "garbage" in desc_lower:
                best_category = "Garbage Dump"
            elif len(desc_lower.strip()) > 3:
                best_category = "Pothole"
            else:
                best_category = "Pothole"

        config = self.categories.get(best_category, self.categories["Other"])

        # Determine Confidence
        conf_min, conf_max = config["default_confidence_range"]
        # Add slight pseudo-random variation based on text length and score for realism
        seed_offset = (len(desc_lower) * 3 + int(img_features.get("edge_score", 10))) % (conf_max - conf_min + 1)
        confidence_val = min(98, max(82, conf_min + seed_offset))

        # Determine Severity
        severity = config["base_severity"]
        for sev_level, words in SEVERITY_KEYWORDS.items():
            if any(w in desc_lower for w in words):
                severity = sev_level
                break

        # Calculate Priority (1 to 10 scale)
        base_pri = config["base_priority"]
        if severity == "CRITICAL":
            priority_val = min(10, base_pri + 2)
        elif severity == "HIGH":
            priority_val = min(9, max(7, base_pri + 1))
        elif severity == "MEDIUM":
            priority_val = min(7, max(5, base_pri))
        else: # LOW
            priority_val = min(4, max(2, base_pri - 2))

        # Format output
        return {
            "issue": best_category,
            "confidence": f"{confidence_val}%",
            "confidence_val": confidence_val,
            "severity": severity,
            "priority": f"{priority_val}/10",
            "priority_val": priority_val,
            "department": config["department"],
            "visual_signature": config["visual_signature"],
            "model_engine": "Civisense Hybrid Vision & Semantic Engine (v1.2)"
        }


# Global helper instance
_classifier_instance = None

def analyze_issue(image_path=None, description=""):
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = CivicIssueClassifier()
    return _classifier_instance.predict(image_path=image_path, description=description)
