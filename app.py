import xml.etree.ElementTree as ET
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import json
import os
import uuid
from datetime import datetime
from data import generate_synthetic_powercenter_xml

# State definition for the workflow
class WorkflowState(TypedDict):
    xml_content: str
    parsed_data: Dict[str, Any]
    transformations: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    workflow_summary: str
    errors: List[str]
    session_id: str
    session_folder: str

class PowerCenterWorkflowExtractor:
    def __init__(self, llm_model="gpt-4"):
        try:
            # Check if OpenAI API key is available
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                print("Warning: OPENAI_API_KEY environment variable not set")
                raise Exception("OpenAI API key not found")
            
            self.llm = ChatOpenAI(model=llm_model, temperature=0, api_key=openai_api_key)
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI LLM: {e}")
            print("Using mock LLM for demonstration purposes")
            self.llm = None
        self.graph = self._build_graph()
    
    def _create_session_folder(self) -> tuple[str, str]:
        """Create a session folder with format: date_HHMM_UUID(4char)"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M")
        uuid_4char = str(uuid.uuid4())[:4]
        
        session_id = f"{date_str}_{time_str}_{uuid_4char}"
        session_folder = os.path.join("sessions", session_id)
        
        # Create sessions directory if it doesn't exist
        os.makedirs("sessions", exist_ok=True)
        os.makedirs(session_folder, exist_ok=True)
        
        return session_id, session_folder
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("parse_xml", self._parse_xml_node)
        workflow.add_node("analyze_workflow", self._analyze_workflow_node)
        workflow.add_node("map_dependencies", self._map_dependencies_node)
        workflow.add_node("summarize", self._summarize_node)
        
        # Define edges
        workflow.set_entry_point("parse_xml")
        workflow.add_edge("parse_xml", "analyze_workflow")
        workflow.add_edge("analyze_workflow", "map_dependencies")
        workflow.add_edge("map_dependencies", "summarize")
        workflow.add_edge("summarize", END)
        
        return workflow.compile()
    
    def _parse_xml_node(self, state: WorkflowState) -> WorkflowState:
        """Parse PowerCenter XML and extract basic structure"""
        try:
            root = ET.fromstring(state["xml_content"])
            
            parsed_data = {
                "repository_name": root.get("NAME", "Unknown"),
                "version": root.get("VERSION", "Unknown"),
                "sources": [],
                "targets": [],
                "transformations": [],
                "mappings": [],
                "sessions": [],
                "workflows": []
            }
            
            # Extract sources
            for source in root.findall(".//SOURCE"):
                parsed_data["sources"].append({
                    "name": source.get("NAME"),
                    "type": source.get("DATABASETYPE"),
                    "connection": source.get("OWNERNAME"),
                    "columns": [col.get("NAME") for col in source.findall(".//SOURCEFIELD")]
                })
            
            # Extract targets
            for target in root.findall(".//TARGET"):
                parsed_data["targets"].append({
                    "name": target.get("NAME"),
                    "type": target.get("DATABASETYPE"),
                    "connection": target.get("OWNERNAME"),
                    "columns": [col.get("NAME") for col in target.findall(".//TARGETFIELD")]
                })
            
            # Extract transformations
            for trans in root.findall(".//TRANSFORMATION"):
                parsed_data["transformations"].append({
                    "name": trans.get("NAME"),
                    "type": trans.get("TYPE"),
                    "description": trans.get("DESCRIPTION", ""),
                    "input_ports": [port.get("NAME") for port in trans.findall(".//TRANSFORMFIELD[@PORTTYPE='INPUT']")],
                    "output_ports": [port.get("NAME") for port in trans.findall(".//TRANSFORMFIELD[@PORTTYPE='OUTPUT']")]
                })
            
            # Extract mappings
            for mapping in root.findall(".//MAPPING"):
                parsed_data["mappings"].append({
                    "name": mapping.get("NAME"),
                    "description": mapping.get("DESCRIPTION", ""),
                    "is_valid": mapping.get("ISVALID", "YES") == "YES"
                })
            
            state["parsed_data"] = parsed_data
            
        except Exception as e:
            state["errors"].append(f"XML parsing error: {str(e)}")
            
        return state
    
    def _analyze_workflow_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze transformations and data flow logic"""
        
        prompt = f"""
        Analyze the following PowerCenter workflow data and extract key transformation logic:
        
        Sources: {json.dumps(state["parsed_data"]["sources"], indent=2)}
        Targets: {json.dumps(state["parsed_data"]["targets"], indent=2)}
        Transformations: {json.dumps(state["parsed_data"]["transformations"], indent=2)}
        
        For each transformation, identify:
        1. Business purpose/logic
        2. Data transformation type (filter, lookup, aggregation, etc.)
        3. Input-output relationships
        4. Potential data quality rules
        
        Return as JSON array of transformation analyses.
        """
        
        try:
            if self.llm:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                llm_content = response.content
            else:
                # Mock response when LLM is not available
                llm_content = f"Mock analysis for {len(state['parsed_data']['transformations'])} transformations"
            
            # Parse LLM response and structure transformation analysis
            transformations = []
            for trans in state["parsed_data"]["transformations"]:
                analysis = {
                    "name": trans["name"],
                    "type": trans["type"],
                    "business_purpose": f"Data transformation of type {trans['type']}",
                    "input_fields": trans["input_ports"],
                    "output_fields": trans["output_ports"],
                    "transformation_logic": llm_content
                }
                transformations.append(analysis)
            
            state["transformations"] = transformations
            
        except Exception as e:
            state["errors"].append(f"Workflow analysis error: {str(e)}")
            
        return state
    
    def _map_dependencies_node(self, state: WorkflowState) -> WorkflowState:
        """Map dependencies between sources, transformations, and targets"""
        
        dependencies = {}
        
        # Simple dependency mapping based on parsed data
        for source in state["parsed_data"]["sources"]:
            dependencies[source["name"]] = []
        
        for trans in state["transformations"]:
            dependencies[trans["name"]] = trans["input_fields"]
        
        for target in state["parsed_data"]["targets"]:
            # Assume targets depend on transformations (simplified)
            dependencies[target["name"]] = [t["name"] for t in state["transformations"]]
        
        state["dependencies"] = dependencies
        return state
    
    def _summarize_node(self, state: WorkflowState) -> WorkflowState:
        """Generate human-readable workflow summary and save as markdown"""
        
        prompt = f"""
        Create a comprehensive workflow summary based on this PowerCenter analysis:
        
        Repository: {state["parsed_data"]["repository_name"]}
        Sources: {len(state["parsed_data"]["sources"])} tables
        Targets: {len(state["parsed_data"]["targets"])} tables  
        Transformations: {len(state["transformations"])} components
        
        Transformations Details:
        {json.dumps(state["transformations"], indent=2)}
        
        Dependencies:
        {json.dumps(state["dependencies"], indent=2)}
        
        Provide:
        1. High-level workflow purpose
        2. Data flow summary (source → transformations → target)
        3. Key business rules identified
        4. Potential optimization opportunities
        """
        
        try:
            if self.llm:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                state["workflow_summary"] = response.content
            else:
                # Mock summary when LLM is not available
                state["workflow_summary"] = f"Mock workflow summary for {state['parsed_data']['repository_name']} with {len(state['transformations'])} transformations"
            
            # Generate markdown content
            markdown_content = self._generate_markdown_report(state)
            
            # Save markdown file to session folder
            markdown_file_path = os.path.join(state["session_folder"], "workflow_summary.md")
            with open(markdown_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Markdown report saved to: {markdown_file_path}")
            
        except Exception as e:
            state["errors"].append(f"Summarization error: {str(e)}")
            state["workflow_summary"] = "Summary generation failed"
            
        return state
    
    def _generate_markdown_report(self, state: WorkflowState) -> str:
        """Generate a well-formatted markdown report"""
        
        # Get current timestamp for the report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown = f"""# PowerCenter Workflow Analysis Report

**Session ID:** {state["session_id"]}  
**Generated:** {timestamp}  
**Repository:** {state["parsed_data"].get("repository_name", "Unknown")}

---

## Executive Summary

{state["workflow_summary"]}

---

## Repository Information

- **Repository Name:** {state["parsed_data"].get("repository_name", "Unknown")}
- **Version:** {state["parsed_data"].get("version", "Unknown")}
- **Total Sources:** {len(state["parsed_data"].get("sources", []))}
- **Total Targets:** {len(state["parsed_data"].get("targets", []))}
- **Total Transformations:** {len(state["transformations"])}
- **Total Mappings:** {len(state["parsed_data"].get("mappings", []))}

---

## Data Sources

"""
        
        # Add sources section
        for i, source in enumerate(state["parsed_data"].get("sources", []), 1):
            markdown += f"""### {i}. {source.get("name", "Unknown Source")}

- **Type:** {source.get("type", "Unknown")}
- **Connection:** {source.get("connection", "Unknown")}
- **Columns:** {', '.join(source.get("columns", []))}

"""
        
        # Add targets section
        markdown += "## Data Targets\n\n"
        for i, target in enumerate(state["parsed_data"].get("targets", []), 1):
            markdown += f"""### {i}. {target.get("name", "Unknown Target")}

- **Type:** {target.get("type", "Unknown")}
- **Connection:** {target.get("connection", "Unknown")}
- **Columns:** {', '.join(target.get("columns", []))}

"""
        
        # Add transformations section
        markdown += "## Transformations\n\n"
        for i, trans in enumerate(state["transformations"], 1):
            markdown += f"""### {i}. {trans.get("name", "Unknown Transformation")}

- **Type:** {trans.get("type", "Unknown")}
- **Business Purpose:** {trans.get("business_purpose", "Not specified")}
- **Input Fields:** {', '.join(trans.get("input_fields", []))}
- **Output Fields:** {', '.join(trans.get("output_fields", []))}
- **Transformation Logic:** {trans.get("transformation_logic", "Not available")}

"""
        
        # Add dependencies section
        markdown += "## Data Dependencies\n\n"
        for component, deps in state["dependencies"].items():
            if deps:
                markdown += f"- **{component}** depends on: {', '.join(deps)}\n"
            else:
                markdown += f"- **{component}** has no dependencies\n"
        
        # Add errors section if any
        if state["errors"]:
            markdown += "\n## Errors and Warnings\n\n"
            for error in state["errors"]:
                markdown += f"- ⚠️ {error}\n"
        
        # Add footer
        markdown += f"""
---

*Report generated by PowerCenter Workflow Extractor on {timestamp}*
"""
        
        return markdown
    
    def extract_workflow(self, xml_file_path: str) -> Dict[str, Any]:
        """Main method to extract workflow understanding"""
        
        # Create session folder
        session_id, session_folder = self._create_session_folder()
        print(f"Created session folder: {session_folder}")
        
        # Read XML file
        with open(xml_file_path, 'r', encoding='utf-8') as file:
            xml_content = file.read()
        
        # Initialize state
        initial_state = WorkflowState(
            xml_content=xml_content,
            parsed_data={},
            transformations=[],
            dependencies={},
            workflow_summary="",
            errors=[],
            session_id=session_id,
            session_folder=session_folder
        )
        
        # Run the workflow
        final_state = self.graph.invoke(initial_state)
        
        return {
            "session_id": final_state["session_id"],
            "session_folder": final_state["session_folder"],
            "repository_info": final_state["parsed_data"],
            "transformations": final_state["transformations"],
            "dependencies": final_state["dependencies"],
            "summary": final_state["workflow_summary"],
            "errors": final_state["errors"]
        }


# FastAPI web server
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
import shutil
from pathlib import Path

# Create FastAPI app
app = FastAPI(title="PowerCenter XML Analyzer", version="1.0.0")

# Add CORS middleware
# Configure allowed origins based on environment
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",  # Vite default dev port
    "https://etl-cognition-frontend.onrender.com",  # Production frontend URL
]

# In development, allow all origins
if os.environ.get("ENVIRONMENT") == "development":
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount sessions folder as static files
app.mount("/sessions", StaticFiles(directory="sessions"), name="sessions")

@app.post("/api/analyze-xml")
async def analyze_xml_file(file: UploadFile = File(...)):
    """Process uploaded PowerCenter XML file"""
    try:
        # Validate file type
        if not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail="Only XML files are allowed")
        
        # Read file content
        content = await file.read()
        xml_content = content.decode('utf-8')
        
        # Create extractor and process
        extractor = PowerCenterWorkflowExtractor()
        
        # Save XML content to temporary file for processing
        temp_xml_file = f"temp_{file.filename}"
        with open(temp_xml_file, "w", encoding='utf-8') as f:
            f.write(xml_content)
        
        try:
            result = extractor.extract_workflow(temp_xml_file)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_xml_file):
                os.remove(temp_xml_file)
        
        # Try to create graph visualization
        try:
            graph_image = extractor.graph.get_graph().draw_mermaid_png()
            graph_file_path = os.path.join(result['session_folder'], "workflow_diagram.png")
            with open(graph_file_path, "wb") as f:
                f.write(graph_image)
        except Exception as e:
            print(f"Warning: Could not create graph visualization: {e}")
        
        return JSONResponse({
            "session_id": result['session_id'],
            "session_folder": result['session_folder'],
            "summary": result['summary'],
            "repository_info": result['repository_info'],
            "transformations_count": len(result['transformations']),
            "errors": result['errors'],
            "success": True
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing XML: {str(e)}")

@app.post("/api/analyze-xml-content")
async def analyze_xml_content(content: dict):
    """Process XML content from text input"""
    try:
        xml_content = content.get("xml_content", "")
        if not xml_content.strip():
            raise HTTPException(status_code=400, detail="XML content is required")
        
        # Create temporary XML file
        temp_xml_file = "temp_content.xml"
        with open(temp_xml_file, "w", encoding='utf-8') as f:
            f.write(xml_content)
        
        # Create extractor and process
        extractor = PowerCenterWorkflowExtractor()
        
        try:
            result = extractor.extract_workflow(temp_xml_file)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_xml_file):
                os.remove(temp_xml_file)
        
        # Try to create graph visualization
        try:
            graph_image = extractor.graph.get_graph().draw_mermaid_png()
            graph_file_path = os.path.join(result['session_folder'], "workflow_diagram.png")
            with open(graph_file_path, "wb") as f:
                f.write(graph_image)
        except Exception as e:
            print(f"Warning: Could not create graph visualization: {e}")
        
        return JSONResponse({
            "session_id": result['session_id'],
            "session_folder": result['session_folder'],
            "summary": result['summary'],
            "repository_info": result['repository_info'],
            "transformations_count": len(result['transformations']),
            "errors": result['errors'],
            "success": True
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing XML: {str(e)}")

@app.get("/api/sessions")
async def list_sessions():
    """Get list of all analysis sessions"""
    try:
        sessions_dir = Path("sessions")
        if not sessions_dir.exists():
            return JSONResponse({"sessions": []})
        
        sessions = []
        for session_folder in sessions_dir.iterdir():
            if session_folder.is_dir():
                summary_file = session_folder / "workflow_summary.md"
                diagram_file = session_folder / "workflow_diagram.png"
                
                # Extract timestamp from session ID
                session_id = session_folder.name
                try:
                    # Parse session ID format: YYYYMMDD_HHMM_UUID
                    date_part, time_part, uuid_part = session_id.split('_')
                    year, month, day = date_part[:4], date_part[4:6], date_part[6:8]
                    hour, minute = time_part[:2], time_part[2:4]
                    
                    formatted_date = f"{year}-{month}-{day} {hour}:{minute}"
                except:
                    formatted_date = session_id
                
                sessions.append({
                    "session_id": session_id,
                    "created_at": formatted_date,
                    "has_summary": summary_file.exists(),
                    "has_diagram": diagram_file.exists()
                })
        
        # Sort by session_id (which includes timestamp)
        sessions.sort(key=lambda x: x['session_id'], reverse=True)
        
        return JSONResponse({"sessions": sessions})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details and content"""
    try:
        session_folder = Path("sessions") / session_id
        if not session_folder.exists():
            raise HTTPException(status_code=404, detail="Session not found")
        
        summary_file = session_folder / "workflow_summary.md"
        diagram_file = session_folder / "workflow_diagram.png"
        
        summary_content = ""
        if summary_file.exists():
            with open(summary_file, "r", encoding='utf-8') as f:
                summary_content = f.read()
        
        return JSONResponse({
            "session_id": session_id,
            "summary": summary_content,
            "has_diagram": diagram_file.exists(),
            "diagram_url": f"/sessions/{session_id}/workflow_diagram.png" if diagram_file.exists() else None
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

@app.get("/api/sessions/{session_id}/diagram")
async def get_session_diagram(session_id: str):
    """Get session diagram file"""
    try:
        diagram_file = Path("sessions") / session_id / "workflow_diagram.png"
        if not diagram_file.exists():
            raise HTTPException(status_code=404, detail="Diagram not found")
        
        return FileResponse(diagram_file, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting diagram: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PowerCenter XML Analyzer"}

# Example usage / CLI mode
if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Create sessions directory if it doesn't exist
    os.makedirs("sessions", exist_ok=True)
    
    # Check if running in CLI mode (with arguments) or server mode
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # CLI mode - generate sample and process
        print("=== PowerCenter XML Analyzer CLI Mode ===")
        
        # Generate synthetic XML file
        synthetic_xml = generate_synthetic_powercenter_xml()
        
        # Save to file
        with open("sample_powercenter.xml", "w", encoding="utf-8") as f:
            f.write(synthetic_xml)
        
        # Initialize extractor
        extractor = PowerCenterWorkflowExtractor()
        
        # Extract workflow understanding
        result = extractor.extract_workflow("sample_powercenter.xml")
        
        # Print results
        print("=== WORKFLOW EXTRACTION RESULTS ===")
        print(f"Session ID: {result['session_id']}")
        print(f"Session Folder: {result['session_folder']}")
        print(f"Repository: {result['repository_info']['repository_name']}")
        print(f"Sources: {len(result['repository_info']['sources'])}")
        print(f"Targets: {len(result['repository_info']['targets'])}")
        print(f"Transformations: {len(result['transformations'])}")
        print("\n=== WORKFLOW SUMMARY ===")
        print(result['summary'])
        print("\n=== ERRORS ===")
        for error in result['errors']:
            print(f"- {error}")
        
        # Create and save graph visualization in session folder
        print("\n=== CREATING GRAPH VISUALIZATION ===")
        try:
            graph_image = extractor.graph.get_graph().draw_mermaid_png()
            graph_file_path = os.path.join(result['session_folder'], "workflow_diagram.png")
            with open(graph_file_path, "wb") as f:
                f.write(graph_image)
            print(f"Graph visualization saved as '{graph_file_path}'")
        except Exception as e:
            print(f"Error creating graph visualization: {str(e)}")
        
        print(f"\n=== SESSION COMPLETE ===")
        print(f"All outputs saved to: {result['session_folder']}")
    else:
        # Server mode
        print("=== PowerCenter XML Analyzer API ===")
        print("Starting FastAPI server...")
        print("API Documentation: http://localhost:8000/docs")
        print("Health Check: http://localhost:8000/health")
        print("Use --cli flag to run in CLI mode")
        
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # Disable reload in production
            log_level="info"
        )