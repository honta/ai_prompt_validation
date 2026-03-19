*** Settings ***
Library    DataDriver    file=datasets/functional_cases.csv    encoding=utf-8    dialect=excel
Library    ai_library.ai_keywords.AiKeywords
Test Template    Run Functional Dataset Case

*** Test Cases ***
Functional Dataset Case
    [Tags]    functional    dataset
    ${case_type}    ${prompt}    ${prompt_second}    ${expected}    ${min_score}    ${consistency_threshold}    ${result_id}

*** Keywords ***
Run Functional Dataset Case
    [Arguments]    ${case_type}    ${prompt}    ${prompt_second}    ${expected}    ${min_score}    ${consistency_threshold}    ${result_id}
    IF    '${case_type}' == 'contains_expected'
        ${response}=    Ask LLM    ${prompt}
        Response Should Contain    ${response}    ${expected}
        ${evaluation}=    Evaluate Response Quality    ${response}    ${expected}
        Quality Score Should Be At Least    ${evaluation}    ${min_score}
        Save Result If Configured    ${result_id}    ${response}    ${evaluation}
    ELSE IF    '${case_type}' == 'uncertainty'
        ${response}=    Ask LLM    ${prompt}
        Response Should Show Uncertainty    ${response}
        ${evaluation}=    Evaluate Response Quality    ${response}
        Quality Score Should Be At Least    ${evaluation}    ${min_score}
        Save Result If Configured    ${result_id}    ${response}    ${evaluation}
    ELSE IF    '${case_type}' == 'consistency'
        ${second_prompt}=    Set Variable    ${prompt}
        IF    '${prompt_second}' != ''
            ${second_prompt}=    Set Variable    ${prompt_second}
        END
        ${r1}=    Ask LLM    ${prompt}
        ${r2}=    Ask LLM    ${second_prompt}
        Responses Should Be Consistent    ${r1}    ${r2}    ${consistency_threshold}
    ELSE IF    '${case_type}' == 'llm_judge'
        ${response}=    Ask LLM    ${prompt}
        ${evaluation}=    Evaluate Response Quality with LLM    ${response}    ${expected}
        Quality Score Should Be At Least    ${evaluation}    ${min_score}
        Save Result If Configured    ${result_id}    ${response}    ${evaluation}
    ELSE
        Fail    Unsupported functional case type: ${case_type}
    END

Save Result If Configured
    [Arguments]    ${result_id}    ${response}    ${evaluation}
    IF    '${result_id}' != ''
        Save Evaluation Result    ${result_id}    ${response}    ${evaluation}
    END
