*** Settings ***
Library    DataDriver    file=datasets/prompt_injection_cases.csv    encoding=utf-8    dialect=excel
Library    ai_library.ai_keywords.AiKeywords
Test Template    Run Prompt Injection Dataset Case

*** Test Cases ***
Prompt Injection Dataset
    [Tags]    prompt-injection    dataset
    ${prompt}    ${mode}    ${max_iterations}    ${min_score}    ${result_id}

*** Keywords ***
Run Prompt Injection Dataset Case
    [Arguments]    ${prompt}    ${mode}    ${max_iterations}    ${min_score}    ${result_id}
    IF    '${mode}' == 'iterative'
        ${response}=    Ask LLM With Prompt Injection    ${prompt}    ${max_iterations}
    ELSE IF    '${mode}' == 'single'
        ${response}=    Ask LLM    ${prompt}
    ELSE
        Fail    Unsupported prompt injection mode: ${mode}
    END

    Response Should Resist Prompt Injection    ${response}
    ${evaluation}=    Evaluate Response Quality    ${response}
    Quality Score Should Be At Least    ${evaluation}    ${min_score}

    IF    '${result_id}' != ''
        Save Evaluation Result    ${result_id}    ${response}    ${evaluation}
    END
