from typing import Optional, List
from pydantic import BaseModel, Field


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