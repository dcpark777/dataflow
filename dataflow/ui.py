"""
Streamlit web UI for DataFlow dataset management and transformations
"""

import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, List, Any, Optional
import os

# Configure page
st.set_page_config(
    page_title="DataFlow - Natural Language Data Transformations",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import configuration
try:
    from .config import get_config
except ImportError:
    # Fallback for when running directly with streamlit
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from dataflow.config import get_config

# Get configuration
config = get_config()
API_BASE_URL = config.api_url

def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Make API request to DataFlow backend"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return {}


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🔄 DataFlow")
    st.markdown("**Natural Language Data Transformations**")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📊 Datasets", "🔄 Transformations", "⚙️ Settings"]
    )
    
    # Health check
    health_status = make_api_request("GET", "/api/health")
    if health_status.get("status") == "healthy":
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.error("Cannot connect to DataFlow API. Please ensure the API server is running.")
        return
    
    # Route to appropriate page
    if page == "📊 Datasets":
        datasets_page()
    elif page == "🔄 Transformations":
        transformations_page()
    elif page == "⚙️ Settings":
        settings_page()


def datasets_page():
    """Datasets management page"""
    st.header("📊 Dataset Management")
    
    # Tabs for different dataset operations
    tab1, tab2, tab3, tab4 = st.tabs(["View Datasets", "Create Dataset", "Import/Export", "Data Validation"])
    
    with tab1:
        st.subheader("Existing Datasets")
        
        # Fetch datasets
        datasets_response = make_api_request("GET", "/api/datasets")
        datasets = datasets_response.get("datasets", [])
        
        if datasets:
            # Display datasets in a table
            df = pd.DataFrame(datasets)
            st.dataframe(df, use_container_width=True)
            
            # Dataset details
            if st.checkbox("Show Dataset Details"):
                selected_dataset = st.selectbox("Select Dataset", [d["name"] for d in datasets])
                
                if selected_dataset:
                    dataset_response = make_api_request("GET", f"/api/datasets/{selected_dataset}")
                    if dataset_response:
                        st.json(dataset_response)
                        
                        # Delete dataset option
                        if st.button("Delete Dataset", type="secondary"):
                            if st.session_state.get("confirm_delete", False):
                                make_api_request("DELETE", f"/api/datasets/{selected_dataset}")
                                st.success(f"Dataset '{selected_dataset}' deleted!")
                                st.rerun()
                            else:
                                st.session_state.confirm_delete = True
                                st.warning("Click again to confirm deletion")
        else:
            st.info("No datasets found. Create one using the 'Create Dataset' tab.")
    
    with tab2:
        st.subheader("Create New Dataset")
        
        with st.form("create_dataset_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                dataset_name = st.text_input("Dataset Name", placeholder="e.g., customers")
                dataset_description = st.text_area("Description", placeholder="Description of the dataset")
                source_type = st.selectbox("Source Type", ["manual", "file", "database", "api"])
            
            with col2:
                tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., sales, customers, contacts")
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            
            st.subheader("Fields Definition")
            
            # Dynamic fields
            if "fields" not in st.session_state:
                st.session_state.fields = [{"name": "", "type": "string", "nullable": True, "description": ""}]
            
            for i, field in enumerate(st.session_state.fields):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    field_name = st.text_input(f"Field Name {i+1}", value=field["name"], key=f"field_name_{i}")
                with col2:
                    field_type = st.selectbox(f"Type {i+1}", ["string", "integer", "double", "boolean", "date", "timestamp"], 
                                           index=["string", "integer", "double", "boolean", "date", "timestamp"].index(field["type"]),
                                           key=f"field_type_{i}")
                with col3:
                    field_nullable = st.checkbox(f"Nullable {i+1}", value=field["nullable"], key=f"field_nullable_{i}")
                with col4:
                    field_description = st.text_input(f"Description {i+1}", value=field["description"], key=f"field_desc_{i}")
                
                st.session_state.fields[i] = {
                    "name": field_name,
                    "type": field_type,
                    "nullable": field_nullable,
                    "description": field_description
                }
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Field"):
                    st.session_state.fields.append({"name": "", "type": "string", "nullable": True, "description": ""})
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Remove Last Field"):
                    if len(st.session_state.fields) > 1:
                        st.session_state.fields.pop()
                        st.rerun()
            
            # Submit form
            if st.form_submit_button("Create Dataset", type="primary"):
                if dataset_name and all(field["name"] for field in st.session_state.fields):
                    dataset_data = {
                        "name": dataset_name,
                        "description": dataset_description,
                        "fields": st.session_state.fields,
                        "source_type": source_type,
                        "tags": tags
                    }
                    
                    response = make_api_request("POST", "/api/datasets", dataset_data)
                    if response:
                        st.success(f"Dataset '{dataset_name}' created successfully!")
                        st.session_state.fields = [{"name": "", "type": "string", "nullable": True, "description": ""}]
                        st.rerun()
                else:
                    st.error("Please fill in all required fields.")
    
    with tab3:
        st.subheader("Import/Export Datasets")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Export Datasets**")
            export_format = st.selectbox("Export Format", ["json", "yaml"])
            
            if st.button("Export All Datasets"):
                response = make_api_request("POST", f"/api/export/datasets?format={export_format}")
                if response:
                    st.download_button(
                        label=f"Download {export_format.upper()}",
                        data=response["data"],
                        file_name=f"datasets.{export_format}",
                        mime="application/json" if export_format == "json" else "text/yaml"
                    )
        
        with col2:
            st.markdown("**Import Datasets**")
            import_format = st.selectbox("Import Format", ["json", "yaml"], key="import_format")
            
            uploaded_file = st.file_uploader("Choose file", type=[import_format])
            
            if uploaded_file and st.button("Import Datasets"):
                file_content = uploaded_file.read().decode("utf-8")
                response = make_api_request("POST", f"/api/import/datasets?format={import_format}", {"data": file_content})
                if response:
                    st.success(f"Imported {response['count']} datasets successfully!")
                    st.rerun()
    
    with tab4:
        st.subheader("Data Validation")
        
        # Get datasets for validation
        datasets_response = make_api_request("GET", "/api/datasets")
        datasets = datasets_response.get("datasets", [])
        
        if datasets:
            selected_dataset = st.selectbox("Select Dataset for Validation", [d["name"] for d in datasets])
            
            if selected_dataset:
                st.markdown("**Upload Sample Data**")
                
                # File upload for validation
                uploaded_file = st.file_uploader("Upload CSV/JSON file", type=["csv", "json"])
                
                if uploaded_file:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            data = pd.read_csv(uploaded_file)
                        else:
                            data = pd.read_json(uploaded_file)
                        
                        # Convert to list of dictionaries
                        data_list = data.to_dict('records')
                        
                        # Validate data
                        validation_data = {
                            "dataset_name": selected_dataset,
                            "data": data_list
                        }
                        
                        response = make_api_request("POST", f"/api/datasets/{selected_dataset}/validate", validation_data)
                        
                        if response:
                            if response["valid"]:
                                st.success("✅ Data validation passed!")
                                st.info(f"Validated {response['row_count']} rows")
                            else:
                                st.error("❌ Data validation failed!")
                                for error in response["errors"]:
                                    st.error(f"• {error}")
                        
                        # Show sample data
                        st.markdown("**Sample Data Preview**")
                        st.dataframe(data.head(10))
                        
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
        else:
            st.info("No datasets available for validation.")


def transformations_page():
    """Transformations management page"""
    st.header("🔄 Transformation Management")
    
    # Tabs for different transformation operations
    tab1, tab2, tab3 = st.tabs(["View Jobs", "Create Job", "Execute Job"])
    
    with tab1:
        st.subheader("Transformation Jobs")
        
        # Fetch jobs
        jobs_response = make_api_request("GET", "/api/transformations")
        jobs = jobs_response.get("jobs", [])
        
        if jobs:
            # Display jobs in a table
            jobs_df = pd.DataFrame([
                {
                    "Job ID": job["job_id"][:8] + "...",
                    "Name": job["name"],
                    "Status": job["status"],
                    "Steps": len(job["steps"]),
                    "Created": job["created_at"][:10]
                }
                for job in jobs
            ])
            st.dataframe(jobs_df, use_container_width=True)
            
            # Job details
            if st.checkbox("Show Job Details"):
                selected_job_id = st.selectbox("Select Job", [job["job_id"] for job in jobs])
                
                if selected_job_id:
                    job_response = make_api_request("GET", f"/api/transformations/{selected_job_id}")
                    if job_response:
                        st.json(job_response)
        else:
            st.info("No transformation jobs found. Create one using the 'Create Job' tab.")
    
    with tab2:
        st.subheader("Create Transformation Job")
        
        with st.form("create_job_form"):
            job_name = st.text_input("Job Name", placeholder="e.g., Customer Analysis")
            job_description = st.text_area("Description", placeholder="Description of the transformation job")
            
            st.subheader("Transformation Steps")
            
            # Get available datasets
            datasets_response = make_api_request("GET", "/api/datasets")
            datasets = datasets_response.get("datasets", [])
            dataset_names = [d["name"] for d in datasets]
            
            if not dataset_names:
                st.warning("No datasets available. Please create datasets first.")
            else:
                # Dynamic steps
                if "job_steps" not in st.session_state:
                    st.session_state.job_steps = [{"step_name": "", "query": "", "input_datasets": [], "output_dataset": ""}]
                
                for i, step in enumerate(st.session_state.job_steps):
                    st.markdown(f"**Step {i+1}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        step_name = st.text_input(f"Step Name {i+1}", value=step["step_name"], key=f"step_name_{i}")
                        step_query = st.text_area(f"Natural Language Query {i+1}", 
                                                value=step["query"], 
                                                placeholder="e.g., Filter customers with age greater than 30",
                                                key=f"step_query_{i}")
                    
                    with col2:
                        input_datasets = st.multiselect(f"Input Datasets {i+1}", 
                                                      dataset_names, 
                                                      default=step["input_datasets"],
                                                      key=f"input_datasets_{i}")
                        output_dataset = st.text_input(f"Output Dataset {i+1}", 
                                                    value=step["output_dataset"],
                                                    key=f"output_dataset_{i}")
                    
                    st.session_state.job_steps[i] = {
                        "step_name": step_name,
                        "query": step_query,
                        "input_datasets": input_datasets,
                        "output_dataset": output_dataset
                    }
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Add Step"):
                        st.session_state.job_steps.append({"step_name": "", "query": "", "input_datasets": [], "output_dataset": ""})
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("Remove Last Step"):
                        if len(st.session_state.job_steps) > 1:
                            st.session_state.job_steps.pop()
                            st.rerun()
                
                # Submit form
                if st.form_submit_button("Create Job", type="primary"):
                    if job_name and all(step["step_name"] and step["query"] for step in st.session_state.job_steps):
                        job_data = {
                            "job_name": job_name,
                            "job_description": job_description,
                            "steps": st.session_state.job_steps
                        }
                        
                        response = make_api_request("POST", "/api/transformations", job_data)
                        if response:
                            st.success(f"Transformation job '{job_name}' created successfully!")
                            st.session_state.job_steps = [{"step_name": "", "query": "", "input_datasets": [], "output_dataset": ""}]
                            st.rerun()
                    else:
                        st.error("Please fill in all required fields.")
    
    with tab3:
        st.subheader("Execute Transformation Job")
        
        # Get available jobs
        jobs_response = make_api_request("GET", "/api/transformations")
        jobs = jobs_response.get("jobs", [])
        
        if jobs:
            selected_job_id = st.selectbox("Select Job to Execute", [job["job_id"] for job in jobs])
            
            if selected_job_id:
                # Get job details
                job_response = make_api_request("GET", f"/api/transformations/{selected_job_id}")
                
                if job_response:
                    st.markdown("**Job Details**")
                    st.json(job_response)
                    
                    st.markdown("**Input Data**")
                    
                    # Get input datasets for the job
                    input_datasets = set()
                    for step in job_response["steps"]:
                        input_datasets.update(step["input_datasets"])
                    
                    input_data = {}
                    
                    for dataset_name in input_datasets:
                        st.markdown(f"**{dataset_name}**")
                        
                        # File upload for input data
                        uploaded_file = st.file_uploader(f"Upload data for {dataset_name}", 
                                                       type=["csv", "json"], 
                                                       key=f"upload_{dataset_name}")
                        
                        if uploaded_file:
                            try:
                                if uploaded_file.name.endswith('.csv'):
                                    data = pd.read_csv(uploaded_file)
                                else:
                                    data = pd.read_json(uploaded_file)
                                
                                input_data[dataset_name] = data.to_dict('records')
                                st.success(f"✅ Loaded {len(input_data[dataset_name])} rows for {dataset_name}")
                                
                            except Exception as e:
                                st.error(f"Error processing file for {dataset_name}: {str(e)}")
                    
                    # Execute job
                    if input_data and st.button("Execute Job", type="primary"):
                        with st.spinner("Executing transformation..."):
                            response = make_api_request("POST", f"/api/transformations/{selected_job_id}/execute", input_data)
                        
                        if response:
                            st.success("✅ Transformation executed successfully!")
                            
                            # Display results
                            st.markdown("**Results**")
                            for dataset_name, data in response["results"].items():
                                st.markdown(f"**{dataset_name}**")
                                df = pd.DataFrame(data)
                                st.dataframe(df, use_container_width=True)
        else:
            st.info("No transformation jobs available for execution.")


def settings_page():
    """Settings page"""
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    st.text_input("API Base URL", value=API_BASE_URL, disabled=True)
    
    st.subheader("System Information")
    
    # Get health status
    health_status = make_api_request("GET", "/api/health")
    
    if health_status:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Status", "✅ Healthy" if health_status.get("status") == "healthy" else "❌ Unhealthy")
        
        with col2:
            st.metric("Spark Available", "✅ Yes" if health_status.get("spark_available") else "❌ No")
        
        with col3:
            st.metric("Dataset Registry", "✅ Available" if health_status.get("dataset_registry_available") else "❌ Unavailable")
        
        st.markdown("**Detailed Status**")
        st.json(health_status)
    
    st.subheader("About DataFlow")
    st.markdown("""
    **DataFlow** is a natural language data transformation tool that allows you to:
    
    - Define datasets using JSON, YAML, or Python dataclass formats
    - Create transformations using natural language queries
    - Execute transformations using PySpark
    - Manage datasets and transformations through a web interface
    
    **Version:** 0.1.0
    """)


if __name__ == "__main__":
    main()
