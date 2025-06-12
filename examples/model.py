from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from ..constants import SOLUTION_BRIEF_TEMPLATE_TYPES


class SubSection(BaseModel):
    title: str = Field(..., max_length=100)
    content: str = Field(..., max_length=2000)
    icon: Optional[str] = None


class ContentSection(BaseModel):
    section_title: str = Field(..., max_length=150)
    content: str = Field(..., max_length=10000)
    section_type: Literal["intro", "body", "highlight", "feature_grid", "numbered_list"]
    subsections: Optional[List[SubSection]] = None


# Solution Brief specific models
class ProblemCategory(BaseModel):
    title: str = Field(..., max_length=100)
    items: List[str] = Field(..., max_items=5)


class ValueProposition(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)


class UseCase(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)


class TechnologyFeature(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    sub_features: Optional[List[str]] = None


class ServiceOffering(BaseModel):
    category: str = Field(..., max_length=50)  # "base", "custom", "specialized"
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    scope_details: Optional[List[str]] = None


class MethodologyPhase(BaseModel):
    phase_number: int = Field(..., ge=1, le=6)
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)


class TechnologyPartner(BaseModel):
    name: str = Field(..., max_length=100)
    proficiency_level: str = Field(
        ..., max_length=50
    )  # e.g., "Gold Partner", "Certified"
    logo_url: Optional[str] = None
    included_in_base: bool = True


class ClientSuccessStory(BaseModel):
    client_name: str = Field(..., max_length=100)
    engagement_scope: str = Field(..., max_length=200)
    key_stakeholders: str = Field(..., max_length=200)  # AE, SA info
    challenge: str = Field(..., max_length=500)
    solution_approach: str = Field(..., max_length=500)
    business_outcomes: str = Field(..., max_length=500)


class SolutionBriefData(BaseModel):
    # Header Section
    company_name: str = Field(default="BlueAlly")
    service_title: str = Field(..., max_length=200)
    date: str = Field(..., max_length=50)  # e.g., "Q1CY2025"
    prepared_by: str = Field(..., max_length=100)

    # Service Overview (Required)
    service_overview: str = Field(..., max_length=2000)

    # Problem Statement (Required)
    problem_categories: List[ProblemCategory] = Field(..., min_items=2, max_items=4)

    # Value Proposition (Required)
    value_propositions: List[ValueProposition] = Field(..., min_items=3, max_items=4)

    # Use Cases (Required)
    use_cases: List[UseCase] = Field(..., min_items=3, max_items=4)

    # Key Features (Required)
    technology_features: List[TechnologyFeature] = Field(..., min_items=3)
    service_offerings: List[ServiceOffering] = Field(..., min_items=3)

    # Methodology (Required)
    methodology_phases: List[MethodologyPhase] = Field(..., min_items=6, max_items=6)
    methodology_diagram_url: Optional[str] = None

    # Technology Partners (Required)
    technology_partners: List[TechnologyPartner] = Field(..., min_items=1)

    # Optional sections
    related_services: Optional[List[str]] = None
    client_success_story: Optional[ClientSuccessStory] = None
    by_the_numbers: Optional[Dict[str, str]] = None  # key-value pairs for metrics
    industry_facts: Optional[List[str]] = None

    # Marketing sections
    captivating_opening: Optional[str] = Field(None, max_length=1000)
    why_choose_blueally: Optional[List[str]] = None
    call_to_action: str = Field(
        default="Visit blueally.com/contact to connect with our team"
    )


class DocumentData(BaseModel):
    # Header/Branding
    company_name: str = Field(..., max_length=100)
    company_logo_url: Optional[str] = None
    document_title: str = Field(..., max_length=200)
    document_subtitle: Optional[str] = Field(None, max_length=300)
    document_type: str = Field(default="WHITE PAPER")

    # Content Sections
    sections: List[ContentSection]

    # Footer
    contact_info: Optional[str] = None
    copyright_text: Optional[str] = None


class PDFOptions(BaseModel):
    page_size: Literal["letter", "a4"] = "letter"
    orientation: Literal["portrait", "landscape"] = "portrait"
    include_cover_page: bool = True
    include_page_numbers: bool = True
    margins: Optional[Dict[str, Any]] = None


class DocumentRequest(BaseModel):
    template_type: Literal[
        "whitepaper",
        "report",
        "proposal",
        "solution_brief",
        "solution_brief_minimal",
        "solution_brief_simple",
        "solution_brief_debug",
    ]
    document_data: Optional[DocumentData] = None  # For existing templates
    solution_brief_data: Optional[SolutionBriefData] = None  # For solution brief
    options: Optional[PDFOptions] = None

    def model_post_init(self, __context):
        # Ensure at least one data field is provided
        if not self.document_data and not self.solution_brief_data:
            raise ValueError(
                "Either document_data or solution_brief_data must be provided"
            )

        # Ensure the correct data field is used for the template type
        if (
            self.template_type in SOLUTION_BRIEF_TEMPLATE_TYPES
            and not self.solution_brief_data
        ):
            raise ValueError(
                "solution_brief_data is required for solution_brief template"
            )

        if (
            self.template_type not in SOLUTION_BRIEF_TEMPLATE_TYPES
            and not self.document_data
        ):
            raise ValueError(
                "document_data is required for non-solution_brief templates"
            )


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseModel):
    message: str
    document_id: Optional[str] = None
    generated_at: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class TemplateInfo(BaseModel):
    name: str
    description: str
    supported_sections: List[str]


class TemplatesResponse(BaseModel):
    templates: List[TemplateInfo]


class GenerateSolutionBriefResponse(BaseModel):
    """Response model for solution brief generation from documents."""

    solution_brief_data: SolutionBriefData
    message: str
    generated_at: datetime
    processed_files: List[str]
    total_content_length: int
