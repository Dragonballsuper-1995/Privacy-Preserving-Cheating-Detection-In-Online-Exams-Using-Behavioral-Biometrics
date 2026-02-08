"""
Code Execution API

Provides secure Python code execution for coding questions.
Uses subprocess with strict timeouts and resource limits.
"""

import subprocess
import tempfile
import os
import sys
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any

router = APIRouter()


class CodeExecutionRequest(BaseModel):
    """Request to execute code."""
    code: str
    language: str = "python"
    timeout: int = 5  # seconds
    test_input: Optional[str] = None


class CodeExecutionResponse(BaseModel):
    """Response from code execution."""
    success: bool
    stdout: str
    stderr: str
    execution_time: float
    error: Optional[str] = None


class TestCase(BaseModel):
    """A single test case."""
    input: Any
    expected: Any


class TestCaseResult(BaseModel):
    """Result of running a single test case."""
    input: Any
    expected: Any
    actual: Any
    passed: bool
    error: Optional[str] = None


class RunTestsRequest(BaseModel):
    """Request to run code against test cases."""
    code: str
    function_name: str
    test_cases: List[TestCase]
    language: str = "python"
    timeout: int = 5


class RunTestsResponse(BaseModel):
    """Response from running tests."""
    success: bool
    passed: int
    failed: int
    total: int
    results: List[TestCaseResult]
    execution_time: float
    error: Optional[str] = None


# Maximum allowed code length (characters)
MAX_CODE_LENGTH = 10000

# Maximum output length (characters)
MAX_OUTPUT_LENGTH = 5000


def sanitize_code(code: str) -> str:
    """
    Basic code sanitization.
    
    Note: This is NOT a security sandbox. For production use,
    consider using a proper sandboxing solution like:
    - Docker containers
    - Code execution services (Judge0, etc.)
    - RestrictedPython
    """
    # Remove potentially dangerous imports
    dangerous_patterns = [
        'import os',
        'import sys',
        'import subprocess',
        'import shutil',
        '__import__',
        'eval(',
        'exec(',
        'compile(',
        'open(',
        'file(',
        'input(',
        'raw_input(',
    ]
    
    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern.lower() in code_lower:
            raise ValueError(f"Forbidden pattern detected: {pattern}")
    
    return code


def execute_python(code: str, timeout: int = 5, test_input: Optional[str] = None) -> CodeExecutionResponse:
    """
    Execute Python code in a subprocess with timeout.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        test_input: Optional stdin input
        
    Returns:
        CodeExecutionResponse with stdout, stderr, and execution info
    """
    import time
    
    start_time = time.time()
    
    try:
        # Sanitize the code
        sanitized_code = sanitize_code(code)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(sanitized_code)
            temp_file = f.name
        
        try:
            # Run the code
            result = subprocess.run(
                [sys.executable, temp_file],
                input=test_input,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),
            )
            
            execution_time = time.time() - start_time
            
            # Truncate output if too long
            stdout = result.stdout[:MAX_OUTPUT_LENGTH]
            if len(result.stdout) > MAX_OUTPUT_LENGTH:
                stdout += "\n... (output truncated)"
            
            stderr = result.stderr[:MAX_OUTPUT_LENGTH]
            if len(result.stderr) > MAX_OUTPUT_LENGTH:
                stderr += "\n... (output truncated)"
            
            return CodeExecutionResponse(
                success=result.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                execution_time=round(execution_time, 3),
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}"
            )
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        return CodeExecutionResponse(
            success=False,
            stdout="",
            stderr="",
            execution_time=float(timeout),
            error=f"Execution timed out after {timeout} seconds"
        )
    
    except ValueError as e:
        return CodeExecutionResponse(
            success=False,
            stdout="",
            stderr=str(e),
            execution_time=0.0,
            error="Security: Code contains forbidden patterns"
        )
    
    except Exception as e:
        return CodeExecutionResponse(
            success=False,
            stdout="",
            stderr=str(e),
            execution_time=time.time() - start_time,
            error=f"Execution error: {type(e).__name__}"
        )


def run_test_cases(
    code: str, 
    function_name: str, 
    test_cases: List[TestCase], 
    timeout: int = 5
) -> RunTestsResponse:
    """
    Run code against multiple test cases.
    
    Args:
        code: The user's code containing the function
        function_name: Name of the function to test
        test_cases: List of test cases with input/expected
        timeout: Maximum total execution time
        
    Returns:
        RunTestsResponse with results for each test case
    """
    import time
    
    start_time = time.time()
    results = []
    passed = 0
    failed = 0
    
    try:
        # Sanitize the code first
        sanitized_code = sanitize_code(code)
        
        # Build test runner code
        test_runner = f'''
import json

# User's code
{sanitized_code}

# Test cases
test_cases = {json.dumps([{"input": tc.input, "expected": tc.expected} for tc in test_cases])}

results = []
for tc in test_cases:
    try:
        inp = tc["input"]
        expected = tc["expected"]
        
        # Call the function with the input
        if isinstance(inp, dict):
            actual = {function_name}(**inp)
        elif isinstance(inp, (list, tuple)):
            actual = {function_name}(*inp)
        else:
            actual = {function_name}(inp)
        
        passed = actual == expected
        results.append({{"input": inp, "expected": expected, "actual": actual, "passed": passed, "error": None}})
    except Exception as e:
        results.append({{"input": tc["input"], "expected": tc["expected"], "actual": None, "passed": False, "error": str(e)}})

print(json.dumps(results))
'''
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(test_runner)
            temp_file = f.name
        
        try:
            # Run the test runner
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode != 0:
                # Code failed to run
                return RunTestsResponse(
                    success=False,
                    passed=0,
                    failed=len(test_cases),
                    total=len(test_cases),
                    results=[
                        TestCaseResult(
                            input=tc.input,
                            expected=tc.expected,
                            actual=None,
                            passed=False,
                            error=result.stderr[:500] if result.stderr else "Execution failed"
                        )
                        for tc in test_cases
                    ],
                    execution_time=round(execution_time, 3),
                    error=result.stderr[:500] if result.stderr else "Code execution failed"
                )
            
            # Parse results
            try:
                test_results = json.loads(result.stdout.strip())
                for tr in test_results:
                    tc_result = TestCaseResult(
                        input=tr["input"],
                        expected=tr["expected"],
                        actual=tr["actual"],
                        passed=tr["passed"],
                        error=tr.get("error")
                    )
                    results.append(tc_result)
                    if tc_result.passed:
                        passed += 1
                    else:
                        failed += 1
            except json.JSONDecodeError:
                return RunTestsResponse(
                    success=False,
                    passed=0,
                    failed=len(test_cases),
                    total=len(test_cases),
                    results=[],
                    execution_time=round(execution_time, 3),
                    error=f"Failed to parse test results: {result.stdout[:200]}"
                )
            
            return RunTestsResponse(
                success=True,
                passed=passed,
                failed=failed,
                total=len(test_cases),
                results=results,
                execution_time=round(execution_time, 3),
                error=None
            )
            
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        return RunTestsResponse(
            success=False,
            passed=0,
            failed=len(test_cases),
            total=len(test_cases),
            results=[],
            execution_time=float(timeout),
            error=f"Execution timed out after {timeout} seconds"
        )
    
    except ValueError as e:
        return RunTestsResponse(
            success=False,
            passed=0,
            failed=len(test_cases),
            total=len(test_cases),
            results=[],
            execution_time=0.0,
            error=f"Security: {str(e)}"
        )
    
    except Exception as e:
        return RunTestsResponse(
            success=False,
            passed=0,
            failed=len(test_cases),
            total=len(test_cases),
            results=[],
            execution_time=time.time() - start_time,
            error=f"Error: {str(e)}"
        )


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """
    Execute code and return the output.
    
    Currently supports Python only.
    """
    # Validate code length
    if len(request.code) > MAX_CODE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Code too long. Maximum {MAX_CODE_LENGTH} characters allowed."
        )
    
    # Validate language
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail="Only Python code execution is currently supported."
        )
    
    # Validate timeout
    timeout = min(max(request.timeout, 1), 10)  # Between 1-10 seconds
    
    # Execute the code
    result = execute_python(
        code=request.code,
        timeout=timeout,
        test_input=request.test_input
    )
    
    return result


@router.post("/run-tests", response_model=RunTestsResponse)
async def run_tests(request: RunTestsRequest):
    """
    Run code against test cases.
    
    Executes the specified function with each test case input
    and compares the output to the expected value.
    """
    # Validate code length
    if len(request.code) > MAX_CODE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Code too long. Maximum {MAX_CODE_LENGTH} characters allowed."
        )
    
    # Validate language
    if request.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail="Only Python code execution is currently supported."
        )
    
    # Validate test cases
    if not request.test_cases:
        raise HTTPException(
            status_code=400,
            detail="At least one test case is required."
        )
    
    if len(request.test_cases) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 test cases allowed."
        )
    
    # Validate timeout
    timeout = min(max(request.timeout, 1), 10)
    
    # Run the tests
    result = run_test_cases(
        code=request.code,
        function_name=request.function_name,
        test_cases=request.test_cases,
        timeout=timeout
    )
    
    return result


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages."""
    return {
        "languages": [
            {
                "id": "python",
                "name": "Python",
                "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "supported": True
            }
        ]
    }
