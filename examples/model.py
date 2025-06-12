from typing import Optional, List, Dict, Any

import bleach
from pydantic import BaseModel, Field, root_validator, model_validator

# List of stuff allowed
ALLOWED_TAGS: List[str] = []          # no HTML tags
ALLOWED_ATTRIBUTES: Dict[str, List[str]] = {}

def _clean_str(s: str) -> str:
    # trim then strip any HTML/JS
    return bleach.clean(
        s.strip(),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

class ProjectModel(BaseModel):
    title: str = Field(..., description="Project title")
    intro: str = Field(..., description="Introduction text")
    problem: Optional[List[str]] = Field(
        None, 
        description="List of problems (>3 items recommended)",
        min_length=0
    )
    solution_desc: str = Field(..., description="Solution description")
    implementation: str = Field(..., description="Implementation details")
    approach: Optional[List[str]] = Field(
        None, 
        description="List of approach steps"
    )
    about: str = Field(..., description="About section")
    getting_started: str = Field(..., description="Getting started guide")

    class Config:
        # This allows the model to work with both snake_case and original field names
        populate_by_name = True

    # If you want to use the exact field names from your list (with spaces/special chars)
    # you can use aliases:
    # solution_desc: str = Field(..., alias="Solution Desc")

    @model_validator(mode="before")
    @classmethod
    def sanitize_all_inputs(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs before validation: strips HTML/JS and trims whitespace
        on every string or list-of-strings field.
        """
        sanitized: Dict[str, Any] = {}
        for k, v in values.items():
            if isinstance(v, str):
                sanitized[k] = _clean_str(v)
            elif isinstance(v, list):
                sanitized[k] = [
                    _clean_str(item) if isinstance(item, str) else item
                    for item in v
                ]
            else:
                sanitized[k] = v
        return sanitized


# Example usage:
if __name__ == "__main__":
    # Example with all fields
    project_full = ProjectModel(
        title="My Project",
        intro="This is an introduction",
        problem=["Problem 1", "Problem 2", "Problem 3", "Problem 4"],
        solution_desc="This solves the problems",
        implementation="Here's how to implement",
        approach=["Step 1", "Step 2", "Step 3"],
        about="About this project",
        getting_started="To get started..."
    )

    # Example without optional fields
    project_minimal = ProjectModel(
        title="My Project",
        intro="This is an introduction",
        solution_desc="This solves the problems",
        implementation="Here's how to implement",
        about="About this project",
        getting_started="To get started..."
    )

    print(project_full.model_dump_json(indent=2))