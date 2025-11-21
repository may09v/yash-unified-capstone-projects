from langchain.tools import tool
from typing import Dict, List
import requests
from src.api.models.approval_models import ApprovalRequest 
from src.api.models.visa_models import VisaApplicationPatch , CreateApplicationRequest , ApplicantTool , TravelDetailsTool , CreateApplicationArgsTool , Document
from langchain_core.tools import StructuredTool
from typing import Optional
import requests
import json
from typing import Optional, List
from src.services.visa_service import VisaService
from src.services import rag_service
from fastapi import APIRouter, HTTPException, status, Depends
from src.utils.logger import get_logger
import sqlite3
from datetime import datetime, timezone
from src.api.models.approval_models import ApprovalResponse
from src.api.routes.approval_workflow import get_next_stage, WORKFLOW_STAGES


# base_url = "http://127.0.0.1:8001/"

base_url = "http://localhost:8001/"

def get_visa_service() -> VisaService:
    return VisaService()


@tool
def Get_Visa_Details(
    application_id: str
):
    """
    Get visa application by ID.
   
    Args:
        application_id: Application ID
   
    Returns:
        VisaApplication object
    """
    try:
        visa_service = VisaService()
        print(application_id)
        application = visa_service.get_application(application_id)
       
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found"
            )
       
        return application
       
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve application: {str(e)}"
        )


@tool
def Approve_Visa_Workflow(
    application_id: str,
    approver_id: str,
    approver_role: str,
    action: str,
    comments: Optional[str] = None
):
    """
    Approve or reject a visa application in the approval workflow. 
    
    Args:
        application_id: Application ID
        approver_id: ID of the approver
        approver_role: Role of the approver (hr_team, legal_team, management_team)
        action: Action to take (approve, reject, request_change)
        comments: Optional comments about the decision
    """
    print("Approve_Visa_Workflow tool")
    logger = get_logger(__name__) 
    
    # Create an ApprovalRequest object from the parameters
    request = ApprovalRequest(
        application_id=application_id,
        approver_id=approver_id,
        approver_role=approver_role,
        action=action,
        comments=comments
    )
    
    endpoint_url = f"{base_url}api/approvals/process"
    # try:
    #     response = requests.post(endpoint_url, json=request.model_dump() , timeout=60)
    #     response.raise_for_status()
    #     print(f"> API Response ({response.status_code}): {response.json()}")
    #     return response.json()

    # except requests.exceptions.RequestException as e:
    #     print(f"> Network/API error occurred: {e}")
    #     if e.response:
    #         print(f"> Server Response Body: {e.response.text}")
    #     return e.response.text
    
    try:
        logger.info(f"Processing approval for application {request.application_id}")
        conn = sqlite3.connect("visa_applications.db")
        cursor = conn.cursor()

        # Fetch current stage and status
        cursor.execute("""
                SELECT va.current_stage, va.status, td.destination_country
                FROM visa_applications va
                JOIN travel_details td ON va.id = td.application_id
                WHERE va.id = ?
            """,
            (request.application_id,)
        )
        result = cursor.fetchone()
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Application {request.application_id} not found")

        current_stage, current_status ,embassy = result
        timestamp = datetime.now(timezone.utc).isoformat()

        # Validate approver role
        if current_stage != request.approver_role:
            conn.close()
            raise HTTPException(status_code=403, detail="Approver role does not match current stage")

        # Insert approval history record
        cursor.execute("""
            INSERT INTO approval_history (application_id, approver, role, action, timestamp, comments)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.application_id,
            request.approver_id,
            request.approver_role,
            request.action,
            timestamp,
            request.comments
        ))

        if request.action == "approve":
            next_stage = get_next_stage(current_stage)
            if next_stage:
                # Move to next stage
                cursor.execute("""
                    UPDATE visa_applications
                    SET current_stage = ?, current_approver = ?, approval_status = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    next_stage,
                    next_stage,  # You can replace with actual approver logic
                    "pending",
                    timestamp,
                    request.application_id
                ))
                conn.commit()
                conn.close()
                return ApprovalResponse(
                    success=True,
                    message=f"Application approved and moved to {next_stage}",
                    application_status=f"Pending with {next_stage}"
                )
            else:
                # Final stage completed
                cursor.execute("""
                    UPDATE visa_applications
                    SET current_stage = ?, status = ?, approval_status = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    "completed",
                    "Workflow Completed",
                    "approved",
                    timestamp,
                    request.application_id
                ))

                cursor.execute('''
                    INSERT INTO embassy_tracking (
                        application_id, status, embassy_name, tracking_number,
                        submission_date, last_updated, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    request.application_id,
                    "pending",
                    embassy,
                    'tracking_number',
                    timestamp,
                    timestamp,
                    "We Will update you once the embassy processes the application."
                ))


                conn.commit()
                conn.close()
                return ApprovalResponse(
                    success=True,
                    message="Workflow completed successfully",
                    application_status="Workflow Completed"
                )

        elif request.action in ["reject", "request_change"]:
            new_status = "Rejected" if request.action == "reject" else "Changes Requested"
            cursor.execute("""
                UPDATE visa_applications
                SET status = ?, approval_status = ?, updated_at = ?
                WHERE id = ?
            """, (
                new_status,
                "rejected" if request.action == "reject" else "pending",
                timestamp,
                request.application_id
            ))
            conn.commit()
            conn.close()
            return ApprovalResponse(
                success=True,
                message=f"Application has been {new_status.lower()}",
                application_status=new_status
            )

        else:
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid action specified.")

    except Exception as e:
        logger.error(f"Error processing approval: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process approval {str(e)}")



# --- All your Pydantic Models (ApplicantTool, etc.) remain the same ---
# (Assuming they are defined above this function)
@tool
def Create_Visa_Application(tool_ip:dict) -> dict:
    """
    Creates a visa application by constructing a NESTED JSON payload that mirrors
    the API's expected schema and submits it.
    """
    print("\n--- Tool Called: submit_visa_application ---")
    visa_service = VisaService()
    try:
        # --- START: CORRECT NESTED PAYLOAD CREATION ---

        # The API is confirmed to expect a nested structure.
        # We will build the payload to exactly match the working curl command.

        # Step 1: Convert the Pydantic model arguments into dictionaries.
        # This is the crucial step to ensure the data is JSON-serializable.
        # applicant_dict = applicant.model_dump()
        # travel_details_dict = travel_details.model_dump()

        # Step 2: Construct the final nested payload.
        # payload = {
        #     "applicant": applicant_dict,
        #     "visa_type": visa_type,
        #     "travel_details": travel_details_dict,
        #     "notes": notes
        # }
        pd_payload = CreateApplicationRequest(**tool_ip)


        print(f"--- CORRECTLY NESTED API Payload ---")

        # --- END: CORRECT NESTED PAYLOAD CREATION ---

        # endpoint_url = f"{base_url}api/visa/applications"
        # headers = {
        #     'accept': 'application/json',
        #     'Content-Type': 'application/json'
        # }
        
        # print(f"> Sending POST request to {endpoint_url}...")
        # response = requests.post(endpoint_url, json=payload, headers=headers, timeout=60)
        
        # # Raise an exception for 4xx/5xx server errors
        # response.raise_for_status()
        
        # response_data = response.json()
        response = visa_service.create_application(pd_payload)


        print(f"✅ API Success: {response}")


        return response

    except requests.exceptions.HTTPError as http_err:
        # This block will give us the real error from the API
        status_code = http_err.response.status_code
        error_message = f"API Error: The server rejected the request with status code {status_code}."
        
        try:
            server_error_details = http_err.response.json()
            error_message += f" Server Response: {json.dumps(server_error_details)}"
        except json.JSONDecodeError:
            server_error_details = http_err.response.text
            error_message += f" Server Response (Non-JSON): {server_error_details}"
            
        print(f"❌ {error_message}")
        
        return {"error": error_message, "details": server_error_details}
        
    except Exception as e:
        error_msg = f"An unexpected error occurred in the tool function: {type(e).__name__} - {e}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}




@tool
def rag_visa_query(query: str) :
    """
    Query the RAG knowledge base for Document needed to create visa for a country and to get embassy details .

    Args:
        query (str): The user's question regarding visa document requirements or embassy information.

    Returns:
        dict: A JSON object containing the answer, sources, and number of retrieved chunks.
    """
    print("RAG Query:", query)
    rs = rag_service.RAGService()
    payload = {"query": query}

    if not rs.is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service is currently unavailable"
            )
       
    try:
        relevant_docs = rs.retrieve_relevant_info(query, k=3)

        sources = []
        for doc in relevant_docs:
            sources.append({
                "content": doc.page_content,
                "metadata": getattr(doc, 'metadata', {}),
                "score": getattr(doc, 'score', None)
            })
       
        response = {
            "success": True,
            "query": query,
            "answer": relevant_docs,
            "sources": sources,
            "total_results": len(sources)
        }
        print(f"> API Response ({response}): {response}")
        return response

    except requests.exceptions.RequestException as e:
        print(f"> Network/API error occurred: {e}")
        if e.response:
            print(f"> Server Response Body: {e.response.text}")
        return e.response.text
    

@tool(args_schema=VisaApplicationPatch)
def patch_application(**kwargs):
    """
    Update visa application data using keyword arguments.
    **remember to send application id in kwargs

    """
    print("--------------in patch function----------------")
    patch = VisaApplicationPatch(**kwargs)  # Rebuild schema from kwargs
    application_id = patch.id
    if not application_id:
        raise ValueError("Application ID is required for update")

    update_data = patch.model_dump(exclude_unset=True)
    print("payload for patch function ",update_data)
    visa_service = VisaService()
    # endpoint_url = f"{base_url}api/visa/applications/{application_id}"
    try:
        response = visa_service.patch_application(application_id,update_data)
       
        print(f"> Response (response): {response}")
        return response

    except requests.exceptions.RequestException as e:
        print(f"> Network/API error occurred: {e}")
        if e.response:
            print(f"> Server Response Body: {e.response.text}")
        return e.response.text
    


# @tool
# def update_embassy_status(application_id: str, status: str, embassy_name: Optional[str] = None, tracking_number: Optional[str] = None, notes: Optional[str] = None) -> dict:

#     """

#     Update embassy tracking status for a visa application.

#     Args:

#         application_id: The visa application ID

#         status: Embassy status - must be one of: 'not_submitted', 'submitted', 'under_review', 'approved', 'rejected', 'visa_issued'

#         embassy_name: Name of the embassy

#         tracking_number: Tracking number for embassy submission

#         notes: Additional notes about embassy status

#     Returns:

#         dict: Response with success status and embassy tracking details

#     """

#     print("update_embassy_status tool")

#     endpoint_url = f"{base_url}api/visa/applications/{application_id}/embassy"

#     request_data = {

#         "status": status

#     }

#     if embassy_name:

#         request_data["embassy_name"] = embassy_name

#     if tracking_number:

#         request_data["tracking_number"] = tracking_number

#     if notes:

#         request_data["notes"] = notes

#     try:

#         response = requests.put(endpoint_url, json=request_data, timeout=60)

#         response.raise_for_status()

#         print(f"> API Response ({response.status_code}): {response.json()}")

#         return response.json()
 
#     except requests.exceptions.RequestException as e:

#         print(f"> Network/API error occurred: {e}")

#         if e.response:

#             print(f"> Server Response Body: {e.response.text}")

#         return e.response.text
 

@tool
def get_embassy_status(application_id: str) -> dict:
    """
    Retrieve embassy tracking status for a visa application.
    Args:
        application_id: The visa application ID to retrieve embassy status for
    """
    
    print("get_embassy_status tool")
    
    try:
        # Import logger at the function level or use print for now
        from src.utils.logger import get_logger
        logger = get_logger(__name__)
        
        visa_service = VisaService()
        logger.info(f"Getting embassy tracking for {application_id}")
       
        success = visa_service.get_embassy_status(application_id)
        print(success, "embassy status success")
        
        if not success:
            # Return error response instead of raising HTTPException since this is a tool
            return {
                "error": f"Failed to get embassy status for application {application_id}",
                "details": "Application not found or embassy status unavailable"
            }
        
        return success
       
    except ValueError as e:
        error_msg = f"Validation error: {e}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Error getting embassy status: {e}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}  
    

@tool
def validate_document_content(application_id: str) -> dict:

    """

    Validate if documents have content and are properly filled for a visa application.

    Args:

        application_id: The visa application ID to validate documents for

    Returns:

        dict: Document validation results including completeness and issues found

    """

    print("validate_document_content tool")

    endpoint_url = f"{base_url}api/visa/applications/{application_id}/validate-documents-content"

    try:

        response = requests.post(endpoint_url, timeout=60)

        response.raise_for_status()

        print(f"> API Response ({response.status_code}): {response.json()}")

        return response.json()
 
    except requests.exceptions.RequestException as e:

        print(f"> Network/API error occurred: {e}")

        if e.response:

            print(f"> Server Response Body: {e.response.text}")

        return e.response.text
 
@tool
def get_pending_approvals(approver_role: str) -> dict:
    """
    Get all visa applications pending approval for a specific approver role.

    Args:
        approver_role (str): The role of the approver (e.g., 'hr_team', 'legal_team', 'management_team', 'ceo')."""
    print("get_pending_approvals tool")
    try:
        vs = VisaService()

        try:
            conn = vs._get_connection()
            cursor = conn.cursor()
            cursor.execute(
    "SELECT id, current_stage FROM visa_applications WHERE current_stage <> %s",
    ('user',)
)

            #
            result = cursor.fetchone()
            conn.close()
           
            if result:
                print("Found pending applications ",result)
                app_data = [i for i in result]
                return app_data

            else:
                print(f"Applications not found")
                return None
               
        except Exception as e:
            print(f"Failed to retrieve applications : {e}")
            return None


        
        # # In production: Query database for pending approvals
        # return {
        #     "approver_role": approver_role,
        #     "pending_count": 0,
        #     "applications": []
        # }
    
    except Exception as e:
        print(f"Error fetching pending approvals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch pending approvals")

    
 
