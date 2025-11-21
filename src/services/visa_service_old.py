"""
Core visa application service
Handles business logic for visa processing
"""

from typing import List, Dict, Any, Optional
from src.api.models.visa_models import (
    VisaApplication, ApplicationStatus, VisaRequirement,
    Document, DocumentType
)
from src.services.rag_service import RAGService
from src.services.approval_service import ApprovalService
import yaml
from datetime import datetime, timedelta
import uuid

class VisaService:
    def __init__(self):
        """Initialize visa service with dependencies."""
        self.rag_service = RAGService()
        self.approval_service = ApprovalService()
        
        with open("config/visa_requirements.yaml", 'r') as f:
            self.config = yaml.safe_load(f)
    
    def create_application(
        self,
        application: VisaApplication
    ) -> VisaApplication:
        """
        Create new visa application with validation.
        
        Args:
            application: Visa application data
        
        Returns:
            Created application with ID
        """
        # Generate application ID
        application.id = f"VISA-{uuid.uuid4().hex[:8].upper()}"
        application.created_at = datetime.now()
        application.updated_at = datetime.now()
        
        # Generate session ID
        application.session_id = f"SESSION-{uuid.uuid4().hex[:12].upper()}"
        
        # Validate basic requirements
        self._validate_application(application)
        
        # Store application (in production, save to database)
        # For now, return the application
        
        return application
    
    def get_visa_requirements(
        self,
        country: str,
        visa_type: str,
        employee_nationality: Optional[str] = None
    ) -> VisaRequirement:
        """
        Get visa requirements for destination using RAG.
        
        Args:
            country: Destination country
            visa_type: Type of visa
            employee_nationality: Optional employee nationality for specific requirements
        
        Returns:
            Visa requirements
        """
        additional_context = f"Applicant nationality: {employee_nationality}" if employee_nationality else None
        
        # Query RAG service
        requirements_data = self.rag_service.query_visa_requirements(
            country=country,
            visa_type=visa_type,
            additional_context=additional_context
        )
        
        # Parse and structure the response
        # In production, this would parse the LLM response into structured data
        return VisaRequirement(
            country=country,
            visa_type=visa_type,
            required_documents=self._extract_required_documents(visa_type),
            processing_time_days=self._estimate_processing_time(country, visa_type),
            validity_months=12,
            fees={"application_fee": 160.0, "service_fee": 50.0},
            special_requirements=[],
            embassy_contacts={}
        )
    
    def validate_documents(
        self,
        application: VisaApplication
    ) -> Dict[str, Any]:
        """
        Validate all documents in application.
        
        Args:
            application: Visa application with documents
        
        Returns:
            Validation results
        """
        validation_results = {
            "complete": True,
            "missing_documents": [],
            "invalid_documents": [],
            "warnings": []
        }
        
        # Get required documents for visa type
        required_docs = self._extract_required_documents(application.visa_type)
        
        # Check for missing documents
        provided_doc_types = [doc.type for doc in application.documents]
        
        for req_doc in required_docs:
            if req_doc not in provided_doc_types:
                validation_results["missing_documents"].append(req_doc)
                validation_results["complete"] = False
        
        # Validate individual documents
        for document in application.documents:
            doc_validation = self._validate_single_document(
                document,
                application
            )
            
            if not doc_validation["valid"]:
                validation_results["invalid_documents"].append({
                    "document": document.type,
                    "issues": doc_validation["issues"]
                })
                validation_results["complete"] = False
            
            if doc_validation.get("warnings"):
                validation_results["warnings"].extend(doc_validation["warnings"])
        
        return validation_results
    
    def submit_application(
        self,
        application_id: str
    ) -> VisaApplication:
        """
        Submit application for approval process.
        
        Args:
            application_id: Application ID
        
        Returns:
            Updated application
        """
        # In production, retrieve from database
        # application = self._get_application(application_id)
        
        # Validate documents are complete
        # validation = self.validate_documents(application)
        # if not validation["complete"]:
        #     raise ValueError("Cannot submit incomplete application")
        
        # Update status and timestamp
        # application.status = ApplicationStatus.SUBMITTED
        # application.submitted_at = datetime.now()
        # application.updated_at = datetime.now()
        
        # Initialize approval workflow
        # self.approval_service.start_workflow(application)
        
        # return application
        pass
    
    def track_application_status(
        self,
        application_id: str
    ) -> Dict[str, Any]:
        """
        Track current status and next steps.
        
        Args:
            application_id: Application ID
        
        Returns:
            Status information
        """
        # In production, retrieve from database
        return {
            "application_id": application_id,
            "current_status": "hr_review",
            "progress_percentage": 30,
            "next_step": "Awaiting HR Manager approval",
            "estimated_completion": datetime.now() + timedelta(days=5),
            "timeline": [
                {"stage": "submitted", "completed": True, "date": datetime.now() - timedelta(days=2)},
                {"stage": "hr_review", "completed": False, "current": True},
                {"stage": "legal_review", "completed": False},
                {"stage": "management_approval", "completed": False},
                {"stage": "embassy_submission", "completed": False}
            ]
        }
    
    def _validate_application(self, application: VisaApplication):
        """Validate application basic requirements."""
        # Check passport validity
        months_until_expiry = (application.applicant.passport_expiry - datetime.now().date()).days / 30
        if months_until_expiry < 6:
            raise ValueError("Passport must be valid for at least 6 months")
        
        # Check travel dates
        if application.travel_details.departure_date < datetime.now().date():
            raise ValueError("Departure date cannot be in the past")
    
    def _extract_required_documents(self, visa_type: str) -> List[str]:
        """Extract required documents for visa type from config."""
        # This would typically aggregate from multiple sources
        base_docs = ["passport", "passport_photos", "employment_letter"]
        
        if visa_type == "business":
            base_docs.extend(["invitation_letter", "bank_statements", "flight_itinerary"])
        elif visa_type == "work":
            base_docs.extend(["employment_letter", "bank_statements", "qualification_certificates"])
        
        return base_docs
    
    def _estimate_processing_time(self, country: str, visa_type: str) -> int:
        """Estimate processing time in days."""
        # In production, this would query historical data or RAG
        base_times = {
            "business": 10,
            "work": 20,
            "tourist": 7,
            "student": 15
        }
        return base_times.get(visa_type, 10)
    
    def _validate_single_document(
        self,
        document: Document,
        application: VisaApplication
    ) -> Dict[str, Any]:
        """Validate a single document."""
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Document-specific validation rules
        if document.type == DocumentType.PASSPORT:
            # Check expiry
            months_valid = (application.applicant.passport_expiry - datetime.now().date()).days / 30
            if months_valid < 6:
                result["valid"] = False
                result["issues"].append("Passport expires within 6 months")
        
        elif document.type == DocumentType.BANK_STATEMENT:
            # Check recency
            # In production, extract date from document
            result["warnings"].append("Ensure bank statement is from last 3 months")
        
        return result
