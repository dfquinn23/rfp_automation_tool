@echo on
cd /d "C:\Users\Daniel Quinn\Desktop\AI_Consultancy_Project\rfp_assistant\rfp_automation_tool"
echo Running pipeline for: %~1
"C:\Users\Daniel Quinn\anaconda3\envs\dev\python.exe" run_pipeline.py --rfp "%~1"
if %errorlevel% neq 0 (
    echo ❌ Python script failed with error code %errorlevel%
) else (
    echo ✅ Script completed successfully.
)
pause

