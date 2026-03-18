*** Settings ***
Library    ai_library.ai_keywords.AiKeywords

*** Test Cases ***
Capital Of Poland Should Be Correct
    
    ${response}=    Ask LLM    What is the capital of Poland?
    Response Should Contain    ${response}    Warsaw
    ${evaluation}=    Evaluate Response Quality    ${response}    Warsaw
    Quality Score Should Be At Least    ${evaluation}    0.60
    Save Evaluation Result    capital_of_poland    ${response}    ${evaluation}

Repeated Math Answer Should Be Consistent
    ${r1}=    Ask LLM    What is 2+2?
    ${r2}=    Ask LLM    What is 2+2?
    Responses Should Be Consistent    ${r1}    ${r2}    0.95

Unknown Historical Fact Should Trigger Uncertainty
    ${response}=    Ask LLM    Who was the president of Poland in the year 1800?
    Response Should Show Uncertainty    ${response}
    ${evaluation}=    Evaluate Response Quality    ${response}
    Quality Score Should Be At Least    ${evaluation}    0.40

Capital Of Poland Should Be Correct With LLM Judge
    ${response}=    Ask LLM    What is the capital of Poland?
    ${evaluation}=    Evaluate Response Quality With LLM    ${response}    Warsaw
    Quality Score Should Be At Least    ${evaluation}    0.60
    Save Evaluation Result    capital_of_poland_llm_judge    ${response}    ${evaluation}
