@echo off
echo Launching RFP Automation Tool...

:: Activate your environment
call conda activate rfp_automation_tool

:: Change to project directory
cd "C:\Users\Daniel Quinn\Desktop\AI_Consultancy_Project\rfp_assistant\rfp_automation_tool"

:: Launch Streamlit
start cmd /k "streamlit run ui_streamlit.py"

:: Launch n8n in a second terminal (optional)
start cmd /k "npx n8n"

:: Open Streamlit in browser
start http://localhost:8501
