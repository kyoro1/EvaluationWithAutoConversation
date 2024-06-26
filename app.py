import streamlit as st
from src import common


## Initialization of the tools
tools = common.AOAI_TOOLS(config_file='./config.yml')

## Sidebar
with st.sidebar:
    st.title('Auto-Conversation with AOAI API')

    ## Select prompt for caller and operator
    flag_prompt_caller = st.radio(
        "Prompt for caller",
        tools.caller_prompt_list
    )

    flag_prompt_operator = st.radio(
        "Prompt for operator",
        tools.operator_prompt_list
    )
    
    flag_prompt_evaluator = st.radio(
        "Prompt for evaluator",
        tools.evaluator_prompt_list
    )

    ## Set the number of interactions
    conversation_number = st.select_slider("how many interactions?", options=range(1, 10), value=2)

    with st.form("my_form"):
        st.write("Ready to start?")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Start conversation")
        if submitted:
            st.write(f'Start auto-conversation with {conversation_number} interaction(s).')

if submitted:
    ## Set configuration for AOAI client
    tools.setClient()

    ## Define initial prompt for caller
    prompt_caller = tools.promptBank['caller_prompt']['PROMPTS'][flag_prompt_caller]
    ## Define initial prompt for operator
    prompt_operator = tools.promptBank['operator_prompt']['PROMPTS'][flag_prompt_operator]

    ## Generate conversation
    Conversation = tools.generate_conversation(prompt_caller=prompt_caller,
                                                prompt_operator=prompt_operator,
                                                conversation_number=conversation_number,
                                                ui_flg=True)
else:
    st.stop()


with st.expander("Evaluation results will be here"):
    evaluate_result = tools.evaluate_conversation(prompt_evaluator = tools.promptBank['evaluate_prompt']['PROMPTS'][flag_prompt_evaluator],
                                                    conversation=Conversation)

    try:
        # convert json to dataframe
        df = tools.convert_to_df(evaluate_result)
        st.dataframe(df)
    except:
        st.write(evaluate_result)